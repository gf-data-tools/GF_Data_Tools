# %%
from gf_utils.stc_data import get_stc_data
import os
import csv
import datetime
import pandas as pd
import re

from pathlib import Path
os.chdir(Path(__file__).resolve().parent)
# %%
region = 'ch'
stc_data = get_stc_data(
    stc_dir=f'../data-miner/data/{region}/stc', 
    table_dir=f'../data-miner/data/{region}/asset/table',
    subset=['enemy_character_type','enemy_in_team','enemy_team','spot','mission'],
)

# %%
get_df = lambda d, k: pd.DataFrame.from_records(iter(d.values()),columns=k,index='id').convert_dtypes()
s = get_df(stc_data['spot'],['id','mission_id','enemy_team_id'])
m = get_df(stc_data['mission'],['id','name'])
t = get_df(stc_data['enemy_team'],['id','enemy_leader'])
e = get_df(stc_data['enemy_in_team'],['id','enemy_team_id', 'enemy_character_type_id','number'])
c = get_df(stc_data['enemy_character_type'],['id','name'])
# %%
ec = e.join(c,on='enemy_character_type_id',rsuffix='_enemy_character_type',how='left').drop(columns='enemy_character_type_id').groupby(['enemy_team_id','name']).sum()
# %%
tl = t.join(c,on='enemy_leader').drop(columns='enemy_leader').rename(columns={'name':'leader'})
ms = s.join(m,on='mission_id').drop(columns=['mission_id'])
mstl = ms.join(tl,on='enemy_team_id',how='right').rename(columns={'name':'mission'}).groupby('enemy_team_id').first().fillna('')
mstl
# %%
mstlec = mstl.join(ec.reset_index().set_index('enemy_team_id')).reset_index().set_index(['enemy_team_id','leader','mission'])
mstlec
# %%
