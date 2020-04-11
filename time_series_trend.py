##########################################
# Mapping NYC COVID-19 Time Series Data
##########################################
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
r = requests.get(github_url+data_file_urls[3])
txt = r.content.decode('utf-8-sig').split('\r\n') # this vector contains all the data

header = txt[0].split(',')
dates = [datetime.datetime.strptime(ii.split(',')[0],'%m/%d/%y') for ii in txt[1:]]

fig,axs = plt.subplots(2,1,figsize=(12,9))
cii = 0
for jj in range(1,len(txt[0].split(','))):
    vals = []
    for ii in range(0,len(txt[1:])):
        val = (txt[1:])[ii].split(',')[jj]
        if val=='':
            val = np.nan
        else:
            val = float(val)
        vals.append(val)
        
    axs[0].scatter(dates,vals,label=txt[0].split(',')[jj].replace('_',' '),color=plt.cm.tab10(cii),linewidth=3.0)    
    axs[1].plot(dates,np.nancumsum(vals),label=(txt[0].split(',')[jj]).replace('_',' ').replace('NEW','TOTAL'),
                                                                linewidth=6.0,color=plt.cm.tab10(cii),linestyle=':')
    cii+=1
    
axs[0].legend(title='New Case Counts')
axs[0].tick_params(axis='x', rotation=15)
axs[0].set_ylabel('New Count',fontsize=16)
axs[0].set_yscale('log')
axs[0].tick_params('both',labelsize=16)
axs[0].set_xticklabels([])
axs[1].legend(title='Total Case Counts')
axs[1].set_yscale('log')
axs[1].tick_params(axis='x', rotation=15)
axs[1].set_xlabel('Date [Year-Month-Day]',fontsize=18,labelpad=10)
axs[1].set_ylabel('Total Count',fontsize=18)
axs[1].tick_params('both',labelsize=16)
fig.subplots_adjust(hspace=0.1)
fig.savefig(header[0]+'_in_NYC_COVID19.png',dpi=300,facecolor='#FCFCFC')
plt.show()
