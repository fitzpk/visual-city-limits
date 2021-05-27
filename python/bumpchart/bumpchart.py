import pandas as pd
import numpy as np
import os
#import warnings
#warnings.filterwarnings("ignore")
import seaborn as sns
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.font_manager as font_manager
import matplotlib.patheffects as pe
from matplotlib import rcParams

# Read in data
dir_path = os.path.dirname(os.path.realpath(__file__))
source = pd.read_excel(dir_path+'/QS_Subject_rankings.xlsx',
                     sheet_name="Canadian Schools",dtype=str)
print("Finished reading in data")

# Change the type of specific columns
source['Final Rank'] = source['Final Rank'].astype(int)
source['Year'] = source['Year'].astype(int)

# Isolate one subject of interest
subject = source[(source['Subject'] == 'Engineering Technology')]

# Setup figure and grid
sns.set(rc={'axes.facecolor':'#ffffff'})
fig = plt.figure(constrained_layout=True,figsize=(10,7))
gs = fig.add_gridspec(1, 1)

# Setup custom font
font_dirs = dir_path+'/univers-condensed-medium-5871d3fdc2110.ttf'
font_files = font_manager.findSystemFonts(fontpaths=font_dirs)
font_list = font_manager.createFontList(font_files)
font_manager.fontManager.ttflist.extend(font_list)
font_manager._rebuild()
matplotlib.rcParams['font.family'] = 'Univers Condensed'

# Sort data by year, rank in canada, and institution name
ca_ranks = subject.sort_values(by=['Year','Final Rank','Institution'],ascending=[True,True,True])

# Multiply to by -1 so that top institution is at the top of our graph (many ways to achieve the same result)
ca_ranks['Bump Rank'] = ca_ranks['Final Rank']*-1

# Keep only schools that are in the top 10 in Canada
ca_2018 = ca_ranks[(ca_ranks['Year'] == 2018) & (ca_ranks['Final Rank'] <= 10)]
top_10_schools = ca_2018['Institution'].unique()
ca_ranks_top = ca_ranks[ca_ranks['Institution'].isin(top_10_schools)]

# Create subplot
fig_ax0 = fig.add_subplot(gs[0, 0])
palette = sns.color_palette(['white'], len(ca_ranks_top['Institution'].unique()))

# Plot twice simply for design because we want to achieve a white border around the line
kwargs={'markersize':8,'linewidth':8}
sns.lineplot(data=ca_ranks_top, x="Year", y="Bump Rank", hue='Institution', ax=fig_ax0, palette=palette, **kwargs)
kwargs={'markerfacecolor':'white','markersize':16,'markeredgewidth':1.5,'linewidth':5}
sns.lineplot(data=ca_ranks_top, x="Year", y="Bump Rank", hue='Institution', ax=fig_ax0, palette='deep', marker='o', zorder=2, **kwargs)
fig_ax0.set(ylabel='',yticks=[-10,-9,-8,-7,-6,-5,-4,-3,-2,-1],yticklabels=ca_ranks_top['Institution'].unique()[::-1],
            xticks=[2018,2019,2020],xticklabels=['2018','2019','2020'])
fig_ax0.legend_.remove()
fig_ax0.grid(linestyle='--',color='#e2e2e2')

# Change edgecolour based on school
colour_map = dict(zip(fig_ax0.lines,sns.color_palette('deep').as_hex()))
for l in fig_ax0.lines:
    c = colour_map.get(l)
    l.set_mec(c)

# Annotate ranking inside line plot marker
colour_map = dict(zip(top_10_schools,sns.color_palette('deep').as_hex()))
for x,y,z,i in zip(ca_ranks_top['Year'],ca_ranks_top['Bump Rank'],ca_ranks_top['Final Rank'],ca_ranks_top['Institution']):
    c = colour_map.get(i)
    fig_ax0.annotate(z,xy=(x,y-0.01), ha='center', va='center', textcoords='data',fontweight='bold',fontsize=10,color=c)

# Change colour of ytick labels to match lines and act as a legend
cnt=0
ycolours = sns.color_palette('deep').as_hex()[::-1]
for label in fig_ax0.get_yticklabels():
    label.set_color(ycolours[cnt])
    label.set_fontweight('bold')
    cnt+=1

# Title and sub-title
fig.suptitle('QS World University Subject Rankings',y=0.96,fontweight='bold')
plt.text(0.5, 0.92, 'Engineering Technology - 2018 to 2020', size=10, ha="center", va="center", fontweight='normal',
         transform = fig.transFigure,
         bbox=dict(boxstyle="round",ec='white',fc='white',alpha=0))

# Add logo
logo = plt.imread(dir_path+'/qs.png')
plt.figimage(logo, 60, 1240, zorder=2)

# Adjust subplot as necessary
plt.subplots_adjust(left=0.22, right=0.93, top=0.89, bottom=0.11, wspace=0.20, hspace=0.20)
plt.show()
