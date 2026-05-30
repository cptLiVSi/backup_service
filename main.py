import hashlib
import json
import datetime
import shutil
from pathlib import Path


# TODO: remove hardcode
TARGET_DIR = Path(r'C:\Users\user\py\tst_b_up\t1')
ROOT_DIR = Path(TARGET_DIR).parent
B_UP_DIR = ROOT_DIR / f'{TARGET_DIR.name}_backup'

current_datetime = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")


def get_list_of_files(dir_path):
    return [str(p) for p in Path(dir_path).rglob("*") if p.is_file()]


def compute_file_hash(file_path, algorithm='sha256'):
    hash_func = hashlib.new(algorithm)

    with open(file_path, 'rb') as file:
        # Read the file in chunks of 8192 bytes
        while chunk := file.read(8192):
            hash_func.update(chunk)

    return hash_func.hexdigest()


def get_dict_of_files_and_hashes(list_of_files):
    return {filepath: compute_file_hash(filepath) for filepath in list_of_files}


def save_json(dict_of_files_and_hashes):
    with (B_UP_DIR / 'snapshot_last.json').open('w') as f:
        json.dump(dict_of_files_and_hashes, f, indent=4)
    with (B_UP_DIR / ('snapshot_' + current_datetime + '.json')).open('w') as f:
        json.dump(dict_of_files_and_hashes, f, indent=4)


def backup_changed_files(dict_of_files_and_hashes):
    B_UP_DIR.mkdir(parents=True, exist_ok=True)
    snapshot_path = B_UP_DIR / 'snapshot_last.json'
    try:
        with snapshot_path.open() as json_file:
            prev_snapshot = json.load(json_file)
    except FileNotFoundError:
        prev_snapshot = {}

    for k, v in dict_of_files_and_hashes.items():
        if prev_snapshot.get(k) != v:
            create_file_b_up(k)


# TODO: handle double suffixes
def create_file_b_up(src):
    src = Path(src)
    rel_path = src.relative_to(TARGET_DIR)
    dst = B_UP_DIR / 'files' / rel_path
    dst.parent.mkdir(parents=True, exist_ok=True)

    name = dst.stem
    ext = dst.suffix
    dst = dst.with_name(f"{name}_{current_datetime}{ext}")
    shutil.copyfile(src, dst)


list_of_files = get_list_of_files(TARGET_DIR)
dict_of_files_and_hashes = get_dict_of_files_and_hashes(list_of_files)
backup_changed_files(dict_of_files_and_hashes)
save_json(dict_of_files_and_hashes)

