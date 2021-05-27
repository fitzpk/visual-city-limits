import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.font_manager as font_manager
import os

dir_path = os.path.dirname(os.path.realpath(__file__))
source = pd.read_excel(dir_path+'/player_stats_2020_21.xlsx',
                     sheet_name="Summary",dtype=str)

source['P'] = source['P'].astype(int)
source = source.sort_values(by=['P'],ascending=False)

# Setup grid and figure
fig = plt.figure(constrained_layout=True,figsize=(10,7))
gs = fig.add_gridspec(nrows=11,ncols=1)
sns.set(rc={'axes.facecolor':'#ffffff'})


# Setup custom font
font_dirs = dir_path+'/univers-condensed-medium-5871d3fdc2110.ttf'
font_files = font_manager.findSystemFonts(fontpaths=font_dirs)
font_list = font_manager.createFontList(font_files)
font_manager.fontManager.ttflist.extend(font_list)
font_manager._rebuild()
matplotlib.rcParams['font.family'] = 'Univers Condensed'

# Create palettes and map to a dictionary
pal=['#bf869e','#aba3d1','#6ca895','#d5ac6a']
pal_dark=['#8d3e5f','#504683','#306857','#a58551']
div_pal = dict(zip(['Scotia North','MassMutual East','Honda West','Discover Central'],pal))
div_pal_dark = dict(zip(['Scotia North','MassMutual East','Honda West','Discover Central'],pal_dark))

# Iterate through each division and generate rainclouds
row_count=0
colour_count=0
for div in source['Division'].unique():
    colo = div_pal.get(div)
    div_df = source[source['Division'] == div]

    fig_ax0 = fig.add_subplot(gs[row_count,0])
    sns.kdeplot(x=div_df['P'],fill=True,ax=fig_ax0,cut=0,color=colo)
    fig_ax0.set(ylabel='',yticklabels=[],xticklabels=[],xlabel='',xlim=[20,110])
    
    fig_ax1 = fig.add_subplot(gs[row_count+1, 0])
    sns.boxplot(x=div_df['P'],ax=fig_ax1,color=colo,boxprops=dict(alpha=0.4))
    sns.stripplot(x=div_df['P'],ax=fig_ax1,jitter=0.2,color=colo)
    if row_count == 9:
        fig_ax1.set(xlabel='Points Scored',xlim=[20,110])
    else:
        fig_ax1.set(xlabel='',xticklabels=[],xlim=[20,110])

    fig_ax1.set_ylabel(div,rotation=0,ha='right')
    fig_ax1.tick_params(axis='y',length=5)

    
    for dot,player,pos,points in zip(fig_ax1.collections[0].get_offsets(),div_df['Player'],div_df['Pos'],div_df['P']):
        colour = div_pal_dark.get(div)
        if player in ['Patrick Kane','Connor McDavid','Brad Marchand','Mikko Rantanen','Tyson Barrie','Adam Fox','Victor Hedman','Cale Makar']:
            if pos == 'D':
                note = 'Defense | '+str(points)+' points'
            else:
                note = 'Forward | '+str(points)+' points'

            # Circle to highlight specific dot
            fig_ax1.annotate(' ',xy=(dot[0],dot[1]),xycoords='data',
                             bbox=dict(boxstyle="circle,pad=-0.1", fc=colour, ec='w', lw=1))

            # Label and arrow pointing to highlighted dot
            fig_ax1.annotate(player,xy=(dot[0]+0.7,dot[1]-0.1), xycoords='data',xytext=(dot[0]+2.5,dot[1]-0.4),textcoords='data',
                             color=colour,fontsize=8,fontweight='bold',ha='left',
                             arrowprops=dict(arrowstyle = '->',color=colour,visible=True,connectionstyle='arc3,rad=0.3'),
                             bbox=dict(boxstyle="round,pad=0", fc='w', ec='w', lw=0,alpha=0))

            # Extra label info
            fig_ax1.annotate(note,xy=(dot[0]+0.7,dot[1]-0.1), xycoords='data',xytext=(dot[0]+2.5,dot[1]-0.15),textcoords='data',
                             color='w',fontsize=7,fontweight='bold',ha='left',
                             bbox=dict(boxstyle="round,pad=0.1", fc=colour, ec='w', lw=0,alpha=0.7))


    row_count+=3
    colour_count+=1

fig.suptitle('NHL Player Point Distributions by Division',y=0.96,fontweight='bold')
plt.text(0.5, 0.92, '2020-21 Season', size=10, ha="center", va="center", fontweight='normal',
         transform = fig.transFigure,
         bbox=dict(boxstyle="round",ec='white',fc='white',alpha=0))
fig_ax1.axhline(y=0.5,color='black')

logo = plt.imread(dir_path+'/nhl-logo.png')
plt.figimage(logo, 60, 1275, zorder=2)
plt.subplots_adjust(left=0.16, right=0.92, top=0.88, bottom=0.11, wspace=0.20, hspace=0.20)
plt.savefig('raincloud_output.png')
plt.show()

    
    






