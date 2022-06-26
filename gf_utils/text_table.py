# %%
import os
import csv
import logging
# %%
class TextTable():
    def __init__(self, table_dir):
        self.dict = dict()
        for fname in os.listdir(table_dir):
            if fname == 'tableconfig.txt':
                continue
            logging.debug(f'Reading {fname}')
            with open(os.path.join(table_dir,fname),'r',encoding='utf-8') as f:
                reader = csv.reader(f)
                for row in reader:
                    # print(row)
                    k,v = row
                    self.dict[k] = v
    
    def __call__(self, k):
        return self.dict.get(k, k)
                    

# %%
if __name__=='__main__':
    logging.basicConfig(level='DEBUG',force=True)
    table_dir = r'..\data-miner\data\ch\asset\table'
    table = TextTable(table_dir)
    print(table('achievement-20000015'),table(32))


# %%
