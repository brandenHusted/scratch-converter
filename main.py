import os
import logging
import json
from utils import gen_key, init_folder, generate_zip, delete_files, get_code_from_key
from flask import Flask, request, render_template, send_file, jsonify
from downloader import ScratchDownloader

app = Flask(__name__)
app.secret_key = '3jfjdja5fgj5n32j4j3'
app.config['UF'] = 'scratch_files'
app.config['DF'] = 'generated_files'

# DEBUG, INFO, WARNING, ERROR, CRITICAL
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("my")

# get flask built-in logger
werkzeug_logger = logging.getLogger('werkzeug')
# only log higher than warning level
werkzeug_logger.setLevel(logging.WARNING)


def get_version():
    with open("version", "r") as f:
        return f"0.0.{f.read()}"


def get_translation():
    available_langs = ["zh", "en", "de"]
    lang = request.cookies.get("lang")
    if lang not in available_langs:
        lang = request.accept_languages.best_match(available_langs)
        lang = lang if lang else "en"
    with open(f"static/langs/{lang}.json", 'r') as f:
        translation = json.load(f)

    return translation, lang


def get_trans_from(key):
    translation, _ = get_translation()
    return translation.get(key, "Not Implemented")


def gen_rsp():
    return {
        "code": 1,
        "msg": "",
        "out": "",
        "err": ""
    }


@app.route('/')
def index():
    version = get_version()
    translation, lang = get_translation()

    if request.headers.get("X-Forwarded-Host").count("calvin") > 0:
        prefix = "/pystage"
    else:
        prefix = ""
    return render_template('index.html', **translation, lang=lang, version=version, prefix=prefix)


@app.route('/generate/file', methods=['POST'])
def upload_file():
    logger.debug(request.files)
    logger.debug(request.form)

    rsp = gen_rsp()

    if 'file' not in request.files or not request.files['file'].filename:
        rsp['code'] = 0
        rsp['msg'] = "No file!!"
        return jsonify(rsp)

    if "fileName" not in request.form:
        rsp['code'] = 0
        rsp['msg'] = "No fileName!!"
        return jsonify(rsp)

    file = request.files['file']
    logger.debug(request.form['fileName'])
    key = gen_key(request.form['fileName'])
    file.save(os.path.join(app.config['UF'], f"{key}.sb3"))

    convert_params = {
        "lang": request.form.get("lang")
    }
    rst = generate_zip(app.config, key, convert_params)
    if not rst[0]:
        rsp['code'] = 0
        rsp['msg'] = get_trans_from("error_in_generating")
        rsp['out'] = rst[1]
        rsp['err'] = rst[2]
        return jsonify(rsp)
    rsp['msg'] = get_trans_from("success_in_generating")
    rsp['out'] = rst[1]
    rsp['key'] = key
    rsp['python_code'] = get_code_from_key(app.config, key)
    return jsonify(rsp)


@app.route('/generate/link', methods=['POST'])
def upload_url():
    logger.debug(request.get_json())
    rsp = gen_rsp()

    if "link" not in request.get_json():
        rsp['code'] = 0
        rsp['msg'] = "No link!!"
        return jsonify(rsp)

    link = request.get_json()['link']
    file = ScratchDownloader("/tmp/scratch").get_sb3(link)
    key = gen_key(file.file_name)

    if not file.save(os.path.join(app.config['UF'], f"{key}.sb3")):
        rsp['code'] = 0
        rsp['msg'] = "Invalid URL or internal error!"
        return jsonify(rsp)

    convert_params = {
        "lang": request.get_json().get("lang")
    }
    rst = generate_zip(app.config, key, convert_params)
    if not rst[0]:
        rsp['code'] = 0
        rsp['msg'] = get_trans_from("error_in_generating")
        rsp['out'] = rst[1]
        rsp['err'] = rst[2]
        return jsonify(rsp)

    rsp['msg'] = get_trans_from("success_in_generating")
    rsp['out'] = rst[1]
    rsp['key'] = key
    rsp['python_code'] = get_code_from_key(app.config, key)
    return jsonify(rsp)


@app.route('/download/<filename>')
def download_file(filename):
    # get the original name
    original_name = filename.rsplit("_", 1)[0] + ".zip"
    logger.debug(f"{filename}, {original_name}")
    return send_file(os.path.join(app.config['DF'], f"{filename}.zip"), as_attachment=True, download_name=original_name)


if __name__ == "__main__":
    init_folder(app.config)
    delete_files(app.config)
    app.run(debug=True, port=5000, host='0.0.0.0')
