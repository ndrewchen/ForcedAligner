# Forced Aligner

This project hooked up Flask with the Montreal Forced Aligner (MFA) to create a webpage that, when given a .wav audio file and a .txt transcript, plays the audio file back while simultaneously printing the transcript. Due to cache issues, it works best in incognito mode. 

## Setup
To set this project up, you need to proceed with the following steps:
1. Install Conda for Python 3.8
2. Clone this repository
3. Run these commands to setup MFA
   - ```conda create -n aligner -c conda-forge openblas python=3.8 openfst pynini ngram baumwelch```
   - ```conda activate aligner```
   - ```pip install montreal-forced-aligner```
   - ```mfa thirdparty download```
   - ```mfa download acoustic english```
4. Install the packages ```flask``` and ```textgrid``` to setup the flask app
5. Run these commands to run ```app.py```
   - ```cd flask_app```
   - ```export FLASK_APP=app```
   - ```flask run```

The webpage can now be found at the address http://127.0.0.1:5000/. Open it in an incognito window.

## Video demonstration

A video demonstration is available here:
https://youtu.be/53vgKs7uGMc