#######################################
# Mapping NYC COVID-19 Zip Code Data
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
    m.fillcontinents(color=plt.cm.tab20c(19)) # continent color
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
# nyc zip code shapefile: https://data.cityofnewyork.us/Business/Zip-Code-Boundaries/i8iw-xf4u
shapefile_folder = './ZIP_CODE_040114/' # location of city shapefile (locally)
shapefile = shapefile_folder+os.listdir(shapefile_folder)[0].split('_correct_CRS')[0]+'_correct_CRS.shp'
drv    = ogr.GetDriverByName('ESRI Shapefile') # define shapefile driver
ds_in  = drv.Open(shapefile,0) # open shapefile
lyr_in = ds_in.GetLayer() # grab layer
shp = lyr_in.GetExtent() # shapefile boundary
zoom = 0.01 # zooming out or in of the shapefile bounds
bbox = [shp[0]-zoom,shp[2]-zoom,shp[1]+zoom,shp[3]+zoom] # bounding box for plotting
fig,ax,m = basemapper() #handler for plotting geographic data

fig.canvas.draw() # draw to get transform data
transf = ax.transData.inverted() # for labeling
shape_areas = [ii['AREA'] for ii in m.curr_shapefile_info] # for shrinking text size in zip codes

# read borough data file first and plot
r = requests.get(github_url+data_file_urls[5]) # request the zipcode data
txt = r.content.decode('utf-8-sig').split('\r\n') # this vector contains all the data
header = txt[0].split(',') # get file header info

zipcodes = [data_row.split(',')[0] for data_row in txt[3:]] # zip codes
zipcode_pos = [float(data_row.split(',')[1]) for data_row in txt[3:]] # positive cases
zipcode_tot = [float(data_row.split(',')[2]) for data_row in txt[3:]] # total tested
zipcode_perc = [float(data_row.split(',')[3]) for data_row in txt[3:]] # percent (division of the two above * 100)

data_array = [zipcode_pos,zipcode_tot,zipcode_perc]
data_titles = ['Positive Cases','Total Tested','Percent Testing Positive']
data_indx = 2 # select which data to plot
data_range = [np.min(data_array[data_indx]),np.max(data_array[data_indx])] # for colormapping

# color schemes
cmap_sel = plt.cm.BuPu # selected colormap for visualizations
txt_color = 'w' # color of zipcode text
shape_edge_colors = 'k' # color of edges of shapes
NA_color = 'w' # color of zip codes without data

