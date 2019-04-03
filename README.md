
watson-assistant-workbench-mp3-extension

This is an extension of WAW for creating mp3 files from a xlsx file.
It is necessary to create file private.cfg with personal credentials of Watson Assistant.

Create a xlsx file and save it to example\mp3_app\xls
The first row in the file are the actions, second row are reactions.
WAW takes reactions and transform it to mp3 file. Mp3 is saved in generated mp3 directory
The name of every mp3 is written in cddf txt file. 

For transformating text to mp3 is necessary to install Google text to speech module 
```
pip install -m gTTs 
```

list of languages is here: https://cloud.google.com/speech-to-text/docs/languages
For changing your bot just change language code in !Meta command in xlsx file. 

For using Watson Text to Speech create credentials in IBM Cloud and save them to credentials.json, save them and change classpath in config.py
Also install watson developer cloud and import TextToSpeechV1
```
pip install --upgrade watson-developer-cloud

```

```
from watson_developer_cloud import TextToSpeechV1

```
