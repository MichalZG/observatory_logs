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
from update_config import *


def get_dirs_to_walk(data_dir, datetime_start):
    folders_in_root = os.listdir(data_dir)

    date_start = datetime_start.date()
    if datetime_start.hour >= 12:
        date_start = date_start + dt.timedelta(days=1)
        
    p = re.compile(DATE_REGEX) 
    
    dirs_to_walk = []
    for _d in os.listdir(data_dir):
        if (p.match(_d) and \
                dt.datetime.strptime(_d, '%Y-%m-%d').date() >= date_start):
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


def get_folder_data(files_to_open):
    folder_data = []
    for f in files_to_open:
        with gzip.open(f, 'rb') as f_in:
            hdr = dict(fits.getheader(f))
            
            obs_datetime = dt.datetime.strptime(
                hdr['DATE-OBS'] + 'T' + hdr['TIME-OBS'],
                '%Y-%m-%dT%H:%M:%S.%f').isoformat()
            
            object_name = hdr['OBJECT']
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
        folder_data.append(row)
        
    folder_data = sorted(folder_data, key=lambda x: x['obs_datetime'])
    
    return folder_data


def get_grouped_folder_data(folder_data, telescope_name):
    results = []
    target = {}
    n_frames = 0
    prev_name = None

    for frame in folder_data:
        if frame['object_name'] != prev_name:
            n_frames = 0
            if target:
                target['datetime_end'] = frame['obs_datetime']
                target['colorfilters'] = [
                    {'name': c} for c in target['colorfilters']
                ]
                results.append(target)
            target = {}
            prev_name = frame['object_name']
            target['name'] = frame['object_name']
            target['datetime_start'] = frame['obs_datetime']
            target['observer'] = frame['observer']
            target['colorfilters'] = []
            target['total_exposure_time'] = 0
            target['number_of_frames'] = 0
            target['telescope'] = telescope_name

        target['number_of_frames'] += 1    
        target['total_exposure_time'] += float(frame.get('exptime', 0))
        if frame['color_filter'] not in target['colorfilters']:
            target['colorfilters'].append(frame['color_filter'])

    return results

def send_data(data_to_send):
    for folder_ds in data_to_send:
        for ds in folder_ds:
            try:
                response = requests.post(
                    UPLOAD_URL, auth=(DB_USER, DB_PASSWORD),
                        data=json.dumps(ds),
                        headers={'content-type': 'application/json'})
            except (requests.ConnectionError, requests.Timeout) as exception:
                raise Exception('No connection to DB!')
            print(response.ok)
            print(response.content)

def get_info_from_db(args):
    try:
        telescope_url = STATS_URL + args.telescope_name
        response = requests.get(telescope_url, timeout=TIMEOUT,
                                auth=(DB_USER, DB_PASSWORD),
                    headers={'content-type': 'application/json'})
        print('connected')
    except (requests.ConnectionError, requests.Timeout) as exception:
        raise Exception('No connection to DB!')

    if not response.ok:
        raise Exception(f'{response.content}')

    return json.loads(response.content)

def validate_datetime(datetime_start):
    try:
        datetime_start = dt.datetime.strptime(
            datetime_start, "%Y-%m-%dT%H:%M:%S")
    except ValueError as e:
        raise Exception(e, 'Wrong datetime format')
    
    return datetime_start

def validate_data_dir(data_dir):
    if not data_dir or not os.path.isdir(data_dir):
        raise Exception('Wrong data dir')
    return data_dir

def process(data_dir, datetime_start, telescope_name):
    dirs_to_walk = sorted(get_dirs_to_walk(data_dir, datetime_start))
    data_to_send = []
    for _dir in dirs_to_walk:
        print('#'*9)
        pp(_dir)

        folder_files = get_files(_dir)
        folder_data = get_folder_data(folder_files)
        grouped_folder_data = get_grouped_folder_data(
            folder_data, telescope_name
        )
        data_to_send.append(grouped_folder_data)
        pp(grouped_folder_data)
        print('#'*9)

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
        "-s", "--datetime_start", type=str, nargs='?', const='',
        help=("Where to start. If none, taken from database, \
               if none form database start from year 1900. \
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
    data_dir = validate_data_dir(args.data_dir)
    print('process')
    process(data_dir, datetime_start_parsed, args.telescope_name)