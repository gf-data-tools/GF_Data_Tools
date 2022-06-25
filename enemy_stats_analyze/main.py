# %%
import pandas as pd
from gf_utils.stc_data import get_stc_data

stc_data = get_stc_data(
    stc_dir=r'data\ch\stc',
    table_dir=r'data\ch\asset\table',
    subset=['enemy_in_team','enemy_character_type','enemy_standard_attribute']
)