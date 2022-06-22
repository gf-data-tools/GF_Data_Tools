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
        delta='',
    )
    rows.append(row)
df = pd.DataFrame(rows)

table = df.style
styles = [
    {'selector': '','props': 'margin-left: auto; margin-right: auto; text-align: center;padding: 0.5em 1em;width:72em'},
    {'selector': 'th,td','props': 'padding: 0.5em 1em;'},
    {'selector': 'thead','props': 'background-color: #EEE; color: #333;display: block;'},
    {'selector': 'tbody','props': 'color: white;display: block;overflow: auto;width: 100%;height: 90vh;'},
    {'selector': 'tbody tr:nth-child(even)','props': 'background-color: #222'},
    {'selector': 'tbody tr:nth-child(odd)','props': 'background-color: #444'},
    {'selector': 'tbody tr:hover','props': 'background-color:#666'},
    {'selector': 'caption','props':'color:black;text-align: right;'},
] 
width = [
    {'selector': f'td:nth-child({c+1}),th:nth-child({c+1})','props':f'width: {w}em;'} for c,w in enumerate([2,8,3,8,6,8,6,10])
]
table.set_table_styles(styles+width)

table.hide(axis="index")

def header_format(key):
    return dict(
        id="ID",
        name="人形",
        rank="星级",
        first_event="登场活动",
        first_time="登场时间",
        last_event="最近打捞活动",
        last_time="结束时间",
        delta="距今"
    )[key]
table.format_index(header_format,axis=1)

html_string = '''
{table}
<script>
var now = new Date().getTime()
var daymax = new Date("2030-01-01").getTime()
var colors = ["magenta","white","cyan","limegreen","yellow","red"]
var col0s = document.getElementsByClassName("data col0")
var col1s = document.getElementsByClassName("data col1")
var col2s = document.getElementsByClassName("data col2")
var col5s = document.getElementsByClassName("data col5")
var col6s = document.getElementsByClassName("data col6")
var col7s = document.getElementsByClassName("data col7")
for (let i=0; i < col6s.length; i++) {{
    var rank_color = colors[col2s[i].textContent-1]
    col0s[i].style.color=rank_color
    col1s[i].style.color=rank_color
    col2s[i].style.color=rank_color
    var last = new Date(col6s[i].textContent).getTime()
    var days = Math.floor((now-last) / (1000 * 60 * 60 * 24));
    if(last==daymax) col6s[i].textContent = "常驻"
    console.log(last-daymax,col6s[i].textContent)
    if (days <= 0) col7s[i].textContent="当前可捞"
    else col7s[i].textContent=days+"天前"
    var day_color = colors[Math.max(0,Math.min(Math.floor((days+89)/90),5))]
    col5s[i].style.color=day_color
    col6s[i].style.color=day_color
    col7s[i].style.color=day_color
}}
</script>
'''

with open('rescue.html','w',encoding='utf-8') as f:
    f.write(html_string.format(table=table.to_html()))
df.to_csv('rescue.csv')

# %%
