# %%
import os
import csv
import logging
import re
# %%
class TextTable():
    def __init__(self, table_dir):
        self.dict = dict()
        for fname in os.listdir(table_dir):
            if fname == 'tableconfig.txt':
                continue
            logging.debug(f'Reading {fname}')
            with open(os.path.join(table_dir,fname),'r',encoding='utf-8') as f:
                for line in f.readlines():
                    k,*vs = line.split(',')
                    v = ','.join(vs)
                    v = re.sub(r'//c',',',v)
                    v = re.sub(r'//n','\n',v)
                    self.dict[k] = v.strip()
    
    def __call__(self, k):
        return self.dict.get(k, k)
                    

# %%
if __name__=='__main__':
    logging.basicConfig(level='DEBUG',force=True)
    table_dir = r'..\data\us\asset\table'
    table = TextTable(table_dir)
    print(table('battle_skill_config-210040301'))
    print(table('battle_skill_config-211001802'))
    print(table(1234567))


# %%
