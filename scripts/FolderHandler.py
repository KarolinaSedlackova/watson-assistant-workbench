import os, re
import unicodedata, unidecode
from openpyxl import load_workbook
from wawCommons import printf, eprintf, toIntentName
from zipfile import BadZipfile
from xml.sax.saxutils import escape
import DialogData as Dialog
from DialogData import DialogData
from itertools import izip_longest
from NodeData import NodeData
import more_itertools
from XLSXHandler import XLSXHandler


class FolderHandler(object):

    def __init__(self,config):
        # self._dialogData=DialogData(config)
        self._config = config

# CREATE FOLDER IF DOES NOT EXIST
    def create_folder(self,blocks,config):
        for block in blocks:
            if block[2][0][0] and block[2][0][0].startswith("!Fold"):
                folder=block[2][0][0][8::]
                path= os.path.abspath(getattr(config,'common_generated_mp3')[0])
                if not os.path.isdir(path+"/"+folder):
                    os.makedirs(path+"/"+folder)

