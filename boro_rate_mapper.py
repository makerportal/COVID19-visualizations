#######################################
# Mapping NYC COVID-19 Borough Data
#######################################
#
#
import numpy as np
import matplotlib.pyplot as plt
import requests,datetime,os
from mpl_toolkits.basemap import Basemap
from matplotlib.patches import Polygon
from matplotlib.collections import PatchCollection
from osgeo import ogr

plt.style.use('ggplot') # ggplot formatting

def basemapper(): #geographic plotting routine
    fig,ax = plt.subplots(figsize=(14,10))
    m = Basemap(llcrnrlon=bbox[0],llcrnrlat=bbox[1],urcrnrlon=bbox[2],
               urcrnrlat=bbox[3],resolution='h', projection='cyl') # cylindrical projection ('merc' also works here)
    shpe = m.readshapefile(shapefile.replace('.shp',''),'curr_shapefile')
    m.drawmapboundary(fill_color='#bdd5d5') # map color
    m.fillcontinents(color=plt.cm.tab20c(17)) # continent color
    m.drawcounties(color='k',zorder=999)
    parallels = np.linspace(bbox[1],bbox[3],5) # latitudes
    m.drawparallels(parallels,labels=[True,False,False,False],fontsize=12,linewidth=0.25)
    meridians = np.linspace(bbox[0],bbox[2],5) # longitudes
    m.drawmeridians(meridians,labels=[False,False,False,True],fontsize=12,linewidth=0.25)
    return fig,ax,m

# COVID-19 Datasets
github_url = 'https://raw.githubusercontent.com/nychealth/coronavirus-data/master/' # nyc data repository
data_file_urls = ['boro.csv','by-age.csv','by-sex.csv','case-hosp-death.csv',
                  'summary.csv','tests-by-zcta.csv'] # the .csv files to read where data exists

# shapefiles and geographic information
# nyc borough shapefile: https://data.cityofnewyork.us/api/geospatial/tqmj-j8zm?method=export&format=Shapefile
shapefile_folder = './Borough Boundaries/' # location of city shapefile (locally)
shapefile = shapefile_folder+os.listdir(shapefile_folder)[0].split('.')[0]+'.shp'
drv    = ogr.GetDriverByName('ESRI Shapefile') # define shapefile driver
ds_in  = drv.Open(shapefile,0) # open shapefile
lyr_in = ds_in.GetLayer() # grab layer
shp = lyr_in.GetExtent() # shapefile boundary
zoom = 0.01 # zooming out or in of the shapefile bounds
bbox = [shp[0]-zoom,shp[2]-zoom,shp[1]+zoom,shp[3]+zoom] # bounding box for plotting
fig,ax,m = basemapper() #handler for plotting geographic data

# read borough data file first and plot
r = requests.get(github_url+data_file_urls[0])
txt = r.content.decode('utf-8-sig').split('\r\n') # this vector contains all the data
header = txt[0].split(',')

header_to_plot = 2 # 2 = case rate per 100,000, 1 = case count 

boroughs = np.unique([ii['boro_name'] for ii in m.curr_shapefile_info]) # borough vector from shapefile
boro_data,counts,rates = {},[],[]
for ii,boro in zip(range(1,len(txt)-1),boroughs):
    curr_data = txt[ii].split(',')
    if boro.lower()==((curr_data[0]).lower()).replace('the ',''): # matching borough to data
        print(txt[ii].split(',')[0]+' - {0}: {1:2.0f}, {2}: {3:2.2f}'.\
              format(header[1],float(curr_data[1]),header[2],float(curr_data[2])))
        boro_data[boro.lower()+'_'+header[1]] = float(curr_data[1])
        boro_data[boro.lower()+'_'+header[2]] = float(curr_data[2])
        counts.append(float(curr_data[1]))
        rates.append(float(curr_data[2]))

data_array = [counts,rates]
legend_str = ['',' (per 100,000)']
patches,patch_colors,patches_for_legend = [],{},[] # for coloring boroughs
for info, shape in zip(m.curr_shapefile_info, m.curr_shapefile):
    if info['boro_name'] in patch_colors.keys():
        pass
    else:
        patch_colors[info['boro_name']] = plt.cm.Reds(np.interp(boro_data[info['boro_name'].lower()+'_'+header[header_to_plot]],
                                                                  [np.min(data_array[header_to_plot-1]),
                                                                   np.max(data_array[header_to_plot-1])],[0,1]))
        patches_for_legend.append(Polygon(np.array(shape), True, color=patch_colors[info['boro_name']],
                                          label=info['boro_name']+': '+str(boro_data[info['boro_name'].lower()+'_'+header[header_to_plot]])))
        
    patches.append(Polygon(np.array(shape), True, color=patch_colors[info['boro_name']])) # coloring the boroughs
    
pc = PatchCollection(patches, match_original=True, edgecolor='k', linewidths=1., zorder=2)
ax.add_collection(pc)
leg1 = ax.legend(handles=patches_for_legend,title=header[header_to_plot].replace('_',' ').\
          lower().title()+legend_str[header_to_plot-1],fontsize=16,framealpha=0.95)
# textbox showing the date the data was processed
txtbox = ax.text(0.0, 0.025, 'Computed on '+datetime.datetime.now().strftime('%b %d, %Y %H:%M'), transform=ax.transAxes, fontsize=14,
        verticalalignment='center', bbox=dict(boxstyle='round', facecolor='w',alpha=0.5)) 
txtbox.set_x(1.0-(txtbox.figure.bbox.bounds[2]-(txtbox.clipbox.bounds[2]-txtbox.clipbox.bounds[0]))/txtbox.figure.bbox.bounds[2])
fig.savefig(header[header_to_plot]+'_spatial_plot.png',dpi=300)
plt.show()
