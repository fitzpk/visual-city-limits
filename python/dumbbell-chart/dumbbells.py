import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.font_manager as font_manager
import os

dir_path = os.path.dirname(os.path.realpath(__file__))
source = pd.read_excel(dir_path+'/standings.xlsx',
                     sheet_name="Standings",dtype=str)

source['League Standing'] = source['League Standing'].astype(int)
source = source.sort_values(by=['League Standing','Season'],ascending=[True,False])

# Setup grid and figure
fig = plt.figure(constrained_layout=True,figsize=(11,8.8))
gs = fig.add_gridspec(nrows=1,ncols=1)
sns.set(rc={'axes.facecolor':'#ffffff'})

# Setup custom font
font_dirs = dir_path+'/univers-condensed-medium-5871d3fdc2110.ttf'
font_files = font_manager.findSystemFonts(fontpaths=font_dirs)
font_list = font_manager.createFontList(font_files)
font_manager.fontManager.ttflist.extend(font_list)
font_manager._rebuild()
matplotlib.rcParams['font.family'] = 'Univers Condensed'

#------------------------
# Dumbbell plot showing direct differences between this season and last season's standings

teams=[]
diffs=[]
divs=[]
this_standings=[]
last_standings=[]
# Iterate over each team and get their change in the standings
for team in source['Team'].unique():
    team_df = source[source['Team'] == team]
    this_season = team_df[team_df['Season'] == '2020-21']
    last_season = team_df[team_df['Season'] == '2019-20']
    diff = this_season['League Standing'].iat[0] - last_season['League Standing'].iat[0]
    div = this_season['Division'].iat[0]
    teams.append(team)
    diffs.append(diff)
    divs.append(div)
    this_standings.append(this_season['League Standing'].iat[0])
    last_standings.append(last_season['League Standing'].iat[0])

dumbbell = pd.DataFrame(
    {'Team':teams,
     'Difference':diffs,
     'Division': divs,
     '2020-21 Standing':this_standings,
     '2019-20 Standing':last_standings,
    })


# Sort by difference, then reset index twice to get a sequential number column based on this new order that acts as the y axis field
dumbbell = dumbbell.sort_values(by=['Division','Difference'],ascending=[True,False])

# Use this sort if you want to ignore the division and just sort difference
#dumbbell = dumbbell.sort_values(by=['Difference'],ascending=[False])

dumbbell = dumbbell.reset_index().reset_index()

ytlabels = list(dumbbell['Team'].unique())
ytickers = []
for n in range(0,31):
    ytickers.append(n)

fig_ax0 = fig.add_subplot(gs[0, 0])
sns.scatterplot(data=dumbbell, x='2019-20 Standing', y='level_0', alpha=1, s=50, hue=1, palette=['#095c79'], label='2019-20', ax=fig_ax0, linewidth=1.5)
sns.scatterplot(data=dumbbell, x='2020-21 Standing', y='level_0', alpha=1, s=100, hue=1, palette=['#6ba777'], label='2020-21', ax=fig_ax0, linewidth=1.5)
fig_ax0.set(ylabel='',yticklabels=ytlabels,yticks=ytickers,xlabel='League Standing',xticks=[1,5,10,15,20,25,30],xticklabels=['1st','5th','10th','15th','20th','25th','30th'])
fig_ax0.grid(axis='y',color='#f7f3f3')
fig_ax0.tick_params(axis='y', which='both', labelsize=9)

# Add a background behind the yticks to indicate the division they are in
season_2020_21 = source[source['Season'] == '2020-21']
div_colours = dict(zip(season_2020_21['Division'].unique(),['#b48484','#838db4','#7eac96','#b8a66d']))
for tick in fig_ax0.get_yticklabels():
    tick.set_backgroundcolor('#095c79')
    txt = tick.get_text()
    team = season_2020_21[season_2020_21['Team'] == txt]
    div = team['Division'].iat[0]
    colour = div_colours.get(div)
    tick.set_bbox(dict(facecolor=colour, edgecolor=None, linewidth=2, alpha=0.4))


# Legend items were duplicating so here we keep only the legend handles we want
legend_items = [fig_ax0.get_legend_handles_labels()[0][0],fig_ax0.get_legend_handles_labels()[0][2]]
legend_labels = [fig_ax0.get_legend_handles_labels()[1][0],fig_ax0.get_legend_handles_labels()[1][2]]
fig_ax0.legend(handles=legend_items,labels=legend_labels,ncol=1, framealpha=0.4, fontsize=8)