match_array,patches,patches_NA,color_array,txt_array = [],[],[],[],[]
for info,shape in zip(m.curr_shapefile_info,m.curr_shapefile):
    if info['POPULATION']==0.0: # if no population, color the shape white
        patches_NA.append(Polygon(np.array(shape), True, color=NA_color,label='')) # coloring the boroughs
        continue
    if info['ZIPCODE'] in zipcodes:
        # first find where the data matches with shapefile
        zip_indx = [ii for ii in range(0,len(zipcodes)) if info['ZIPCODE']==zipcodes[ii]][0]
        zip_data = data_array[data_indx][zip_indx]
        color_val = np.interp(zip_data,data_range,[0.0,1.0]) # data value mapped to unique color in colormap
        c_map = cmap_sel(color_val) # colormap to use
        
        if info['ZIPCODE'] in match_array:
            # check if we've already labelled this zip code (some repeat for islands, parks, etc.)
            patches.append(Polygon(np.array(shape), True, color=c_map)) 
        else:
            # this is the big data + annotation loop
            match_array.append(info['ZIPCODE'])
            patches.append(Polygon(np.array(shape), True, color=c_map)) # coloring the boroughs to colormap
            
            x_pts = [ii[0] for ii in shape] # get the x pts from the shapefile
            y_pts = [ii[1] for ii in shape] # get the y pts from the shapefile

            x_pts_centroid = [np.min(x_pts),np.min(x_pts),np.max(x_pts),np.max(x_pts)] # x-centroid for label
            y_pts_centroid = [np.min(y_pts),np.max(y_pts),np.min(y_pts),np.max(y_pts)] # y-centroid for label
            
            # calculate eigenvectors from covariance to get rough rotation of each zip code
            evals,evecs = np.linalg.eigh(np.cov(x_pts,y_pts))
            rot_vec = np.matmul(evecs.T,[x_pts,y_pts]) # multiply by inverse of cov matrix
            angle = (np.arctan(evecs[0][1]/evecs[0][0])*180.0)/np.pi # calculate angle using arctan
            angle-=90.0
            # make sure the rotation of the text isn't upside-down
            if angle<-90.0:
                angle+=180.0
            elif angle>90.0:
                angle-=180.0
            
            if angle<-45.0:
                angle+=90.0
            elif angle>45.0:
                angle-=90.0
            
            # this is the zipcode label, shrunken based on the area of the zip code shape
            txtbox = ax.text(np.mean(x_pts_centroid),np.mean(y_pts_centroid), info['ZIPCODE'], ha='center',
                              va = 'center',fontsize=np.interp(info['AREA'],np.sort(shape_areas)[::int(len(np.sort(shape_areas))/4.0)],
                                                               [1.0,2.0,4.0,5.0]),
                             rotation=angle, rotation_mode='anchor',color=txt_color,bbox=dict(boxstyle="round",ec=c_map,fc=c_map))
            
            # this bit ensures no labels overlap or obscure other labels
            trans_bounds = (txtbox.get_window_extent(renderer = fig.canvas.renderer)).transformed(transf)
            for tbox in txt_array:
                tbounds = (tbox.get_window_extent(renderer = fig.canvas.renderer)).transformed(transf)
                loops = 0
                while trans_bounds.contains(tbounds.x0,tbounds.y0) or trans_bounds.contains(tbounds.x1,tbounds.y1) or\
                        tbounds.contains(trans_bounds.x0,trans_bounds.y0) or tbounds.contains(trans_bounds.x1,trans_bounds.y1) or\
                trans_bounds.contains(tbounds.x0+((tbounds.x0+tbounds.x1)/2.0),tbounds.y0+((tbounds.y0+tbounds.y1)/2.0)) or \
                trans_bounds.contains(tbounds.x0-((tbounds.x0+tbounds.x1)/2.0),tbounds.y0-((tbounds.y0+tbounds.y1)/2.0)) or \
                trans_bounds.contains(tbounds.x0+((tbounds.x0+tbounds.x1)/2.0),tbounds.y0-((tbounds.y0+tbounds.y1)/2.0)) or\
                trans_bounds.contains(tbounds.x0-((tbounds.x0+tbounds.x1)/2.0),tbounds.y0+((tbounds.y0+tbounds.y1)/2.0)):
                    txtbox.set_size(txtbox.get_size()-1.0)
                    tbox.set_size(tbox.get_size()-1.0)
                    trans_bounds = (txtbox.get_window_extent(renderer = fig.canvas.renderer)).transformed(transf)
                    tbounds = (tbox.get_window_extent(renderer = fig.canvas.renderer)).transformed(transf)
                    loops+=1
                    if loops>10:
                        break
            
            txt_array.append(txtbox)
            if len(txt_array) % 10 == 0:
                print('{0:2.0f} % Finished'.format(100.0*(len(txt_array)/len(zipcodes))))
            
    else:
        patches_NA.append(Polygon(np.array(shape), True, color=NA_color,label='')) # coloring the shapes that don't have data white (parks, etc.)

# adding the shapes and labels to the figure
pc = PatchCollection(patches, match_original=True, edgecolor=shape_edge_colors, linewidths=1., zorder=2,cmap=cmap_sel)
pc_NA = PatchCollection(patches_NA, match_original=True, edgecolor=shape_edge_colors, linewidths=1., zorder=2)
ax.add_collection(pc)
ax.add_collection(pc_NA)
    
pc.set_clim(data_range) # set the colorbar bounds
cb = plt.colorbar(pc,shrink=0.75) # shrink the colorbar a little
cb.set_label(data_titles[data_indx],fontsize=18,labelpad=10) # set the label

leg1 = ax.legend(handles=[patches_NA[-1]],title='No Data',
                 fontsize=16,framealpha=0.95,loc='upper left') # add legend to describe NA-values

# textbox showing the date the data was processed
txtbox = ax.text(0.0, 0.025, 'Computed on '+datetime.datetime.now().strftime('%b %d, %Y %H:%M'), transform=ax.transAxes, fontsize=14,
        verticalalignment='center', bbox=dict(boxstyle='round', facecolor='w',alpha=0.5)) 
txtbox.set_x(1.1-(txtbox.figure.bbox.bounds[2]-(txtbox.clipbox.bounds[2]-txtbox.clipbox.bounds[0]))/txtbox.figure.bbox.bounds[2])
plt.show()
