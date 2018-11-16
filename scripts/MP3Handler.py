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

#import lxml.etree as XML
import itertools

import gtts as gTTs
from unidecode import unidecode
from wawCommons import eprintf, toIntentName, printf
from DialogData import DialogData
from NodeData import NodeData

NAME_POLICY = 'soft'

# Watson Assistant limits number of options currently to 5, we cut the end of the list of options if it is longer
MAX_OPTIONS = 50

class MP3Handler(object):

    def __init__(self):
        pass

    def convertDialogData(self, dialogData, nodes):
        """ Convert Dialog Data of a single domain into mp3 and return pointer to the root XML element. """
        nodeArray = []
        for node_name in nodes: #for each node in the domain
            nodeData = dialogData.getNode(node_name)
           # nodeData.encode('utf-8')
            if nodeData == None:
                printf("WARNING: Not found a definition for a node name %s \n", node_name)
                continue
            nodeArray.append(nodeData.getRawOutputs())
        return nodeArray

    def conditionsArray(self, dialogData, nodes):
        conditions = []
        for node_name in nodes:
            conditionData=dialogData.getNode(node_name)
            if conditionData == None:
                printf("WARNING: Not found a definition for a node name %s \n", node_name)
                continue
            conditions.append(conditionData.getCondition())
        return conditions

