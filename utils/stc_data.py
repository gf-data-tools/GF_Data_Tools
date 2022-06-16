# %%
import os
import json
from .text_table import TextTable
import logging
# %%
def get_stc_data(stc_dir, table_dir=None):
    stc_data = dict()
    if table_dir is not None:
        text_table = TextTable(table_dir)
    for fname in os.listdir(stc_dir):
        with open(os.path.join(stc_dir,fname)) as f:
            data = json.load(f)
            if table_dir is not None:
                data = convert_text(data,text_table)
            if len(data) > 0 and 'id' in data[0].keys():
                data = {d['id']: d for d in data}
            stc_data[os.path.splitext(fname)[0]] = data
    return stc_data
    

def convert_text(data, text_table):
    if type(data)==list:
        return [convert_text(i,text_table) for i in data]
    elif type(data)==dict:
        return {k: convert_text(v,text_table) for k,v in data.items()}
    else:
        return text_table(data)

# %%
if __name__=='__main__':
    logging.basicConfig(level='DEBUG',force=True)
    table_dir = r'.\data-miner\data\ch\asset\table'
    stc_dir = r'.\data-miner\data\ch\stc'
    stc = get_stc_data(stc_dir,table_dir)
# %%
