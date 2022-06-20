# %%
from gf_utils import stc_data
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
    subset=['gun'],
)

dstr2date = lambda dstr: datetime.date(2000+int(dstr[:2]),int(dstr[2:4]),int(dstr[4:]))

gun_info = dict()
for gun in stc_data['gun'].values():
    if gun['id']<2000:
        gun_info[gun['name']]=dict(
            name=gun['name'],
            id=gun['id'],
            rank=gun['rank'] if not gun['is_additional'] else 1,
        )

rescue_log = dict()
with open('doll_obtain_info.tsv', encoding='utf-8') as f:
    for row in csv.reader(f,delimiter='\t'):   
        event, start_time, end_time, *dolls = row
        start_time=dstr2date(start_time)
        end_time=dstr2date(end_time)
        for name in dolls:
            rescue_log.setdefault(name, {'first':{'event':'','time':dstr2date('300101')},'last':{'event':'','time':dstr2date('160520')},'info':gun_info[name]})
            if start_time <= rescue_log[name]['first']['time']:
                rescue_log[name]['first'] = {'event':event,'time':start_time}
            if end_time >= rescue_log[name]['last']['time']:
                rescue_log[name]['last'] = {'event':event,'time':end_time}

rescue_log = sorted(rescue_log.values(),key=lambda x:x['info']['id'])

# %%

today = datetime.date.today()
dmax = datetime.date(2030,1,1)
deltaday = lambda d1,d2: max((d1-d2).days,0)
rows = []
for record in rescue_log:
    last_time = record['last']['time']
    row = dict(
        id=record['info']['id'],
        name=record['info']['name'],
        rank=record['info']['rank'],
        first_event=record['first']['event'],
        first_time=record['first']['time'],
        last_event=record['last']['event'],
        last_time=record['last']['time'],
    )
    rows.append(row)

df = pd.DataFrame(rows)
table = df.style

color = ['magenta','white','cyan','limegreen','yellow','red']
styles =[
    {'selector': 'table','props': 'margin-left: auto; margin-right: auto;:center'},
    {'selector': 'tbody','props': 'color: white;'},
    {'selector': 'tr','props': 'background-color: #3f3f3f'},
    {'selector': 'td','props': 'padding:0.5em'},
    {'selector': 'tr:hover','props': 'background-color:#7f7f7f'},
    {'selector': 'th','props': 'background-color: blue; color: white;'},
    {'selector': 'caption','props':'color:black'},
] 

table.set_table_styles(styles)

table.hide(axis="index")

def header_format(key):
    return dict(
        id="ID",
        name="人形",
        rank="星级",
        first_event="登场活动",
        first_time="登场时间",
        last_event="最近打捞活动",
        last_time="结束时间"
    )[key]
table.format_index(header_format,axis=1)

def lasttime_format(last_time):
    retstr = last_time.strftime('%Y-%m-%d') if last_time<dmax else '常驻'
    delta = deltaday(today,last_time)
    retstr += f' {delta:>4d}天前' if delta > 0 else ' 当前可捞'
    retstr=re.sub(' ','&ensp;',retstr)
    return retstr
table.format(lasttime_format,subset='last_time')

table.set_caption(f'更新时间:{today.strftime("%Y-%m-%d")}').set_table_styles([{
     'selector': 'caption',
     'props': 'caption-side: bottom;'
 }], overwrite=False)

rank2color=lambda _,rank: [f'color:{color[r-1]}' for r in rank]
table.apply(rank2color, subset=['rank','name'], rank=df['rank'])

date2color=lambda _,date: [f'color:{color[min((deltaday(today,d)+99)//100,5)]}'for d in date]
table.apply(date2color, subset=['last_event','last_time'],date=df['last_time'])

with open('rescue.html','w',encoding='utf-8') as f:
    f.write(table.to_html())

# %%
