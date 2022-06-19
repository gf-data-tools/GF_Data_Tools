import pandas as pd
import plotly.express as px

import os
from pathlib import Path
os.chdir(Path(__file__).resolve().parent)

df = []

with open('doll_obtain_info.tsv','r') as f:
    for line in f.readlines():
        info = line.strip().split('\t')
        event, begin, end = info[:3]
        guns = info[3:]
        if end=='300101':
            end='220530'
        for gun in guns:
            df.append(dict(Gun=gun, Start=f'20{begin[:2]}-{begin[2:4]}-{begin[4:6]}', Finish=f'20{end[:2]}-{end[2:4]}-{end[4:6]}', Event=f'{event}-{gun}'))

fig = px.timeline(df, x_start="Start", x_end="Finish", y="Event", color="Gun")
fig.write_html("result.html")