# %%
from ..utils.stc_data import get_stc_data

# %%
table_dir = r'data-miner\data\ch\asset\table'
stc_dir = r'data-miner\data\ch\stc'
stc = get_stc_data(stc_dir,table_dir)

# %%
enemy_in_team = stc['enemy_in_team']
enemy_team = stc['enemy_team']
enemy_character_type = stc['enemy_character_type']

# %%
team_data = dict()
for id, team in enemy_team.items():
    key_leader = str(team['enemy_leader'])
    leader = enemy_character_type.get(key_leader,{'name':key_leader})['name']
    team_data[id] = dict(id=id, leader=leader, effect=team['effect_ext'], enemy=[], mission='')

# %%
for id, enemy in enemy_in_team.items():
    key_character = str(enemy['enemy_character_type_id'])
    name = enemy_character_type.get(key_character,{'name':key_character})['name']
    key_team = str(enemy['enemy_team_id'])
    if key_team in team_data.keys():
        team_data[str(enemy['enemy_team_id'])]['enemy'].append(
            dict(
                name=name,
                **enemy,
            )
        )

# %%
mission = stc['mission']
spot = stc['spot']
for id,sp in spot.items():
    team_id = sp['enemy_team_id']
    mission_id = sp['mission_id']
    if team_id != 0:
        team_data[str(team_id)]['mission'] = mission.get(str(mission_id),{'name':str(mission_id)})['name']

# %%
import csv
def enemy_string(**kwargs):
    string = ''
    for k,v in kwargs.items():
        string += f'{k}*{v} '
    return string

with open('enemy_team_analyze/enemy_team_info.csv','w', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=['id','mission','leader','effect','enemies'])
    writer.writeheader()
    for id,team in team_data.items():
        enemy_count = dict()
        for enemy in team['enemy']:
            enemy_count.setdefault(enemy['name'],0)
            enemy_count[enemy['name']] += enemy['number']
        team['enemies'] = enemy_string(**enemy_count)
        writer.writerow(
            dict(
                mission=team['mission'], 
                id=team['id'], 
                leader=team['leader'], 
                effect=team['effect'], 
                enemies=enemy_string(**enemy_count),
            )
        )
    

# %%



