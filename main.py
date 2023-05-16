import os
from utils import gen_key, init_folder, generate_zip, delete_files
from flask import Flask, redirect, request, render_template, send_file, url_for, flash
from downloader import ScratchDownloader

app = Flask(__name__)
app.secret_key = 'secret_key'
app.config['UF'] = 'scratch_files'
app.config['DF'] = 'generated_files'


@app.route('/')
def index():
    key = request.args.get('key')
    path = f"{app.config['DF']}/{key}/{key}.py"
    if key and os.path.exists(path):
        with open(path, 'r') as f:
            code = f.read()
        return render_template('index.html', key=key, code=code, ok=1)
    return render_template('index.html')


@app.route('/upload', methods=['POST'])
def upload_file():
    file = request.files['file']
    if not file.filename:
        flash('No file selected!')
        return redirect(url_for('index'))
    key = gen_key()
    file.save(os.path.join(app.config['UF'], f"{key}.sb3"))

    # flash('Generating file...')
    rst = generate_zip(app.config, key)
    if not rst[0]:
        flash('Error in generating file!')
        flash(rst[1])
        flash(rst[2])
        return redirect(url_for('index'))
    flash('File generated successfully!')
    # for line in rst[1].split('\r\n'):
    #     flash(line)
    return redirect(url_for('index', key=key))


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
