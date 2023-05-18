import os
import logging
from utils import gen_key, init_folder, generate_zip, delete_files
from flask import Flask, redirect, request, render_template, send_file, jsonify, url_for, flash, session
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
    logger.debug(session)
    key = session.get('key')
    session.pop('key', None)
    path = f"{app.config['DF']}/{key}/{key}.py"
    if key and os.path.exists(path):
        with open(path, 'r') as f:
            code = f.read()
        return render_template('index.html', key=key, code=code,)
    return render_template('index.html')


@app.route('/generate/file', methods=['POST'])
def upload_file():
    logger.debug(request.files)
    logger.debug(request.form)

    rsp = {
        "code": 1
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
    session["key"] = key
    file.save(os.path.join(app.config['UF'], f"{key}.sb3"))
    rst = generate_zip(app.config, key)
    if not rst[0]:
        rsp['code'] = 0
        rsp['msg'] = "Error in generating file!"
        rsp['out'] = rst[1]
        rsp['err'] = rst[2]
        return jsonify(rsp)
    rsp['msg'] = "File generated successfully!"
    rsp['out'] = rst[1]
    rsp['key'] = key
    return jsonify(rsp)


@app.route('/generate/link', methods=['POST'])
def upload_url():
    logger.debug(request.get_json())
    rsp = {
        "code": 1
    }

    if "link" not in request.get_json():
        rsp['code'] = 0
        rsp['msg'] = "No link!!"
        return jsonify(rsp)

    link = request.get_json()['link']
    file = ScratchDownloader("/tmp/scratch").get_sb3(link)
    key = gen_key()

    if not file.save(os.path.join(app.config['UF'], f"{key}.sb3")):
        rsp['code'] = 0
        rsp['msg'] = "Invalid URL or internal error!"
        return jsonify(rsp)

    rst = generate_zip(app.config, key)
    if not rst[0]:
        rsp['code'] = 0
        rsp['msg'] = "Error in generating file!"
        rsp['out'] = rst[1]
        rsp['err'] = rst[2]
        return jsonify(rsp)

    rsp['msg'] = "File generated successfully!"
    return jsonify(rsp)


@app.route('/download/<filename>')
def download_file(filename):
    return send_file(os.path.join(app.config['DF'], f"{filename}.zip"), as_attachment=True)


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
