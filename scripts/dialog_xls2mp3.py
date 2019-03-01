
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
from wawCommons import printf
from XLSXHandler import XLSXHandler
from MP3Handler import MP3Handler
from wawCommons import printf, eprintf
from FolderHandler import FolderHandler
from gtts import gTTS
import re



def createMP3File(dialogData, handler, config):
    outputData=[]
    if hasattr(config, 'common_generated_mp3') and not os.path.exists(getattr(config, 'common_generated_mp3')[0]):
           os.makedirs(getattr(config, 'common_generated_mp3')[0])
           print('Created new directory ' + getattr(config, 'common_generated_mp3')[0])
    domains = dialogData.getAllDomains()
    for domain_name in domains:
        audiableData=handler.convertDialogData(dialogData, domains[domain_name]) #outputs
        num=1
        i=1
        outputData = [item for line in audiableData for item in line]
        #create mp3s and put their name to txt file
        with open('cddf.txt', 'w') as cddf:
            for line in outputData:
                i+=1
                name = '{0:03}'.format(num)
                tts = gTTS(text=line, lang='cs')
                directory=getattr(config,'common_generated_mp3')[0]
                folders=dialogData.get_folder()
                if folders:
                    in_folder=folders.index("!!Folder")
                    if i<=in_folder:
                        directory=directory+'/'+folders[0][8::]
                        if folders[i]=="!!Folder":
                            num=0
                            del(folders[0:i+1])
                            i = 1
                tts.save(directory+'/'+name+'.mp3')
                num += 1
            # ADDING DEFINITIONS, ACTIONS, REACTIVE AND MENU TO TEXT FILE
            definitions = dialogData.get_arduino_definitions()
            for definition in definitions:
                cddf.write(definition + '\n')
            actions = dialogData.get_actions()
            for action in actions:
                cddf.write("#define " + action + '\n')
            for item in dialogData.get_reactive_outputs():
                item=str(item)
                for ch in ['[', ']', "'"]:
                    if ch in item:
                        item=item.replace(ch,'')
                cddf.write("const PROGMEM int reactive_MultiOp1[] = {5,0,"+item+'}\n')
            # ADD MENU TO TEXT FILE
            menus=dialogData.get_all_menu()
            for menu in menus:
                cddf.write('const PROGMEM int '+str(menu)+'\n')
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

    if not hasattr(config,'common_generated_mp3'):
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
    xlsxHandler.menu_handling(xlsxHandler.getBlocks())
    xlsxHandler.create_reactive()
    folderHandler.create_folder(xlsxHandler.getBlocks(), config)
    createMP3File(xlsxHandler.getDialogData(), MP3Handler(), config)
    printf('\nFINISHING: ' + os.path.basename(__file__) + '\n')