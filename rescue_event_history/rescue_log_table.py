from gf_utils import stc_data
from gf_utils.stc_data import get_stc_data
import os
from pathlib import Path
import csv
import datetime
from rich.console import Console,CONSOLE_HTML_FORMAT
from rich.terminal_theme import *
from rich.table import Table,Column,box
import re

os.chdir(Path(__file__).resolve().parent)

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


now = datetime.datetime.now()
today = now.date()
rich_table = Table(
    Column('ID',justify='right'),'人形','星级','首次登场活动','首次登场时间','上次登场活动',Column('上次登场时间',justify='right'),
    box=box.ASCII,header_style='default',caption=now.strftime(r'更新时间：%Y-%m-%d %H:%M:%S'),caption_justify='left'
)
color = ['magenta','white','cyan','green','yellow','red']
rows = []
for record in rescue_log:
    last_time = record['last']['time']
    ttl = max((today-last_time).days,0)
    row = dict(
        id=record['info']['id'],
        name=record['info']['name'],
        rank=record['info']['rank'],
        first_event=record['first']['event'],
        first_time=record['first']['time'].strftime(r'%Y-%m-%d'),
        last_event=record['last']['event'],
        last_time=record['last']['time'].strftime(r'%Y-%m-%d'),
        ttl=ttl
    )
    rows.append(row)
    namestr = re.sub('·|[\u00A0]',' ',row["name"])
    rich_table.add_row(
        f'{row["id"]}',
        f'[{color[row["rank"]-1]}]{namestr}',
        f'[{color[row["rank"]-1]}]{row["rank"]}',
        f'{row["first_event"]}',
        f'{row["first_time"]}',
        f'{row["last_event"]}',
        f'[{color[min((ttl+99)//100,5)]}]{str(ttl)+"天前" if ttl>0 else "当前可捞"}',
    )

console = Console(record=True)
console.print(rich_table)

format=re.sub('font-family:','font-family:SimSUN,',CONSOLE_HTML_FORMAT)
console.save_html('rescue.html',theme=DIMMED_MONOKAI,code_format=format)

with open('record.csv','w',encoding='utf-8',newline='') as f:
    writer = csv.DictWriter(f,rows[0].keys())
    writer.writeheader()
    writer.writerows(rows)