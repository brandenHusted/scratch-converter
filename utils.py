import os
import subprocess
import zipfile
from string import ascii_lowercase, digits
from random import choice


def init_folder(config: dict):
    if not os.path.exists(config['UF']):
        os.mkdir(config['UF'])
    if not os.path.exists(config['DF']):
        os.mkdir(config['DF'])


def check_lang(lang):
    if lang in ['en', 'de', "zh"]:
        return lang
    return "en"


def gen_key(prefix=""):
    """return a random string of length 8"""
    key = "".join(choice(ascii_lowercase + digits) for _ in range(8))
    key = f"{prefix}_{key}"
    return key


def run_command(command):
    process = subprocess.Popen(
        command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = process.communicate()
    stdout = stdout.decode('utf-8')
    stderr = stderr.decode('utf-8')
    return_code = process.returncode
    return stdout, stderr, return_code


def get_code_from_key(config, key):
    path = f"{config['DF']}/{key}/{key}.py"
    if key and os.path.exists(path):
        with open(path, 'r') as f:
            code = f.read()
        return code
    return None


def create_zip_folder(folder_path, zip_path):
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        for root, dirs, files in os.walk(folder_path):
            for file in files:
                file_path = os.path.join(root, file)
                zip_file.write(file_path, os.path.relpath(
                    file_path, folder_path))


def generate_zip(config, fn, convert_params: dict = {}):
    _, _, code = run_command(
        f"cd {config['DF']} && mkdir '{fn}'")
    if code != 0:
        return False, None, None

    lang = check_lang(convert_params.get("lang"))
    out, err, code = run_command(
        f"python -m pystage.convert.sb3 '{config['UF']}/{fn}.sb3' -l {lang} -d {config['DF']}/{fn}")
    if code != 0:
        return False, out, err

    create_zip_folder(f"{config['DF']}/{fn}",
                      f"{config['DF']}/{fn}.zip")
    return True, out, err


def delete_folder(path):
    """delete a folder by recursion"""
    for file in os.listdir(path):
        """if it is a direcotry, delete all files in it"""
        if os.path.isdir(os.path.join(path, file)):
            delete_folder(os.path.join(path, file))
        else:
            os.remove(os.path.join(path, file))
    os.rmdir(path)
    return True


def delete_files(config):
    """delete all files in UF and DF"""
    for file in os.listdir(config['DF']):
        """if it is a direcotry, delete all files in it"""
        if os.path.isdir(os.path.join(config['DF'], file)):
            delete_folder(os.path.join(config['DF'], file))
        else:
            os.remove(os.path.join(config['DF'], file))
    for file in os.listdir(config['UF']):
        os.remove(os.path.join(config['UF'], file))
    return True
