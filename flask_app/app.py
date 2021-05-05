import os
import string
import flask
from flask import Flask, render_template, request, send_file
from werkzeug.utils import secure_filename
import subprocess
import textgrid

UPLOAD_FOLDER = '../uploads'
ALLOWED_EXTENSIONS = {'wav', 'txt'}
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


def allowed_file(filename):
    # check that an uploaded file is .wav or .txt
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def interpret_textgrid():
    # uses textgrid package to get the useful parts of the output of MFA
    tg = textgrid.TextGrid.fromFile('../output/uploads-foo.TextGrid')
    intervals = tg[0].intervals
    words = [interval.mark for interval in intervals]
    start_times = [interval.minTime for interval in intervals]
    end_times = [interval.maxTime for interval in intervals]

    words1 = []
    for _ in words:
        words1.append(_.replace("<unk>", ""))

    return [words1, start_times, end_times]


def realign_original_txt():
    # realigns the output of MFA to the original text (MFA auto-cleans out capitalization/punctuation + misses words)
    tg = interpret_textgrid()
    mapping = [[] for i in range(len(tg[0]))]
    original = []
    cleaned_original = []
    out = [[] for _ in range(2)]

    # generate mappings
    with open('../uploads/foo.txt', 'r') as file:
        original = file.read().split()
        cleaned_original = [s.translate(str.maketrans('', '', string.punctuation)).lower() for s in original]

        ptr = 0
        for i in range(len(tg[0])):
            if not tg[0][i]:
                continue
            while tg[0][i] != cleaned_original[ptr]:
                mapping[i - 1].append(ptr)
                ptr += 1
            mapping[i].append(ptr)
            ptr += 1

        if ptr < len(original):
            for i in range(ptr, len(original)):
                mapping[-1].append(i)

    # generate output based on mappings
    for i in range(len(mapping)):
        # space w/o mappings
        if len(mapping[i]) == 0:
            out[0].append('')
            out[1].append(tg[1][i])

        # word
        elif tg[0][i]:
            out[0].append(original[mapping[i][0]])
            out[1].append(tg[1][i])

        # space w/ mappings (words are missing)
        else:
            window = [tg[1][i], tg[2][i]]
            total_time = window[1] - window[0]
            total_chars = sum([len(cleaned_original[_]) for _ in mapping[i]])
            # assume speaking @ 200wpm w/ 5 characters per word --> 75ms / character

            # window time >= window size --> distribute proportionally to characters
            if total_time <= total_chars * 0.075:
                current_time = window[0]
                for j in mapping[i]:
                    out[0].append(original[j])
                    out[1].append(current_time)
                    current_time += len(cleaned_original[j]) / total_chars * 0.075

            # window time < window size --> distribute @ 75 ms / char + equal spaces between words
            else:
                space_time = total_time - total_chars * 0.075
                space_time /= len(mapping[i]) + 1
                current_time = window[0]
                out[0].append('')
                out[1].append(current_time)
                current_time += space_time
                for j in mapping[i]:
                    out[0].append(original[j])
                    out[1].append(current_time)
                    current_time += len(cleaned_original[j]) * 0.075
                    out[0].append('')
                    out[1].append(current_time)
                    current_time += space_time

    return out


def preremove_apostrophes():
    with open('../uploads/foo.txt', 'r') as readfile:
        str1 = readfile.read()
        str2 = str1.replace("'", "")
        open('../uploads/foo.txt', 'w').write(str2)


audio_num = 2


def get_audio_num():
    global audio_num
    audio_num += 1
    return audio_num


def dir_last_updated(folder):
    return str(max(os.path.getmtime(os.path.join(root_path, f))
                   for root_path, dirs, files in os.walk(folder)
                   for f in files))


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
            f2.save(os.path.join(app.config['UPLOAD_FOLDER'], 'foo.txt'))
            preremove_apostrophes()
            subprocess.call(['sh', '../aligner_script.sh'])

            return flask.redirect('/play')


@app.route('/play/', methods=['GET'])
def play_file():
    return render_template('play.html', transcript=realign_original_txt())


@app.route('/get-audio/')
def get_audio():
    try:
        return send_file('../uploads/foo.wav', attachment_filename='foo'+str(get_audio_num())+'.wav', cache_timeout=0)
    except Exception as e:
        return str(e)
