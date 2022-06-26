# %%
import pandas as pd
from gf_utils.stc_data import get_stc_data
import numpy as np

stc_data = get_stc_data(
    stc_dir=r'..\data\ch\stc',
    table_dir=r'..\data\ch\asset\table',
    subset=['enemy_in_team','enemy_character_type','enemy_standard_attribute']
)


# %%
level_cfg = {i['level']: i for i in stc_data['enemy_standard_attribute']}
stat_keys = [i for i in level_cfg[1].keys() if i!='level']
# %%
level_df = pd.DataFrame.from_dict(level_cfg,orient='index')
# %%
enemy_df = pd.DataFrame.from_dict(stc_data['enemy_in_team'],orient='index',columns=['id','enemy_character_type_id','level'])
etype = pd.DataFrame.from_dict(stc_data['enemy_character_type'],orient='index',columns=['id','name','enemy_info','level']+stat_keys)
enemy_df = enemy_df.merge(etype,left_on='enemy_character_type_id',right_on='id',suffixes=[None,'_base']).drop(columns='id_base')
enemy_df = enemy_df.groupby(['enemy_character_type_id','level']).first().reset_index()
ratio = level_df.loc[enemy_df['level']].reset_index()/level_df.loc[enemy_df['level_base']].reset_index()
enemy_df[stat_keys] = np.ceil(enemy_df[stat_keys]*ratio[stat_keys]).astype(int)
enemy_df = enemy_df[['enemy_character_type_id','id','name','enemy_info','level']+stat_keys]
# %%
enemy_df = enemy_df.sort_values(['name','enemy_character_type_id','level'])
enemy_df.to_csv('test.csv')
# %%
