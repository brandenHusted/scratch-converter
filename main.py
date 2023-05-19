import os
import logging
from utils import gen_key, init_folder, generate_zip, delete_files, get_code_from_key, check_lang
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


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/generate/file', methods=['POST'])
def upload_file():
    logger.debug(request.files)
    logger.debug(request.form)

    rsp = {
        "code": 1,
        "msg": "",
        "out": "",
        "err": ""
    }

    if 'file' not in request.files or not request.files['file'].filename:
        rsp['code'] = 0
        rsp['msg'] = "No file!!"
        return jsonify(rsp)

    if "fileName" not in request.form:
        rsp['code'] = 0
        rsp['msg'] = "No fileName!!"
        return jsonify(rsp)

    file = request.files['file']
    key = gen_key(request.form['fileName'])
    file.save(os.path.join(app.config['UF'], f"{key}.sb3"))

    convert_params = {
        "lang": request.form.get("lang")
    }
    rst = generate_zip(app.config, key, convert_params)
    if not rst[0]:
        rsp['code'] = 0
        rsp['msg'] = "Error in generating file!"
        rsp['out'] = rst[1]
        rsp['err'] = rst[2]
        return jsonify(rsp)
    rsp['msg'] = "File generated successfully!"
    rsp['out'] = rst[1]
    rsp['key'] = key
    rsp['python_code'] = get_code_from_key(app.config, key)
    return jsonify(rsp)


@app.route('/generate/link', methods=['POST'])
def upload_url():
    logger.debug(request.get_json())
    rsp = {
        "code": 1,
        "msg": "",
        "out": "",
        "err": ""
    }

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
        rsp['msg'] = "Error in generating file!"
        rsp['out'] = rst[1]
        rsp['err'] = rst[2]
        return jsonify(rsp)

    rsp['msg'] = "File generated successfully!"
    rsp['out'] = rst[1]
    rsp['key'] = key
    rsp['python_code'] = get_code_from_key(app.config, key)
    return jsonify(rsp)


@app.route('/download/<filename>')
def download_file(filename):
    # get the original name
    original_name = filename.rsplit("_")[0] + ".zip"
    return send_file(os.path.join(app.config['DF'], f"{filename}.zip"), as_attachment=True, download_name=original_name)


@app.route('/url/<id>')
def url(id):
    url = f"https://scratch.mit.edu/projects/{id}/"
    rst = ScratchDownloader("/tmp/scratch").get_sb3(url)
    if rst.save(f"{app.config['UF']}/{id}.sb3"):
        return send_file(f"{app.config['UF']}/{id}.sb3", as_attachment=True)
    else:
        return "Error"


if __name__ == "__main__":
    init_folder(app.config)
    delete_files(app.config)
    app.run(debug=True, port=5000, host='0.0.0.0')
