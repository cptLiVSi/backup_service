import hashlib
import os
import json
import datetime
import shutil
from pathlib import Path


# TODO: remove hardcode
target_dir = r'C:\Users\user\py\tst_b_up\t1'
target_dir_name = target_dir.split('\\')
root_dir = os.path.dirname(target_dir)
b_up_dir = root_dir + '\\' + target_dir_name[-1] + '_b_up'

current_datetime = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

list_of_files = []
dict_of_files_and_hashes = {}


def get_list_of_files(dir_path):
    for path, subdirs, files in os.walk(dir_path):
        for name in files:
            filename = os.path.join(path, name)
            list_of_files.append(filename)


def compute_file_hash(file_path, algorithm='sha256'):
    hash_func = hashlib.new(algorithm)

    with open(file_path, 'rb') as file:
        # Read the file in chunks of 8192 bytes
        while chunk := file.read(8192):
            hash_func.update(chunk)

    return hash_func.hexdigest()


def get_dict_of_files_and_hashes():
    for filename in list_of_files:
        dict_of_files_and_hashes[filename] = compute_file_hash(filename)


def save_json():
    with open(b_up_dir + r'\snapshot_last.json', 'w') as f:
        json.dump(dict_of_files_and_hashes, f, indent=4)
    with open(b_up_dir + r'\snapshot_' + current_datetime + '.json', 'w') as f:
        json.dump(dict_of_files_and_hashes, f, indent=4)


def backup_changed_files():
    os.makedirs(b_up_dir, exist_ok=True)
    try:
        with open(b_up_dir + r'\snapshot_last.json') as json_file:
            prev_snapshot = json.load(json_file)
    except FileNotFoundError:
        prev_snapshot = {}

    for k, v in dict_of_files_and_hashes.items():
        if prev_snapshot.get(k) != v:
            create_file_b_up(k)


def create_file_b_up(src):
    dst = Path(b_up_dir + '\\files\\' + src.split(target_dir)[-1])
    dst.parent.mkdir(parents=True, exist_ok=True)
    name, ext = os.path.splitext(dst)
    dst = "{name}_{timestamp}{ext}".format(name=name, timestamp=current_datetime, ext=ext)
    shutil.copyfile(src, dst)


get_list_of_files(target_dir)
get_dict_of_files_and_hashes()
backup_changed_files()
save_json()

