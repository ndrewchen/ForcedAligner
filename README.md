# Forced Aligner

This project hooked up Flask with the Montreal Forced Aligner (MFA) to create a webpage that, when given a .wav audio file and a .txt transcript, plays the audio file back while simultaneously printing the transcript. Due to cache issues, it works best in incognito mode. 

To set this project up, you need to proceed with the following steps:
1. Install Conda for Python 3.8
2. Clone this repository
3. Run these commands to setup MFA
   - ```conda install --file conda-requirements.txt```
   - ```pip install montreal-forced-aligner
   - ```mfa thirdparty download```
   - ```mfa download acoustic english```
4. Run these commands to setup the dependencies required to run the flask server
   - TODO
