import os
import astropy.io.fits as fits
import datetime as dt
import gzip
import re
import glob
from pprint import pprint as pp
import argparse
import requests
import json
import dateutil.parser as dateparser
import csv 

from update_config import *


def get_dirs_to_walk(data_dir, datetime_start, datetime_end):
    folders_in_root = os.listdir(data_dir)

    date_start = datetime_start.date()
    if datetime_start.hour >= 12:
        date_start = date_start + dt.timedelta(days=1)
    
    date_end = datetime_end.date()
    if datetime_end.hour >=12:
        date_end = date_end + dt.timedelta(days=1)

    p = re.compile(DATE_REGEX) 
    
    dirs_to_walk = []
    for _d in os.listdir(data_dir):
        if (p.match(_d) and \
            date_end >= dt.datetime.strptime(_d, '%Y-%m-%d').date() >= date_start
           ):
            dirs_to_walk.append(os.path.join(data_dir, _d))
    return dirs_to_walk

def get_files(_dir):
    
    files_in_folder = []
    for r, d, f in os.walk(_dir):
        for file in f:
            files_in_folder.append(os.path.join(r, file))
    
    files_to_open = []
    for _file in files_in_folder:
        if os.path.isfile(_file):
            if os.path.splitext(_file)[-1] in ALLOWED_EXT:
                files_to_open.append(_file)
    
    return files_to_open


def get_folder_data(files_to_open, names_dict):
    folder_data = []
    logger.debug(files_to_open)
    for f in files_to_open:
        try:
            f_in = gzip.open(f, 'rb')
        except OSError as e:
            logger.error(e)
            continue
            # with gzip.open(f, 'rb') as f_in:
        else:
            with f_in:        
                try:
                    hdr = dict(fits.getheader(f, ignore_missing_end=True))
                except OSError as e:
                    logger.warning(f'HDR problem in file: {f} - {e}')
                    continue

                obs_datetime = dt.datetime.strptime(
                    hdr['DATE-OBS'] + 'T' + hdr['TIME-OBS'],
                    '%Y-%m-%dT%H:%M:%S.%f').isoformat()
                
                object_name = hdr['OBJECT']
                if names_dict:
                    correct_name = [
                        k for k, v in names_dict.items() if object_name in v
                    ]
                    object_name = correct_name[0] if correct_name else object_name
                observer = hdr['OBSERVER']
                color_filter = hdr['FILTER']
                exptime = hdr['EXPTIME']
                
            row = {
                'obs_datetime': obs_datetime,
                'object_name': object_name,
                'observer': observer,
                'color_filter': color_filter,
                'exptime': exptime,
            }
            logger.debug(f'data row: {row}')
            folder_data.append(row)
        
    folder_data = sorted(folder_data, key=lambda x: x['obs_datetime'])
    
    return folder_data


def get_grouped_folder_data(folder_data, telescope_name):
    results = {}
    target = {}
    n_frames = 0
    prev_name = None

    for frame in folder_data:
        object_name = str(frame['object_name']).strip()
        if object_name not in results:
            object_dict = {
                'name': object_name,
                'datetime_start': frame['obs_datetime'],
                'observer': frame['observer'],
                'colorfilters': [],
                'total_exposure_time': 0,
                'number_of_frames': 0,
                'telescope': telescope_name,
            }
            results[object_name] = object_dict
        else:
            object_dict = results[object_name]
        object_dict['colorfilters'].append(frame['color_filter'])
        object_dict['datetime_end'] = frame['obs_datetime']
        object_dict['number_of_frames'] += 1
        object_dict['total_exposure_time'] += float(frame.get('exptime', 0))

    for object_name in results.keys():
        object_dict = results[object_name]
        object_dict['total_exposure_time'] = round(
                    object_dict['total_exposure_time'], 2)
        object_dict['colorfilters'] = [
                    {'name': c} for c in set(object_dict['colorfilters'])
                ]

    return results


def send_data(data_to_send):
    for folder_results in data_to_send:
        for _, target_data in folder_results.items():
            try:
                logger.debug(f'Sending data: {target_data}')
                response = requests.post(
                    UPLOAD_URL, auth=(DB_USER, DB_PASSWORD),
                        data=json.dumps(target_data),
                        headers={'content-type': 'application/json'})
            except (requests.ConnectionError, requests.Timeout) as e:
                logger.error(f'No DB connection - {e}')
                raise Exception(f'No connection to DB! - {e}')
            
            if not response.ok:
                logger.error(f'{response.content}\n {target_data}')


