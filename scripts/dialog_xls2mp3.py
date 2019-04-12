from __future__ import print_function

# coding: utf-8
import itertools

"""
Copyright 2018 IBM Corporation
Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at
    http://www.apache.org/licenses/LICENSE-2.0
Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""
import sys, argparse, os, codecs
from cfgCommons import Cfg
from XLSXHandler import XLSXHandler
from MP3Handler import MP3Handler
from wawCommons import printf, eprintf
from FolderHandler import FolderHandler
from gtts import gTTS
from watson_developer_cloud import TextToSpeechV1
import json
from config import CONFIG_CLASSPATH


def load_credentials(credential_file_path):
    credentials = json.load(open(credential_file_path, "rb"))
    return credentials.get("apikey"), credentials.get("url")


def eng_create_MP3_file (dialogData, handler, config):
    ''' GENERATING ENGLISH MP3s for bot '''
    iam_apikey, url = load_credentials(CONFIG_CLASSPATH)
    text_to_speech = TextToSpeechV1(iam_apikey=iam_apikey, url=url)
    if hasattr(config, 'common_generated_mp3') and not os.path.exists(getattr(config, 'common_generated_mp3')[0]):
        os.makedirs(getattr(config, 'common_generated_mp3')[0])
        print('Created new directory ' + getattr(config, 'common_generated_mp3')[0])
    domains = dialogData.getAllDomains()
    for domain_name in domains:
        audiable_data = handler.convertDialogData(dialogData, domains[domain_name])  # outputs
        num = 1
        i = 1
        output_data = [item for line in audiable_data for item in line]
        for line in output_data:
            directory = getattr(config, 'common_generated_mp3')[0]
            folders = dialogData.get_folder()
            if folders:
                in_folder = folders.index("!!Folder")
                if i <= in_folder:
                    directory = directory + '/' + folders[0][8::]
                    if folders[i] == "!!Folder":
                        num = 0
                        del (folders[0:i + 1])
                        i = 1
            i += 1
            num += 1
            name = '{0:03}'.format(num)
            with open(directory + '/' + name + '.mp3', 'wb') as audio_file:
                audio_file.write(
                    text_to_speech.synthesize(
                        line,
                        'audio/wav',
                        'en-US_AllisonVoice'
                    ).get_result().content)


def cs_create_MP3_file(dialogData, handler, config, lang):
    ''' GENERATING CZECH MP3s for bot '''
    output_data = []
    if hasattr(config, 'common_generated_mp3') and not os.path.exists(getattr(config, 'common_generated_mp3')[0]):
        os.makedirs(getattr(config, 'common_generated_mp3')[0])
        print('Created new directory ' + getattr(config, 'common_generated_mp3')[0])
    domains = dialogData.getAllDomains()
    for domain_name in domains:
        audiable_data = handler.convertDialogData(dialogData, domains[domain_name])  # outputs
        num = 1
        i = 1
        output_data = [item for line in audiable_data for item in line]
        # create mp3s and put their name to txt file
        for line in output_data:
            i += 1
            name = '{0:03}'.format(num)
            tts = gTTS(text=line, lang=lang)
            directory = getattr(config, 'common_generated_mp3')[0]
            folders = dialogData.get_folder()
            if folders:
                in_folder = folders.index("!!Folder")
                if i <= in_folder:
                    directory = directory + '/' + folders[0][8::]
                    if folders[i] == "!!Folder":
                        num = 0
                        del (folders[0:i + 1])
                        i = 1
            tts.save(directory + '/' + name + '.mp3')
            num += 1


def write_to_condensed_file(dialogData, config):
    # ADDING DEFINITIONS, ACTIONS, REACTIVE AND MENU TO TEXT FILE
    with open('cddf.txt', 'w') as cddf:
        name = "Default"
        reactive_outputs = dialogData.get_reactive_outputs()
        for item in reactive_outputs:
            if not item[0].startswith('0'):
                name = item[0]
                item.pop(0)
            for ch in ['[', ']', "'"]:
                if ch in str(item):
                    item = str(item).replace(ch, '')
            cddf.write("const PROGMEM int " + name + " = {5,0," + item + '}\n')
        # ADD MENU TO TEXT FILE
        menus = dialogData.get_all_menu()
        for menu in menus:
            cddf.write('const PROGMEM int ' + str(menu) + '\n')
        dialog_all = dialogData.get_dialog_all()
        s_dialog_all = ', '.join(dialog_all)
        cddf.write('const int* const dialog_all[] PROGMEM = {' + s_dialog_all + '}\n')
        dialog_sizes = dialogData.get_dialog_sizes()
        s_dialog_sizes = ''.join(dialog_sizes)
        cddf.write('const unsigned int dialog_all_sizes1[] = {' + s_dialog_sizes[1:-1] + '}\n')
        composite = dialogData.get_comoposite()
        print(composite)
        for item in composite:
            name = item[0]
            item = item[1::]
            for ch in ['[', ']', "'"]:
                if ch in str(item):
                    item = str(item).replace(ch, '')
            cddf.write("const PROGMEM int " + name + " = {7,0" + str(item[1::])+'}\n')
        cddf.close()


if __name__ == '__main__':
    printf('\nSTARTING: ' + os.path.basename(__file__) + '\n')
    parser = argparse.ArgumentParser(description='Creates dialog nodes with answers to intents .',
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    # optional arguments
    parser.add_argument('-x', '--common_xls', required=False, help='file with MSExcel formated dialog', action='append')
    parser.add_argument('-gm', '--common_generated_mp3', nargs='?', help='directory for generated mp3s')
    parser.add_argument('-c', '--common_configFilePaths', help='configuaration file', action='append')
    parser.add_argument('-oc', '--common_output_config', help='output configuration file')
    parser.add_argument('-v', '--common_verbose', required=False, help='verbosity', action='store_true')
    args = parser.parse_args(sys.argv[1:])
    config = Cfg(args)
    VERBOSE = hasattr(config, 'common_verbose')

    if hasattr(config, 'common_verbose') and getattr(config, 'common_verbose'):
        name_policy = 'soft_verbose'
    if not hasattr(config, 'common_xls'):
        eprintf('ERROR: xls is not defined')
        exit(1)

    if not hasattr(config, 'common_generated_mp3'):
        if VERBOSE: printf('INFO: generated mp3 parameter is not defined\n')
    xlsxHandler = XLSXHandler(config)
    folderHandler = FolderHandler(config)
    allDataBlocks = {}  # map of datablocks, key: Excel sheet name, value: list of all block in the sheet

    print(getattr(config, 'common_xls'))
    for fileOrFolder in getattr(config, 'common_xls'):
        if VERBOSE: printf('INFO: Searching in path: %s\n', fileOrFolder)
        if os.path.isdir(fileOrFolder):
            xlsDirList = os.listdir(fileOrFolder)
            for xlsFile in xlsDirList:
                if os.path.isfile(os.path.join(fileOrFolder, xlsFile)) and xlsFile.endswith('.xlsx') and \
                        not (xlsFile.startswith('~')) and not (xlsFile.startswith('.')):
                    xlsxHandler.parseXLSXIntoDataBlocks(fileOrFolder + "/" + xlsFile)
                else:
                    eprintf('WARNING: The file %s skipped due to failing file selection policy check. '
                            'It should be .xlsx file not starting with ~ or .(dot).\n',
                            os.path.join(fileOrFolder, xlsFile))

        elif os.path.exists(fileOrFolder):
            xlsxHandler.parseXLSXIntoDataBlocks(fileOrFolder)

    xlsxHandler.convertBlocksToDialogData()  # Blocks-> DialogData
    xlsxHandler.updateReferences()  # Resolving cross references
    xlsxHandler.definition_handler()
    xlsxHandler.action_handler()
    xlsxHandler.create_reactive()
    xlsxHandler.menu_handling()
    folderHandler.create_folder(xlsxHandler.getBlocks(), config)
    lang = (xlsxHandler.get_language())
    if 'en' not in lang:
        cs_create_MP3_file(xlsxHandler.getDialogData(), MP3Handler(), config, xlsxHandler.get_language())
    else:
        eng_create_MP3_file(xlsxHandler.getDialogData(), MP3Handler(), config)
    write_to_condensed_file(xlsxHandler.getDialogData(), config)
    printf('\nFINISHING: ' + os.path.basename(__file__) + '\n')
