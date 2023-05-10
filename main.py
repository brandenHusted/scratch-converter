import os
from flask import Flask, redirect, request, render_template, send_file, url_for, flash
import subprocess
import zipfile

app = Flask(__name__)
app.secret_key = 'secret_key'
app.config['UPLOAD_FOLDER'] = 'scratch_files'
app.config['DOWNLOAD_FOLDER'] = 'generated_files'


def create_zip_folder(folder_path, zip_path):
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        for root, dirs, files in os.walk(folder_path):
            for file in files:
                file_path = os.path.join(root, file)
                zip_file.write(file_path, os.path.relpath(
                    file_path, folder_path))


def gen_key():
    import random
    import string
    return ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(16))


def run_command(command):
    process = subprocess.Popen(
        command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = process.communicate()
    return_code = process.returncode
    return stdout, stderr, return_code


def generate_zip(key):
    _, _, code = run_command(f"cd {app.config['DOWNLOAD_FOLDER']} && mkdir {key}")
    if code != 0:
        return False
    _, _, code = run_command(
        f"python -m pystage.convert.sb3 {app.config['UPLOAD_FOLDER']}/{key}.sb3 -l en -d {app.config['DOWNLOAD_FOLDER']}/{key}")
    if code != 0:
        return False

    create_zip_folder(f"{app.config['DOWNLOAD_FOLDER']}/{key}",
                      f"{app.config['DOWNLOAD_FOLDER']}/{key}.zip")
    return True


@app.route('/')
def index():
    filename = request.args.get('message')
    return render_template('index.html', filename=filename)


@app.route('/upload', methods=['POST'])
def upload_file():
    file = request.files['file']
    if not file.filename:
        flash('No file selected!')
        return redirect(url_for('index'))
    key = gen_key()
    file.save(os.path.join(app.config['UPLOAD_FOLDER'], f"{key}.sb3"))

    # flash('Generating file...')
    rst = generate_zip(key)
    if not rst:
        flash('Error in generating file!')
        return redirect(url_for('index'))
    return redirect(f"/download/{key}.zip")


@app.route('/download/<filename>')
def download_file(filename):
    return send_file(os.path.join(app.config['DOWNLOAD_FOLDER'], filename), as_attachment=True)


app.run(debug=True, host='0.0.0.0')