def get_info_from_db(args):
    try:
        telescope_url = STATS_URL + args.telescope_name
        response = requests.get(telescope_url, timeout=TIMEOUT,
                                auth=(DB_USER, DB_PASSWORD),
                    headers={'content-type': 'application/json'})
        logger.info('DB connection ready')
    except (requests.ConnectionError, requests.Timeout) as exception:
        logger.error('No DB connection')
        raise Exception('No connection to DB!')

    if not response.ok:
        raise Exception(f'{response.content}')

    return json.loads(response.content)

def validate_datetime(datetime_str):
    try:
        datetime_object = dateparser.parse(datetime_str)
    except ValueError as e:
        logger.error(f'{e}')
        raise Exception(e, 'Wrong datetime format')
    
    return datetime_object

def validate_data_dir(data_dir):
    if not data_dir or not os.path.isdir(data_dir):
        logger.error(f'Wrong data dir')
        raise Exception('Wrong data dir')
    return data_dir

def validate_names_file(names_path):
    if not os.path.isfile(names_path):
        logger.error('Wrong names file')
        raise Exception('Wrong names file')
    names_dict = {}
    try:
        with open(names_path) as f:
            _reader = csv.reader(f)
            for row in _reader:
                names_dict[row[0]] = row[1:]
    except Exception as e:
        logger.error(f'Wrong names file {e}')
        raise Exception(f'Wrong names file - {e}')
    return names_dict

def process(data_dir, names_dict, datetime_start, datetime_end, telescope_name):
    dirs_to_walk = sorted(
        get_dirs_to_walk(data_dir, datetime_start, datetime_end)
    )
    for _dir in dirs_to_walk:
        logger.info(f'Processing directory: {_dir}')
        print(f'Processing directory: {_dir}')
        data_to_send = []

        folder_files = get_files(_dir)
        folder_data = get_folder_data(folder_files, names_dict)
        grouped_folder_data = get_grouped_folder_data(
            folder_data, telescope_name
        )
        data_to_send.append(grouped_folder_data)
        send_data(data_to_send)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-t", "--telescope_name", type=str, required=True,
        help="Telescope name. Must exist in database"
    )
    parser.add_argument(
        "-d", "--data_dir", type=str, required=True,
        help="Data directory for telescope"
    )
    parser.add_argument(
        "-n", "--names_path", type=str, nargs='?', const='',
        help="Path to csv file with names dictionary"
    )       
    parser.add_argument(
        "-s", "--datetime_start", type=str, nargs='?', const='',
        help=("Where to start. If none, taken from database, \
               if none form database start from year 1900. \
               Datetime must be in iso format e.g  2019-01-27T12:06:21")
    )
    parser.add_argument(
        "-e", "--datetime_end", type=str, nargs='?', const='',
        help=("Where to end. If none, there is no end... \
               Datetime must be in iso format e.g  2019-01-27T12:06:21")
    )
    args = parser.parse_args()

    db_info = get_info_from_db(args)

    if args.datetime_start:
        datetime_start = args.datetime_start
    else:
        if db_info['last_datetime']:
            datetime_start = db_info['last_datetime']
        else:
            datetime_start = ZERO_DATETIME
    datetime_start_parsed = validate_datetime(datetime_start)

    if args.datetime_end:
        datetime_end = args.datetime_end
    else:
        datetime_end = INF_DATETIME
    datetime_end_parsed = validate_datetime(datetime_end)

    data_dir = validate_data_dir(args.data_dir)

    if args.names_path:
        names_dict = validate_names_file(args.names_path)
    else:
        names_dict = None

    print('Process start')
    logger.info(f'Process start - {dt.datetime.now().isoformat()}')
    try:
        process(
            data_dir,
            names_dict,
            datetime_start_parsed,
            datetime_end_parsed,
            args.telescope_name,
        )
        logger.info(f'Finished')
    except Exception as e:
        logger.error(f'Big Error!: {e}')
        raise(e)