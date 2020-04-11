##################################
# Plotting NYC COVID-19 Age Data
##################################
#
#
import numpy as np
import matplotlib.pyplot as plt
import requests,datetime,os

plt.style.use('ggplot') # ggplot formatting

# COVID-19 Datasets
github_url = 'https://raw.githubusercontent.com/nychealth/coronavirus-data/master/' # nyc data repository
data_file_urls = ['boro.csv','by-age.csv','by-sex.csv','case-hosp-death.csv',
                  'summary.csv','tests-by-zcta.csv'] # the .csv files to read where data exists

# read borough data file first and plot
r = requests.get(github_url+data_file_urls[1])
txt = r.content.decode('utf-8-sig').split('\r\n') # this vector contains all the data
header = txt[0].split(',')

fig,ax = plt.subplots(figsize=(14,9))
spacer = -0.25
for plot_indx in range(1,len(header)):
    data_to_plot,x_range = [],[]
    for jj in range(1,len(txt)-1):
        x_range.append(txt[jj].split(',')[0])
        data_to_plot.append(float(txt[jj].split(',')[plot_indx]))
    x_plot = np.arange(0,len(x_range))+spacer
    hist = ax.barh(x_plot,data_to_plot,label=header[plot_indx].replace('_',' ').title(),height=0.25,log=True)
    spacer+=0.25

ax.set_xlabel('Count per 100,000',fontsize=20)
ax.set_yticks(np.arange(0,len(x_range)))
ax.set_yticklabels(x_range)
ax.legend(fontsize=16)
ax.tick_params('both',labelsize=16)
fig.suptitle('COVID-19 in NYC by '+header[0].replace('_',' ').title(),y=0.92,fontsize=18)
# textbox showing the date the data was processed
txtbox = ax.text(0.0, 0.975, 'Computed on '+datetime.datetime.now().strftime('%b %d, %Y %H:%M'), transform=ax.transAxes, fontsize=14,
        verticalalignment='center', bbox=dict(boxstyle='round', facecolor='w',alpha=0.5)) 
txtbox.set_x(1.0-(txtbox.figure.bbox.bounds[2]-(txtbox.clipbox.bounds[2]-txtbox.clipbox.bounds[0]))/txtbox.figure.bbox.bounds[2])
fig.savefig(header[0]+'_in_nyc.png',dpi=300,facecolor='#FCFCFC',bbox_inches = 'tight')
plt.show()