# Add lines with appropriate arrows
for index,row in dumbbell.iterrows():
    diff = row['Difference']

    # Change settings depending on increase/decrease
    if diff < 0:
        x = row['2020-21 Standing']
        xtext = row['2019-20 Standing']
        arr_style = '->'
        label_offset_start = row['2020-21 Standing'] - 0.7
        label_offset_new = row['2019-20 Standing'] + 0.7
        label='+'+str(abs(diff))
    elif diff > 0:
        x = row['2020-21 Standing']
        xtext = row['2019-20 Standing']
        arr_style = '<-'
        label_offset_start = row['2020-21 Standing'] + 0.7
        label_offset_new = row['2019-20 Standing'] - 0.7
        label='-'+str(abs(diff))
    else:
        # When it's zero doesn't matter what x and xtext we pick
        x = row['2020-21 Standing']
        xtext = row['2019-20 Standing']
        arr_style = '<-'
        label_offset_start = row['2020-21 Standing'] + 0.7
        label_offset_new = row['2019-20 Standing'] - 0.7
        label=diff

    # Lines with arrows
    fig_ax0.annotate(
        '',
        xy=(row['2020-21 Standing'], index),
        xycoords='data',
        xytext=(row['2019-20 Standing'],index),
        textcoords='data',
        va='center',
        ha='center',
        fontsize=10,
        fontweight='bold',
        color='#d3a14f',
        arrowprops=dict(arrowstyle='->',color='#757575',visible=True,shrinkA=5,shrinkB=5)
    )

    
    # dot labels for starting year
    fig_ax0.annotate(
        row['2020-21 Standing'],
        xy=(row['2020-21 Standing'], index),
        xycoords='data',
        xytext=(label_offset_start,index),
        textcoords='data',
        va='center',
        ha='center',
        fontsize=10,
        fontweight='bold',
        color='#6ba777'
    )
    
    # dot labels most recent year
    fig_ax0.annotate(
        row['2019-20 Standing'],
        xy=(row['2019-20 Standing'], index),
        xycoords='data',
        xytext=(label_offset_new,index),
        textcoords='data',
        va='center',
        ha='center',
        fontsize=10,
        fontweight='bold',
        color='#095c79'
    )
    
    # difference labels in the middle of line
    if abs(diff)<3:
        y_offset = -0.65
        x_offset = 1.0
    else:
        y_offset = 0
        x_offset = 0

    # Calculate the average to get the mid-point of the arrow line
    x_value = (row['2019-20 Standing']+row['2020-21 Standing'])/2

    # For the very first team in the chart add a note to the middle label indicating what it represents
    if index == 30:
        label = label+'\n'+'Standing Change'
    
    fig_ax0.annotate(
        label,
        xy=(x_value, index),
        xycoords='data',
        xytext=(x_value+x_offset, index+y_offset),
        textcoords=('data'),
        va='center',
        ha='center',
        fontsize=7,
        fontweight='bold',
        color='#838383',
        bbox=dict(boxstyle="round",ec='white',fc='white',alpha=1),
        arrowprops=dict(arrowstyle='-',color='#d6d6d6',visible=True,
                        connectionstyle='angle3,angleA=0,angleB=90'),
    )
    
        

# Add title and sub-title to figure
fig.suptitle('Changes in NHL Team League Standings',y=0.96,fontweight='bold')
plt.text(0.5, 0.92, '2019-20 to 2020-21 Season', size=10, ha="center", va="center", fontweight='normal',
         transform = fig.transFigure,
         bbox=dict(boxstyle="round",ec='white',fc='white',alpha=0))

# Create custom texts to indicate the division breakdown
plt.text(0.05, 0.75, 'Scotia North', size=10, ha="center", va="center", fontweight='normal',
         transform = fig.transFigure, color='#b8a66d',
         bbox=dict(boxstyle="round",ec='white',fc='white',alpha=0))

plt.text(0.05, 0.57, 'MassMutual East', size=10, ha="center", va="center", fontweight='normal',
         transform = fig.transFigure, color='#7eac96',
         bbox=dict(boxstyle="round",ec='white',fc='white',alpha=0))

plt.text(0.05, 0.385, 'Honda West', size=10, ha="center", va="center", fontweight='normal',
         transform = fig.transFigure, color='#b48484',
         bbox=dict(boxstyle="round",ec='white',fc='white',alpha=0))

plt.text(0.05, 0.2, 'Discover Central', size=10, ha="center", va="center", fontweight='normal',
         transform = fig.transFigure, color='#838db4',
         bbox=dict(boxstyle="round",ec='white',fc='white',alpha=0))

# Add logo to figure
logo = plt.imread(dir_path+'/nhl-logo.png')
plt.figimage(logo, 60, 1625, zorder=2)

# Adjust subplots and save figure to png
plt.subplots_adjust(left=0.16, right=0.92, top=0.88, bottom=0.07, wspace=0.20, hspace=0.20)
plt.savefig('dumbbells_output.png')
plt.show()


    






