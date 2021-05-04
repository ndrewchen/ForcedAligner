import os
from flask import Flask, render_template, request, send_file
from werkzeug.utils import secure_filename
import subprocess
import textgrid

UPLOAD_FOLDER = '../uploads'
ALLOWED_EXTENSIONS = {'wav', 'txt'}
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def interpret_textgrid():
    tg = textgrid.TextGrid.fromFile('../output/uploads-foo.TextGrid')
    intervals = tg[0].intervals
    words = [interval.mark for interval in intervals]
    start_times = [interval.minTime for interval in intervals]

    return [words, start_times]


@app.route('/')
def upload_files():
    return render_template('upload.html')


@app.route('/', methods=['POST'])
def upload_file():
    if request.method == 'POST':
        f1 = request.files['audiofile']
        f2 = request.files['textfile']
        if allowed_file(f1.filename) and allowed_file(f2.filename):
            f1.save(os.path.join(app.config['UPLOAD_FOLDER'], 'foo.wav'))
            # f1.save(os.path.join('static', 'foo.wav'))
            f2.save(os.path.join(app.config['UPLOAD_FOLDER'], 'foo.txt'))
            subprocess.call(['sh', '../aligner_script.sh'])
            return render_template('play.html', transcript=interpret_textgrid())


@app.route('/get-audio/')
def get_audio():
    try:
        return send_file('../uploads/foo.wav', attachment_filename='foo.wav')
    except Exception as e:
        return str(e)


if __name__ == '__main__':
    app.run(debug=True)
