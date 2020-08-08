import json
from collections import defaultdict
import logging

from data_utilities import DATA_DIR

def load_metadata():
    all_metadata=defaultdict(list)
    with open(DATA_DIR+'arxiv-metadata-oai-snapshot.json') as f:
        for line in f:
            data=json.loads(line)
            print(data.keys())
            all_metadata[data['id']].append(data)
    metadata={}
    for key,value in all_metadata.items():
        if len(value)==1:
            metadata[key]=value
        else:
            metadata[key] = value[0]
            remainingValues=value[1:]
            for remainingValue in remainingValues:
                for k,v in value:
                    if type(v) is list:


