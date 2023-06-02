import os
import subprocess as sp
import zipfile
from threading import Timer
from string import ascii_lowercase, digits
from random import choice
from logger import *


def init_folder(config: dict):
    os.system(f"rm {config['UF']} -r -f")
    os.system(f"rm {config['DF']} -r -f")
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
    if isinstance(prefix, str) and len(prefix) > 15:
        prefix = prefix[:10]
        if prefix.endswith("_"):
            prefix = prefix[:-1]
    key = "".join(choice(ascii_lowercase + digits) for _ in range(8))
    key = f"{prefix}_{key}"
    return key


def run_command(command):
    # hide the error message like ALSA lib pcm.c:2565:(snd_pcm_open_noupdate) Unknown PCM cards.pcm.rear
    command += " 2>/dev/null"
    logger.debug(f"Running command: {command}")
    try:
        output = sp.check_output(
            command, stderr=sp.STDOUT, timeout=20, shell=True
        )
        output = output.decode("utf-8")
        return True, output
    except sp.CalledProcessError as e:
        logger.debug(e.args[1])
        output = "Bad command executed"
    except sp.TimeoutExpired:
        output = "Timeout"
    except Exception as e:
        output = f"Unknown error: {e.args[1]}"

    return False, output


def get_code_from_key(config, key):
    path = f"{config['DF']}/{key}/{key}.py"
    if key and os.path.exists(path):
        with open(path, 'r') as f:
            code = f.read()

        delete(f"{config['DF']}/{key}")
        delete(f"{config['DF']}/{key}.zip")
        delete(f"{config['UF']}/{key}.sb3")

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
    ok, output = run_command(
        f"cd {config['DF']} && mkdir '{fn}'")
    if not ok:
        return ok, output

    lang = check_lang(convert_params.get("lang"))
    ok, output = run_command(
        f"python -m pystage.convert.sb3 '{config['UF']}/{fn}.sb3' -l {lang} -d {config['DF']}/{fn}")
    if not ok:
        return ok, output

    create_zip_folder(f"{config['DF']}/{fn}",
                      f"{config['DF']}/{fn}.zip")
    return ok, output


def run(command):
    task = sp.Popen(command, shell=True, stdout=sp.DEVNULL, stderr=sp.DEVNULL)
    logger.debug(f"Running command {command}")
    task.wait()
    if task.returncode != 0:
        logger.debug(f"Failed to execute command: {command}")


def delete(path, sec=600):
    if not os.path.exists(path):
        return

    if os.path.isdir(path):
        timer = Timer(sec, run, args=(f"rm {path}/ -r -f",))
    elif os.path.isfile(path):
        timer = Timer(sec, run, args=(f"rm {path} -f",))

    timer.start()
