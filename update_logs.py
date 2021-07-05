#######################
# Template script for update logs
# Created for T60 telescope
#######################


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
import logging
from dotenv import dotenv_values

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

config = dotenv_values(".env")

ALLOWED_EXT = ['.gz', '.bz2', '.fit', '.fits']
FORBIDDEN_KEYS = ['HISTORY', 'COMMENT']
DATE_REGEX = '^\d{4}\-(0[1-9]|1[012])\-(0[1-9]|[12][0-9]|3[01])$'


def check_in_dict(_dict, _name):
    _name = _name.strip()
    _name_up = _name.upper()
    if _name in _dict.keys():
        return _name
    elif _name_up in _dict.keys():
        return _name_up
    else:
        for header, body in _dict.items():
            if _name_up in body: return header
    return _name


def read_dict(_file):
    _dict = {}
    with open(_file) as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            row = [x for x in row if x]
            if not row: continue
            header = row[0]
            body = set([x.upper() for x in row[1:]])
            _dict[header] = body
    return _dict


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


def get_folder_data(files_to_open, names_dict, filters_dict, observers_dict):
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
                
                object_name = check_in_dict(names_dict, hdr['OBJECT'])
                observers = [
                    check_in_dict(observers_dict, observer) for observer in hdr['OBSERVER'].strip().split()
                ]
                observers = [
                    {'name': observer} for observer in observers
                ]
                color_filter = check_in_dict(filters_dict, hdr['FILTER'])
                exptime = hdr['EXPTIME']
                
            row = {
                'obs_datetime': obs_datetime,
                'object_name': object_name,
                'observers': observers,
                'color_filter': color_filter,
                'exptime': exptime,
            }
            logger.debug(f'data row: {row}')
            folder_data.append(row)
        
    folder_data = sorted(folder_data, key=lambda x: x['obs_datetime'])
    
    return folder_data


def get_grouped_folder_data(folder_data, telescope_name):
    results = {}
    for frame in folder_data:
        object_name = str(frame['object_name']).strip()
        if object_name not in results:
            object_dict = {
                'name': object_name,
                'datetime_start': frame['obs_datetime'],
                'observers': frame['observers'],
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
                    url=config['UPLOAD_URL'],
                    auth=(
                        config['REST_USER'],
                        config['REST_PASSWORD']
                        ),
                    data=json.dumps(target_data),
                    headers={'content-type': 'application/json'})
            except (requests.ConnectionError, requests.Timeout) as e:
                logger.error(f'No DB connection - {e}')
                raise Exception(f'No connection to DB! - {e}')
            
            if not response.ok:
                logger.error(f'{response.content}\n {target_data}')


def get_info_from_db(args):
    try:
        telescope_url = config['TELESCOPE_STATS_URL'] + args.telescope_name
        response = requests.get(
            url=telescope_url,
            timeout=float(config.get('TIMEOUT', 10)),
            auth=(
                config['REST_USER'],
                config['REST_PASSWORD']
                ),
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

def validate_dict_file(dict_file):
    if not os.path.isfile(dict_file):
        logger.error(f'No dict file: {dict_file}')
        return False
    return True

def process(
    data_dir, datetime_start, datetime_end,
    telescope_name, names_dict, filters_dict, observers_dict):
    dirs_to_walk = sorted(
        get_dirs_to_walk(data_dir, datetime_start, datetime_end)
    )
    for _dir in dirs_to_walk:
        logger.info(f'Processing directory: {_dir}')
        print(f'Processing directory: {_dir}')
        data_to_send = []

        folder_files = get_files(_dir)
        folder_data = get_folder_data(
            folder_files, names_dict, filters_dict, observers_dict
        )
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
        "-nd", "--names_dict", type=str, nargs='?', const='',
        help="Path to csv file with names dictionary"
    )       
    parser.add_argument(
        "-fd", "--filters_dict", type=str, nargs='?', const='',
        help="Path to csv file with color filters dictionary"
    )       
    parser.add_argument(
        "-od", "--observers_dict", type=str, nargs='?', const='',
        help="Path to csv file with observers dictionary"
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
            datetime_start = config.get('ZERO_DATETIME', '1900-01-01T12:00:00')
    datetime_start_parsed = validate_datetime(datetime_start)

    if args.datetime_end:
        datetime_end = args.datetime_end
    else:
        datetime_end = config.get('INF_DATETIME', '2100-01-01T12:00:00')
    datetime_end_parsed = validate_datetime(datetime_end)

    data_dir = validate_data_dir(args.data_dir)

    names_dict = {}
    if args.names_dict:
        if validate_dict_file(args.names_dict):
            names_dict = read_dict(args.names_dict)

    filters_dict = {}
    if args.filters_dict:
        if validate_dict_file(args.filters_dict):
            names_dict = read_dict(args.filters_dict)

    observers_dict = {}
    if args.observers_dict:
        if validate_dict_file(args.observers_dict):
            observers_dict = read_dict(args.observers_dict)

    print('Process start')
    logger.info(f'Process start - {dt.datetime.now().isoformat()}')
    try:
        process(
            data_dir,
            datetime_start_parsed,
            datetime_end_parsed,
            args.telescope_name,
            names_dict, filters_dict, observers_dict
        )
        logger.info(f'Finished')
    except Exception as e:
        logger.error(f'Big Error!: {e}')
        raise(e)