from app.services.imports import *

#%%Put all definitions here:
def sum_of_list(lst):
    return sum(lst)

def makemydir(newpath):
  try:
    os.makedirs(newpath)
  except OSError:
    pass
  # let exception propagate if we just can't
  # cd into the specified directory
  os.chdir(newpath)

def shape_selection(event, x, y, flags, param):
    # grab references to the global variables
    global ref_point, crop

    # if the left mouse button was clicked, record the starting
    # (x, y) coordinates and indicate that cropping is being performed
    if event == cv.EVENT_LBUTTONDOWN:
        ref_point = [(x, y)]

    # check to see if the left mouse button was released
    elif event == cv.EVENT_LBUTTONUP:
        # record the ending (x, y) coordinates and indicate that
        # the cropping operation is finished
        ref_point.append((x, y))

        # draw a rectangle around the region of interest
        cv.rectangle(image, ref_point[0], ref_point[1], (0, 255, 0), 4)
        cv.imshow("image", image)
        
#Add subroutines for processing wind data into wind rose (for influx data)
def speed_labels(bins, units):   
    labels = []
    for left, right in zip(bins[:-1], bins[1:]):
        if left == bins[0]:
            labels.append('calm'.format(right))
        elif np.isinf(right):
            labels.append('>{} {}'.format(left, units))
        else:
            labels.append('{} - {} {}'.format(left, right, units))

    return list(labels)

def _convert_dir(directions, N=None):
    if N is None:
        N = directions.shape[0]
    barDir = directions * np.pi/180. - np.pi/N
    barWidth = 2 * np.pi / N
    return barDir, barWidth

def wind_rose(rosedata, wind_dirs, palette=None):
    if palette is None:
        palette = seaborn.color_palette('inferno', n_colors=rosedata.shape[1])

    bar_dir, bar_width = _convert_dir(wind_dirs)

    fig, ax = plt.subplots(figsize=(10, 10), subplot_kw=dict(polar=True))
    ax.set_theta_direction('clockwise')
    ax.set_theta_zero_location('N')

    for n, (c1, c2) in enumerate(zip(rosedata.columns[:-1], rosedata.columns[1:])):
        if n == 0:
            # for first column (e.g. calm conditions), draw circle 
            ax.bar(bar_dir, rosedata[c1].values, 
                   width=bar_width,
                   color=palette[0],
                   edgecolor='none',
                   label=c1,
                   linewidth=0)

        # for all other columns, create bar chart
        ax.bar(bar_dir, rosedata[c2].values, 
               width=bar_width, 
               bottom=rosedata.cumsum(axis=1)[c1].values,
               color=palette[n+1],
               edgecolor='none',
               label=c2,
               linewidth=0)

    #leg = ax.legend(loc=(0.75, 0.95), ncol=2)
    #xtl = ax.set_xticklabels(['N', 'NE', 'E', 'SE', 'S', 'SW', 'W', 'NW'])
    return fig

#Find the most northwestern point of a list of coordinates        
def FindNWPt(x_coord,y_coord,site_bdry):
    '''x_coord and y_coord represent a list of x and y coordinate values.
    E.g. [-102.1111, -102.2222]   

    site_bdry is a shapely polygon of the site boundary    
    '''
    az_dirs=[]
    az_mod=[]
    for i in range(len(x_coord)-1):
        az12,_,_ = geod.inv(site_bdry.centroid.x,site_bdry.centroid.y,x_coord[i],y_coord[i])
        az_dirs.append(az12)
        az_mod.append(abs(az12+45)) #modify to get '0' degrees to be at 270 degrees (NW point)
    NW_pt_idx=az_mod.index(min(az_mod)) #get index 
    NWpt_x=x_coord[NW_pt_idx]
    NWpt_y=y_coord[NW_pt_idx] 
    
    return NWpt_x, NWpt_y

#Find the most southwestern point of a list of coordinates        
def FindSWPt(x_coord,y_coord,site_bdry):
    '''x_coord and y_coord represent a list of x and y coordinate values.
    E.g. [-102.1111, -102.2222]   

    site_bdry is a shapely polygon of the site boundary    
    '''
    az_dirs=[]
    az_mod=[]
    for i in range(len(x_coord)-1):
        az12,_,_ = geod.inv(site_bdry.centroid.x,site_bdry.centroid.y,x_coord[i],y_coord[i])
        az_dirs.append(az12)
        az_mod.append(abs(az12+135)) #modify to get '0' degrees to be at 220 degrees (SW point)
    SW_pt_idx=az_mod.index(min(az_mod)) #get index 
    SWpt_x=x_coord[SW_pt_idx]
    SWpt_y=y_coord[SW_pt_idx] 
    
    return SWpt_x, SWpt_y
    
#Find max site distance
def MaxSiteDist(site_bdry):
    '''
    site_bdry is a shapely polygon of the site boundary
    '''
    #get all x and y coordinates of site boundary
    x_coord,y_coord=site_bdry.exterior.coords.xy
    
    meas_dist=[]
    for i in range(len(x_coord)):
        for j in range(len(x_coord)):
            #print(i,j)
            dist_pt_temp=geod.line_length([x_coord[i],x_coord[j]],[y_coord[i],y_coord[j]])
            meas_dist.append(dist_pt_temp)
    max_val=max(meas_dist)
    
    return max_val

#Find closest point
def FindClosestPt(xcoord,ycoord,Pt_x,Pt_y,ResultPct=None,windTriID=None,windTriPct=None):
    rel_dist=[]
    for i in range(len(xcoord)):
        temp_dist=geod.line_length([Pt_x,xcoord[i]],[Pt_y,ycoord[i]])
        rel_dist.append(temp_dist)
    close_pt_idx=rel_dist.index(min(rel_dist))
    
    CP_x=xcoord[close_pt_idx]
    CP_y=ycoord[close_pt_idx]
    if windTriID is not None and windTriPct is not None and ResultPct is not None:
        CP_windID=windTriID[close_pt_idx]
        CP_windPct=windTriPct[close_pt_idx]
        CP_pct=ResultPct[close_pt_idx]
        return CP_x, CP_y, CP_pct, CP_windID, CP_windPct
    elif windTriID is None and windTriPct is None and ResultPct is not None:
        CP_pct=ResultPct[close_pt_idx]
        return CP_x, CP_y, CP_pct
    else:
        return CP_x, CP_y
    
# Function to process wind conditions for a subset of source points
def process_wind_condition(wind_subset, src_points_subset, Obs_Consideration, Detection_Len, newlist_x, newlist_y, Components_DF):
    result = []
    geod = Geod(ellps='WGS84')
    
    for index, wind in wind_subset.iterrows(): #for each index, wind condition
        pct=wind['Percentage'] #Get precentage frequency of a particular wind  condition
        #wsp=wind['Wsp_MpS'] #Get wind speed
        wTri=wind['WTri_Size'] #get size of wind polygon
        wdir=wind['Wdir']+180 #change wind from coming from to going-to-direction
        if wdir>360: #correct for great circle if greater than 360
            wdir=wdir-360
        wdir_m=wdir-(1.2*wTri)
        wdir_p=wdir+(1.2*wTri)
        #Modify wind polygon wind directions if outside of great circle values
        if wdir_m<0:
            wdir_m=wdir_m+360
        if wdir_p<0:
            wdir_p=wdir_p+360
        if wdir_m>360:
            wdir_m=wdir_m-360
        if wdir_p>360:
            wdir_p=wdir_p-360
        WTriTempVal=0
        # Process wind condition for each source point
        for src_pt in src_points_subset: #for each source point location
            WindTriVal=((index)*len(src_points_subset))+WTriTempVal
            WTriTempVal+=1 #add one value
            src_pt_weight=src_pt[4] #get source point weight
            #Calculation of wind triangle length if you are considering obstructions or not.
            if Obs_Consideration == '1': #If considering obstructions
                #Get number of Components at the site
                init_comp=list(range(len(Components_DF)))
                src_pt_comp=src_pt[2] #First identify which component the source point is in
                src_pt_geom=sh.geometry.Point(src_pt[0],src_pt[1])#Make src point a shapely point
                del init_comp[src_pt_comp] #Then you're only left with components you'd like to consider.
                
                #Measure a distance X00m away from source point, and make into a line.
                Tri_EndPt_X,Tri_EndPt_Y,_=geod.fwd(src_pt[0],src_pt[1],wdir,Detection_Len,radians=False)
                #Make line of the trajectory
                testline=LineString([(src_pt[0],src_pt[1]),(Tri_EndPt_X,Tri_EndPt_Y)])
                #Check if the trajectory line intersects.
                intersect_var=[] #This variable will be empty if no intersections with any components occur.
                for e in init_comp:
                    comp_coords3=Components_DF['ComponentCoordsLonLat'][e]
                    poly3=sh.geometry.Polygon(comp_coords3) #get polygon of a given component
                    #If no intersection or you are just comparing a line to a road:
                    val=sh.intersects(testline,poly3)
                    if val==False or Components_DF['ComponentType'][e]=='Exclusion Zone (road/no structure)':
                        continue
                    else: #e.g. if it DOES intersect with another component
                        intersect_var.append(e) #write down component number
                if len(intersect_var)==0:
                    Tri_Dist=Detection_Len
                elif len(intersect_var)>0:
                    dist_comp=[]
                    for f in intersect_var: #For each component number of intersection
                        poly4=sh.geometry.Polygon(Components_DF['ComponentCoordsLonLat'][f])
                        p1,_= nearest_points(poly4,src_pt_geom) #get closest point of component to source point
                        #Calculate distance between the polygon and source point
                        _,_,Dist_Poly=geod.inv(p1.x,p1.y,src_pt_geom.x,src_pt_geom.y) #calculate the distance between the two points
                        dist_comp.append(Dist_Poly)
                    Tri_Dist=min(dist_comp) #get the closest distance
                pass
            else: #not considering obstructions
                Tri_Dist=Detection_Len
                pass
            #Create a wind triangle
            UWLonM,UWLatM,_ = geod.fwd(src_pt[0],src_pt[1],wdir_m,Tri_Dist,radians=False)
            UWLonP,UWLatP,_ = geod.fwd(src_pt[0],src_pt[1],wdir_p,Tri_Dist,radians=False)
            wind_polygon = Polygon ([(src_pt[0],src_pt[1]), (UWLonM,UWLatM), (UWLonP,UWLatP)])
            for x_grid, y_grid in zip(newlist_x, newlist_y): #for each point in placement grid
                pt_grid = sh.geometry.Point(x_grid, y_grid) #Create point
                if pt_grid.within(wind_polygon): # if it lies within the wind triangle
                    result_WindTriID = WindTriVal
                    result_simgrid = pct * src_pt_weight
                else:
                    result_WindTriID = ''
                    result_simgrid = 0
                result.append((x_grid, y_grid, result_WindTriID, result_simgrid))
    return result

#Subroutine for refreshing percentage of graph based on using a given point on the grid
#x1_fnl,y1_fnl,wind_TriID,wind_Tripct,Result_val2,_=PctRefresh(x1_fnl,y1_fnl,wind_TriID,wind_Tripct,Result_val2,x1_fnl[0],y1_fnl[0],FigShow='Off')
def PctRefresh(xcoord,ycoord,windTriID,windTriPct,ResultPct,pt_x,pt_y, FigShow=None,DelVals=None):
    '''

    Parameters
    ----------
    xcoord : tuple
        a list of x coordinates in tuple form.
    ycoord : tuple
        a list of y coordinates in tuple form.
    windTriID : list
        the list of wind triangle IDs covered at each coordinate.
    windTriPct : list
        the list of individual wind triangle percentage likelihood covered at each coordinate.
    ResultPct : list
        the sum of all wind triangle percentages covered at each coordinate.
    pt_x : numpy float64
        the x coordinate of the point to eliminate.
    pt_y : numpy float64
        the y coordinate of the point to eliminate.
    FigShow : 'on' or false, optional
        Whether you want to see the figure of the updated percent of detection. The default is None.
    DelVals : 'on' or false, optional
        Whether you want to compile a list of deleted values.. The default is None.

    Returns
    -------
    newxcoord : tuple
        the updated x coordinates.
    newycoord : tuple
        the updated y coordinates.
    windTriID2 : list
        the updated list of wind Triangle IDs per coordinate.
    windTriPct2 : list
        the updated list of wind triangle percents per coordinate.
    ResultPct2 : list
        the updated sum of the wind triangle percents per coordinate.
    Del_Vals : TYPE
        a list of deleted values.

    '''
    Del_Vals=[]
    x_list=[i for i, j in zip(count(), xcoord) if j == pt_x]
    y_list=[i for i, j in zip(count(), ycoord) if j == pt_y]
    match_val=set(x_list) & set(y_list)
    match_val2=int(list(match_val)[0])
    #get all wind triangles covered by point
    sim_ID_Val_Used=copy.deepcopy(windTriID[match_val2]) #all wind triangle IDs covered by given point
    if DelVals=='On':
        Del_Vals.append(sim_ID_Val_Used)
    for j in range(len(xcoord)): #for each point in result grid
        #print(j,'of',len(xcoord))
        ID_List=windTriID[j] #get all wind triangle IDs covered by a given point
        both = set(ID_List).intersection(sim_ID_Val_Used) #get shared values/wind triangle IDs (NOT index positions)
        #print(len(both))
        if len(both)>0: #If they have shared values
            indices_A = [ID_List.index(x) for x in both] #get index position of points that should be eliminated (shared)
            indices_A=sorted(indices_A,reverse=True)
            for index in indices_A: #for each index value
                #print(index)
                del windTriID[j][index]
                del windTriPct[j][index]
            ResultPct[j]=round(sum(windTriPct[j]),2)
    #Sort all the lists from highest to lowest pct detection
    idx_sort=np.argsort(ResultPct)
    idx_sort=idx_sort[::-1] #reverse to sort from highest to lowest pct values
    windTriPct2=[windTriPct[i] for i in idx_sort]
    windTriID2=[windTriID[i] for i in idx_sort]
    ResultPct2=list(np.array(ResultPct)[idx_sort]) #the Result Pct
    yarray=np.array(ycoord)
    newycoord= yarray[idx_sort]
    xarray=np.array(xcoord)
    newxcoord= xarray[idx_sort]
    data = pd.DataFrame(
        {'X_val': newxcoord,
          'Y_val': newycoord,
          'Percentage':ResultPct2
        })
    data.to_csv('PctRefresh.csv')
    if FigShow=='On':
        #Plot figure
        plt.figure()
        plt.scatter(newxcoord,newycoord,s=8,c=ResultPct2,cmap='turbo')
        #plt.clim(min_graph,max_graph)
        plt.colorbar(label='Percent of Detection')
        plt.show()
    return newxcoord, newycoord, windTriID2, windTriPct2, ResultPct2, Del_Vals

#Subroutines for point locations 

#Even angle spacing
def EvenSpaceDir(Num_Dev,site_bdry,Start_X,Start_Y):
    '''
    Num_Dev=Number of devices to space by
    site_bdry=shapely polygon of site boundary
    Start_X= X coordinate of starting value
    Start_Y= Y coordinate of starting value
    '''
    Angle_Width=360/Num_Dev
    CentroidPt_bdry=site_bdry.centroid
    site_bdry_exterior=sh.get_exterior_ring(site_bdry)
    if Start_X==None:
        Start_Angle=0
    else:
        az1,_,_ = geod.inv(CentroidPt_bdry.x,CentroidPt_bdry.y,Start_X,Start_Y)
        Start_Angle=az1
    #bdry_ring=shapely.get_exterior_ring(site_bdry)
    Angle_Val=[]
    for i in range(Num_Dev):
        Angle_Val.append(int(Start_Angle+(i*Angle_Width)))

    x_val=[]
    y_val=[]
    #Draw line for each point from center
    for k in range(Num_Dev):
        x_temp,y_temp,__=geod.fwd(CentroidPt_bdry.x,CentroidPt_bdry.y,Angle_Val[k],500)
        x_val.append(x_temp)
        y_val.append(y_temp)
    
    x_int=[]
    y_int=[]
    #Find intersection between line and outer shape of boundary
    for j in range(Num_Dev):
        if j==0:
            x_int.append(Start_X)
            y_int.append(Start_Y)
        else:
            line=LineString([(CentroidPt_bdry.x,CentroidPt_bdry.y),(x_val[j],y_val[j])])
            pt=sh.intersection(line,site_bdry_exterior)
            if pt.geom_type== 'MultiPoint':
                pt=pt.geoms[0]
            x_int.append(pt.x)
            y_int.append(pt.y)

    #plt.figure()
    #plt.plot(*bdry.exterior.xy,'blue')
    #plt.plot(*site_bdry_exterior.xy,'green')
    #plt.scatter(x_int,y_int,marker='o',color='green')
    #plt.axis('equal') #Set axis as equal
    #plt.xticks([])
    #plt.yticks([])
    #plt.show()
    return x_int, y_int

#Function to rearrange polygon vertices to be closest to a given point
def rearr_poly(poly,point_x,point_y): #rearrange polygon vertices for order from a given starting point
    xx,yy=poly.exterior.coords.xy #get vertices of boundary
    CentroidPt_bdry=poly.centroid #get centroid of site boundary
    xx=xx[:-1] #eliminate last (repeated) point
    yy=yy[:-1] #eliminate last (repeated) point
    dist_to_start=[]
    for i in range(len(xx)):
        dist_pt_temp1=geod.line_length([point_x,xx[i]],[point_y,yy[i]])
        dist_to_start.append(dist_pt_temp1)
    idx_min_dist=sorted(range(len(dist_to_start)), key=lambda k: dist_to_start[k])
   
    #get the relative az. direction going from starting point to first polygon point. Make sure
    #that the point on the polygon is clockwise direction away from starting point.
    i=0
    chg_deg=-1
    while chg_deg<0:
        init_deg,_,_=geod.inv(CentroidPt_bdry.x,CentroidPt_bdry.y,point_x,point_y)
        close_deg,_,_=geod.inv(CentroidPt_bdry.x,CentroidPt_bdry.y,xx[idx_min_dist[i]],yy[idx_min_dist[i]])
        chg_deg=close_deg-init_deg
        if chg_deg<-180:
            init_deg=init_deg-360
            chg_deg=close_deg-init_deg
        i+=1
    i=i-1
    poly_start_idx=idx_min_dist[i]
   
    #Check whether polygon was drawn in clockwise or counterclockwise order
    if poly_start_idx is (len(xx)-1):
        az2_init,_,_ = geod.inv(CentroidPt_bdry.x,CentroidPt_bdry.y,xx[poly_start_idx],yy[poly_start_idx])
        az2_fnl,_,_ = geod.inv(CentroidPt_bdry.x,CentroidPt_bdry.y,xx[0],yy[0])
        chg_deg2=az2_fnl-az2_init
    else:
        az2_init,_,_ = geod.inv(CentroidPt_bdry.x,CentroidPt_bdry.y,xx[poly_start_idx],yy[poly_start_idx])
        az2_fnl,_,_ = geod.inv(CentroidPt_bdry.x,CentroidPt_bdry.y,xx[poly_start_idx+1],yy[poly_start_idx+1])
        chg_deg2=az2_fnl-az2_init
    if chg_deg2<-180:
        chg_deg2=(360+az2_fnl)-az2_init
    if chg_deg2>180:
        chg_deg2=az2_fnl+az2_init
    if (chg_deg2>0):
        #Then it is drawn clockwise
        #re-sort coordinates based on distance from closest point
        rel_idx=[]
        for i in range(len(xx)):
            rel_idx.append(i-poly_start_idx)
        coords_xx=[0]*len(xx)
        coords_yy=[0]*len(xx)
        for i in range(len(xx)):
            coords_xx[rel_idx[i]]=xx[i]
            coords_yy[rel_idx[i]]=yy[i]
    else:
        #Then it is drawn counterclockwise and you shift coords to make them clockwise
        rel_idx=[]
        for i in range(len(xx)):
            rel_idx.append(poly_start_idx-i)
        coords_xx=[0]*len(xx)
        coords_yy=[0]*len(xx)
        for i in range(len(xx)):
            coords_xx[rel_idx[i]]=xx[i]
            coords_yy[rel_idx[i]]=yy[i]
    return coords_xx, coords_yy

    #plt.figure()
    #plt.plot(*bdry.exterior.xy,'blue')
    #plt.scatter(xx[1],yy[1],marker='o',color='red')
    #plt.scatter(xx[2],yy[2],marker='o',color='green')
    #plt.scatter(coords_xx[1],coords_yy[1],marker='o',color='green')
    #plt.scatter(coords_xx[0],coords_yy[0],marker='o',color='red')
    #plt.axis('equal') #Set axis as equal
    #plt.xticks([])
    #plt.yticks([])
    #plt.show()

#Even distance spacing
def EvenDistSpacing(NumDev,site_bdry,Start_X=None,Start_Y=None):
    #get site perimeter
    xx1,yy1=site_bdry.exterior.coords.xy
    site_bdry_exterior=sh.get_exterior_ring(site_bdry)
    dist_temp_sum=[]
    for i in range(len(xx1)-1):
        dist_temp=geod.line_length([xx1[i],xx1[i+1]],[yy1[i],yy1[i+1]])
        dist_temp_sum.append(dist_temp)
    perim=sum(dist_temp_sum)    
    space=perim/NumDev #permiter devided by the number of devices
    
    #add point information to list of point coords
    pt_coords_x=[]
    pt_coords_y=[]
    
    if Start_X==None:
        point_x,point_y=FindNWPt(xx1,yy1,site_bdry)
        pt_coords_x.append(point_x)
        pt_coords_y.append(point_y)
    else:
        #It will be a point on the grid, not necessarily the boundary polygon.
        CentroidPt_bdry=site_bdry.centroid
        #bdry_ring=shapely.get_exterior_ring(site_bdry)
        az1,_,_ = geod.inv(CentroidPt_bdry.x,CentroidPt_bdry.y,Start_X,Start_Y) #get general location of point and extend it that way to polygon
        x_temp,y_temp,__=geod.fwd(Start_X,Start_Y,az1,200)
        line=LineString([(Start_X,Start_Y),(x_temp,y_temp)])
        pt=sh.intersection(line,site_bdry_exterior)
        if pt.geom_type== 'MultiPoint':
            pt=pt.geoms[0]
        point_x=pt.x
        point_y=pt.y
        pt_coords_x.append(Start_X)
        pt_coords_y.append(Start_Y)

    #add point information to list of point coords
    #pt_coords_x=[]
    #pt_coords_y=[]
    #pt_coords_x.append(point_x)
    #pt_coords_y.append(point_y)

    #Number of points in site boundary polygon
    polypts=len(site_bdry.exterior.xy[0])-1
    #Create list of indices to use
    a=list(range(0,polypts))
    a.append(0)
    for i in range(NumDev):
        if i==0:
            prevpt_x=point_x
            prevpt_y=point_y
            new_coords_xx,new_coords_yy=rearr_poly(bdry,point_x,point_y)
        else: #find 2nd and 3rd, nth pts, etc.
            dist_tot=0 #set distance between point
            remain_space=space
            for idx in range(polypts-1): #for each vertex in polygon
                j=a[idx]
                dist1=geod.line_length([prevpt_x,new_coords_xx[j]],[prevpt_y,new_coords_yy[j]]) #get distance from prev. point and next vertex
                dist_tot+=dist1
                if dist_tot<space: #if distance to vertex is less than space
                    remain_space=space-dist_tot
                    prevpt_x=new_coords_xx[j] #make vertex previous point
                    prevpt_y=new_coords_yy[j] #make vertex previous point
                else: #if distance to vertex is greater than spacing
                    az1,az2,_ = geod.inv(prevpt_x,prevpt_y,new_coords_xx[j],new_coords_yy[j])#determine forward az between two points
                    x1,y1,_ = geod.fwd(prevpt_x,prevpt_y,az1,remain_space)
                    pt_coords_x.append(x1) #This is the coordinate of the nth point
                    pt_coords_y.append(y1)
                    prevpt_x=x1 #make vertex previous point
                    prevpt_y=y1
                    a=a[idx:]
                    break #leave the j loop and move on to next device
    plt.figure()
    plt.plot(*bdry.exterior.xy,'blue')
    #plt.scatter(a[1].x,a[1].y,marker='o',color='green')
    #plt.scatter(pt1_x,pt1_y,s=20,marker='o')
    #plt.scatter(new_coords_xx[1],new_coords_yy[1],s=20,marker='*',color='purple')
    for i in range(len(pt_coords_x)):
        plt.scatter(pt_coords_x[i],pt_coords_y[i],marker='o',color='green')
    #plt.scatter(prevpt_x,prevpt_y,s=20,marker='o',color='green')
    #plt.scatter(new_coords_xx[j],new_coords_yy[j],s=40,marker='o',color='orange')
    plt.axis('equal') #Set axis as equal
    plt.xticks([])
    plt.yticks([])
    plt.show()
    return pt_coords_x, pt_coords_y

def allocate_instruments(n, P_d, P_u):
    # Initial allocation pattern based on given rules
    if n == 1:
        n_d, n_u = 1, 0
    elif n == 2:
        n_d, n_u = 2, 0
    else:
        n_d = (n + 1) // 2
        n_u = n // 2
    
    # Total perimeter
    P_t = P_d + P_u
    
    # Proportions
    proportion_d = P_d / P_t
    proportion_u = P_u / P_t
    
    # Corrected quantities
    n_d_corr = n_d * proportion_d
    n_u_corr = n_u * proportion_u
    
    # Rounding to nearest integer
    n_d_corr = round(n_d_corr)
    n_u_corr = round(n_u_corr)
    
    return n_d_corr, n_u_corr

def merge_lists(lst):
    merged = []
    
    for sublist in lst:
        new_sublist = sublist[:]
        added = False        
        for existing_sublist in merged:
            if any(num in existing_sublist for num in sublist):
                existing_sublist.extend(num for num in sublist if num not in existing_sublist)
                added = True
                break
        
        if not added:
            merged.append(new_sublist)
    
    return merged

def merge_partially_overlapping_segments(line1, line2):
    # Ensure line1 starts before or at the same point as line2
    if line1.coords[0][0] > line2.coords[0][0]:
        line1, line2 = line2, line1

    # Create a new LineString from the start of line1 to the end of line2
    merged_coords = list(line1.coords) + list(line2.coords)

    # Create the merged LineString
    merged_line = LineString(merged_coords)
    return merged_line

# def reorder_vertices_clockwise(vertices, reference_point):
#     Relative_Angles=[]
#     for idx in range(len(vertices)): #for a given vertex
#         v1=vertices[idx]
#         az_v1,_,_ = geod.inv(reference_point.x,reference_point.y,v1[0],v1[1])
#         if az_v1<0:
#             az_v1=(180+az_v1)+180
#         Relative_Angles.append(az_v1)
#     indexed_angles = list(enumerate(Relative_Angles))
#     max_change=0
#     for i in range(1, len(indexed_angles)):
#         change = abs(indexed_angles[i][1] - indexed_angles[i-1][1])
#         if change > max_change:
#             max_change = change
#     if max_change>200: #then you likely have a 360/0 issue
#         indexed_angles=[(x, y if y <= 250 else y - 360) for (x, y) in indexed_angles]
#     sorted_indices = [index for index, _ in sorted(indexed_angles, key=lambda x: x[1])]
#     rearranged_coordinates = [vertices[i] for i in sorted_indices]
    
#     return rearranged_coordinates

def reorder_vertices_clockwise(vertices, reference_point,site_bdry):
    Relative_Angles=[]
    for idx in range(len(vertices)): #for a given vertex
        v1=vertices[idx]
        az_v1,_,_ = geod.inv(reference_point.x,reference_point.y,v1[0],v1[1])
        if az_v1<0:
            az_v1=(180+az_v1)+180
        Relative_Angles.append(az_v1)
    indexed_angles = list(enumerate(Relative_Angles))
    max_change=0
    for i in range(1, len(indexed_angles)):
        change = abs(indexed_angles[i][1] - indexed_angles[i-1][1])
        if change > max_change:
            max_change = change
    if max_change>200: #then you likely have a 360/0 issue
        indexed_angles=[(x, y if y <= 250 else y - 360) for (x, y) in indexed_angles]
    sorted_indices = [index for index, _ in sorted(indexed_angles, key=lambda x: x[1])]
    rearranged_coordinates = [vertices[i] for i in sorted_indices]
    #Now we have coordinates in the right direction. But we want to make sure that the line
    #is drawn correctly. If it is, then it shouldn't be crossing the site boundary
    test_line=[]
    for i in range(len(rearranged_coordinates)):
        current_idx=i
        if i==len(rearranged_coordinates)-1:
            next_idx=0
        else:
            next_idx=i+1
        
        #find az dir between two points
        az,_,dist = geod.inv(rearranged_coordinates[current_idx][0],rearranged_coordinates[current_idx][1],rearranged_coordinates[next_idx][0],rearranged_coordinates[next_idx][1])
        #get midpoint point
        x_temp1,y_temp1,_=geod.fwd(rearranged_coordinates[current_idx][0],rearranged_coordinates[current_idx][1],az,dist/2)
        azstart=az+90
        azend=az-90
        testpt_startx,testpt_starty,_=geod.fwd(x_temp1,y_temp1,azstart,2)
        Testpt_Start=Point(testpt_startx,testpt_starty)
        testpt_endx,testpt_endy,_=geod.fwd(x_temp1,y_temp1,azend,2)
        Testpt_End=Point(testpt_endx,testpt_endy)
        testline=LineString([Testpt_Start,Testpt_End])
        perimeter=site_bdry.boundary
        if perimeter.intersects(testline):
            test_line.append(0)
        else:
            test_line.append(1)
    if 1 in test_line:
        start_index=test_line.index(1)+1 #this is the point where you want to start the loop.
        new_order = rearranged_coordinates[start_index:] + rearranged_coordinates[:start_index]
    else:
        new_order=rearranged_coordinates
    
    return new_order

def find_index(find_coord,lst):
    for j, (x, y) in enumerate(lst):
        if (x,y) == find_coord:
            init_index = j
            break
    return init_index

def test_clockwise(line,reference_point):
    line_coords=list(line.coords)
    condition=True
    for idx in range(len(line_coords)-1): #for a given vertex
        v1=line_coords[idx] 
        v2=line_coords[idx+1]
        az_v1,_,_ = geod.inv(reference_point.x,reference_point.y,v1[0],v1[1])
        az_v2,_,_ = geod.inv(reference_point.x,reference_point.y,v2[0],v2[1])
        chg_deg=az_v2-az_v1
        if chg_deg< -180:
            chg_deg=(360+az_v2)-az_v1
        if chg_deg> 180:
            chg_deg=az_v1+az_v2
        # plt.figure()
        # plt.plot(*bdry.exterior.xy,'black')
        # plt.scatter(v1[0],v1[1],marker='o',color='magenta')
        # plt.scatter(v2[0],v2[1],marker='o',color='blue')
        # plt.axis('equal') #Set axis as equal
        # plt.xticks([])
        # plt.yticks([])
        # plt.show()
        if (chg_deg>0): #then it is clockwise
            continue
        else: #then it is counter clockwise
            condition=False
            break
    return condition

def calculate_geodesic_distance(line, geod):
    coords = list(line.coords)
    total_distance = 0.0
    for i in range(len(coords) - 1):
        lon1, lat1 = coords[i]
        lon2, lat2 = coords[i + 1]
        _, _, distance = geod.inv(lon1, lat1, lon2, lat2)
        total_distance += distance
    return total_distance


#Check if two lines intersect
def check_overlap(segment1,segment2):
    coords_segment1=set(list(segment1.coords))
    coords_segment2=set(list(segment2.coords))
    matching_coordinates=coords_segment1.intersection(coords_segment2)
    if len(matching_coordinates)>0:
        overlap=True
    else:
        overlap=False
    return overlap
#Downwind Weighted Spacing

def DW_Weighted_Part1(wind_dat,site_bdry,Components_DF,xcoord,ycoord,ResultPct):
    '''
    This splits the site boundary polygon into upwind- and downwind- polygons/shapes.
    Inputs:
        -wind_dat = list of wind conditions, and associated percentages (e.g. wind_list variable)
        -site_bdry = polygon of site boundary
        -GridDF = result grid in percentage likelihood
        -SrcPts_Grid = x and y locations of source points. Used to create a weighted site center
        based on source locations.
    Outputs:
        -Search_Angle = the angle used to slice the site polygon into upwind/downwind segments
        -DW_Lines = collection of linestrings that define each DW area/peak
        -UW_Lines = collection of linestrings that define each UW area/peak
        -DW_Length = total downwind length (in meters)
        -UW_Length = total upwind length (in meters)
    '''
    grouped_data = wind_dat.groupby('Wdir')['Percentage'].sum().reset_index()
    
    # Extract wind directions and percentages
    wind_directions = grouped_data['Wdir']
    percentages = grouped_data['Percentage']

    tot_pct=sum(percentages) #total percent - calm wind conditions
    peak_val=tot_pct/len(wind_directions)*1.15

    # Find peaks in the percentage data
    peaks, _ = find_peaks(percentages, height=peak_val)  # Adjust height threshold as needed

    # Number of peaks
    #num_peaks = len(peaks)
    #print("Detected number of peaks:", num_peaks)
    
    #Plot for development
    plt.figure(figsize=(10, 6))
    plt.bar(wind_directions, percentages, color='skyblue', edgecolor='black')
    plt.plot(wind_directions[peaks], percentages[peaks], 'ro')  # Mark peaks with red dots
    plt.title('Wind Direction Distribution')
    plt.xlabel('Wind Direction (degrees)')
    plt.ylabel('Percentage')
    plt.xticks(rotation=45)
    plt.grid(True)
    plt.tight_layout()
    plt.show()
    
    Peak_Idxs=[]
    LB_Idxs=[]
    UB_Idxs=[]
    Peak_LB_Idxs=[]
    Peak_UB_Idxs=[]
    for i in range(len(peaks)): #For each peak
        #Get index of the peak
        peak_val=peaks[i]
        #Find the upper and lower bound of a given peak
        ub,ub_idxs=find_bounds(peak_val,wind_directions,percentages,'upper')
        lb,lb_idxs=find_bounds(peak_val,wind_directions,percentages,'lower')
        Peak_Idxs.append(peak_val)
        LB_Idxs.append(lb_idxs)
        UB_Idxs.append(ub_idxs)
        Peak_LB_Idxs.append(lb)
        Peak_UB_Idxs.append(ub)

    #Find percentage values of all identified peaks
    Peak_Percentages=[]
    Peak_ID=[]
    IDX=[]

    for i in range(len(peaks)): #for each peak
        #Add peak information
        Peak_Percentages.append(percentages[peaks[i]]) #add percentage of peak
        Peak_ID.append(i)
        IDX.append(peaks[i]) #add peak ID
        #Add lower bound extent information
        Peak_Percentages.append(percentages[Peak_LB_Idxs[i]]) #add percentage of peak
        Peak_ID.append(i)
        IDX.append(Peak_LB_Idxs[i]) #add lower bound extent
        #Add upper bound extent information
        Peak_Percentages.append(percentages[Peak_UB_Idxs[i]]) #add percentage of peak
        Peak_ID.append(i)
        IDX.append(Peak_UB_Idxs[i]) #add upper bound extent
        #Add LB of peak information:
        for j in range(len(LB_Idxs[i])): #for e/ index of that peak's LB index
            Peak_Percentages.append(percentages[LB_Idxs[i][j]])
            Peak_ID.append(i)
            IDX.append(LB_Idxs[i][j])
        
        for k in range(len(UB_Idxs[i])):
            Peak_Percentages.append(percentages[UB_Idxs[i][k]])
            Peak_ID.append(i)
            IDX.append(UB_Idxs[i][k])

    Peak_DF = pd.DataFrame(
        {'Peak_ID': Peak_ID,
          'Idx': IDX,
          'Percentage':Peak_Percentages
        })
    Peak_DF['Peak_ID'] = Peak_DF['Peak_ID'].astype(int)

    #Identify peak with the highest percentage, sort from highest to lowest pct
    Peak_Pct=[]
    Peak_Num=[]
    Peak_Idx=[]
    for i in range(len(peaks)):
        Peak_Num.append(i)
        Peak_Pct.append(percentages[peaks[i]])
        Peak_Idx.append(peaks[i])

    Peak_Org = pd.DataFrame(
        {'Peak_ID': Peak_Num,
          'Peak_Idx': Peak_Idx,
          'Percentage':Peak_Pct
        })
    Peak_Org=Peak_Org.sort_values(by='Percentage', ascending=False)

    StartPeak=int(Peak_Org.iloc[0]['Peak_ID'])
    StartPeakIdx=int(Peak_Org.iloc[0]['Peak_Idx'])
    StartPct=Peak_Org.iloc[0]['Percentage']

    #Make sure there are no duplicates (from overlapping curves).
    #If there are, use the one of the higher peak value.

    #Identify duplicates:
    duplicates = Peak_DF[Peak_DF.duplicated(subset=['Idx'], keep=False)]

    #Remove duplicates from lesser peaks
    if len(duplicates)>0:
        Dup_Peak_ID_Remove=[] #Peak IDs of all indices to remove
        Dup_Idx_Remove=[] #Index of all rows to remove
        #Find how many unique duplicated indices there are
        duplicate_idxs = duplicates['Idx'].unique() 
        dup_count=len(duplicate_idxs)
        for i in range(dup_count): #for each set of duplicates: 
            dupidx=duplicate_idxs[i]
            dupvals=duplicates[duplicates['Idx']==dupidx] #subset duplicate pairs
            dupvals = pd.merge(dupvals, Peak_Org, on='Peak_ID', suffixes=('', '_Peak'))
            #Get row of highest peak percentage
            max_row_index = dupvals['Percentage_Peak'].idxmax()
            #row_highest_percentage = dupvals.loc[max_row_index]
            dupvals_remove = dupvals[dupvals.index != max_row_index]
            for j in range(len(dupvals_remove)): #For all values to remove
                Dup_Peak_ID_Remove.append(dupvals_remove.iloc[j]['Peak_ID'])
                Dup_Idx_Remove.append(dupvals_remove.iloc[j]['Idx'])
        
        #Ensure all indices are in integer form
        Dup_Peak_ID_Remove = list(map(int, Dup_Peak_ID_Remove))
        Dup_Idx_Remove = list(map(int, Dup_Idx_Remove))    
        
        conditions = [
        (Peak_DF['Peak_ID'] == pid) & (Peak_DF['Idx'] == idx)
        for pid, idx in zip(Dup_Peak_ID_Remove, Dup_Idx_Remove)]
        
        combined_conditions = reduce(lambda x, y: x | y, conditions)
        
        # Subset DataFrame based on combined conditions
        Peak_DF = Peak_DF[~combined_conditions]

    SeventyPercent=.7*tot_pct #Get percentage value to reach 70% of wind variability of non-calm data
    Sum_Peak_Pct=Peak_DF['Percentage'].sum()

    #Only enter this loop if bounds of peaks exceed 70% coverage.
    if Sum_Peak_Pct>SeventyPercent:
        Used_Peaks=[StartPeak]
        Num_Used_Peaks=len(Used_Peaks)
        Peak_DF_sorted = Peak_DF.sort_values(by='Percentage', ascending=False)
        Peak_DF_sorted.reset_index(drop=True, inplace=True)
        RollingPct=StartPct
        Idx_used=[StartPeakIdx]
        #Prep for first iteration
        
        LBIdx=StartPeakIdx-1
        if LBIdx<0:
            LBIdx+=len(wind_directions)
        UBIdx=StartPeakIdx+1
        if UBIdx>len(wind_directions)-1:
            UBIdx-=len(wind_directions)
        next_val_lb=[LBIdx]
        next_val_ub=[UBIdx]
        #Remove starting peak percentage from Peak_DF
        row_index=Peak_DF_sorted[(Peak_DF_sorted['Peak_ID']==StartPeak) & (Peak_DF_sorted['Idx']==StartPeakIdx)].index
        Peak_DF_sorted.drop(row_index,inplace=True)
        Peak_DF_sorted.reset_index(drop=True)
        stuck_val=0 #make a value to check if we are stuck with non-neighboring values in the loop.
        
        #Begin Loop
        while RollingPct<SeventyPercent: #Loop and add areas until you reach 70% of wind data
            highest_next_val=Peak_DF_sorted.iloc[[0]] #take first row in Peak_DF_sorted      
            if highest_next_val['Peak_ID'].isin(Used_Peaks).any() and highest_next_val['Idx'].isin(next_val_lb).any(): #If it's in the lower bound
                row_index=Peak_DF_sorted[(Peak_DF_sorted['Peak_ID']==highest_next_val['Peak_ID'].iloc[0]) & (Peak_DF_sorted['Idx']==highest_next_val['Idx'].iloc[0])].index #find index of that value
                Peak_DF_sorted.drop(row_index,inplace=True) #drop that value
                Idx_used.append(highest_next_val['Idx'].iloc[0])
                #print(Idx_used)
                RollingPct+=highest_next_val['Percentage'].iloc[0]
                if RollingPct>=SeventyPercent:
                    break
                LBIdx=highest_next_val['Idx'].iloc[0]-1
                if LBIdx<0:
                    LBIdx+=len(wind_directions)
                next_val_lb.append(LBIdx)
                stuck_val=0
                # val=1
                # print(val)
                # print('IdxUsed',highest_next_val['Idx'].iloc[0],'LBIdx added:',LBIdx)
            elif highest_next_val['Peak_ID'].isin(Used_Peaks).any() and highest_next_val['Idx'].isin(next_val_ub).any(): #if it's in the upper bounds
                row_index=Peak_DF_sorted[(Peak_DF_sorted['Peak_ID']==highest_next_val['Peak_ID'].iloc[0]) & (Peak_DF_sorted['Idx']==highest_next_val['Idx'].iloc[0])].index #find index of that value
                Peak_DF_sorted.drop(row_index,inplace=True) #drop that value
                Idx_used.append(highest_next_val['Idx'].iloc[0])
                #print(Idx_used)
                RollingPct+=highest_next_val['Percentage'].iloc[0]
                if RollingPct>=SeventyPercent:
                    break
                UBIdx=highest_next_val['Idx'].iloc[0]+1
                if UBIdx>len(wind_directions)-1:
                    UBIdx-=len(wind_directions)
                next_val_ub.append(UBIdx)
                stuck_val=0
                # val=2
                # print(val)
                # print('IdxUsed',highest_next_val['Idx'].iloc[0],'UBIdx added:',UBIdx)
            elif not highest_next_val['Peak_ID'].isin(Used_Peaks).any(): # if the highest value is in a new peak
                Used_Peaks.append(highest_next_val['Peak_ID'].iloc[0]) #add to a used peak
                row_index=Peak_DF_sorted[(Peak_DF_sorted['Peak_ID']==highest_next_val['Peak_ID'].iloc[0]) & (Peak_DF_sorted['Idx']==highest_next_val['Idx'].iloc[0])].index
                Peak_DF_sorted.drop(row_index,inplace=True) #drop that value
                Idx_used.append(highest_next_val['Idx'].iloc[0])
                #print(Idx_used)
                RollingPct+=highest_next_val['Percentage'].iloc[0]
                if RollingPct>=SeventyPercent:
                    break
                UBIdx=highest_next_val['Idx'].iloc[0]+1
                if UBIdx>len(wind_directions)-1:
                    UBIdx-=len(wind_directions)
                LBIdx=highest_next_val['Idx'].iloc[0]-1
                if LBIdx<0:
                    LBIdx+=len(wind_directions)
                next_val_ub.append(UBIdx)
                next_val_lb.append(LBIdx)
                stuck_val=0
                #val=3
                # print(val)
                # print('IdxUsed',highest_next_val['Idx'].iloc[0])
                # print('LBIdx:',LBIdx)
                # print('UBIdx:',UBIdx)
            else: #The next highest percent value is in the existing peak, but not adjacent to any current points
                #then move index to end of dataframe (for now)
                row_index=Peak_DF_sorted[(Peak_DF_sorted['Peak_ID']==highest_next_val['Peak_ID'].iloc[0]) & (Peak_DF_sorted['Idx']==highest_next_val['Idx'].iloc[0])].index
                row_to_move = Peak_DF_sorted.loc[[row_index[0]]]
                Peak_DF_sorted.drop(index=row_index, inplace=True)
                Peak_DF_sorted = pd.concat([Peak_DF_sorted, row_to_move], ignore_index=True)
                stuck_val+=1
                #print(stuck_val)
                if stuck_val>len(wind_directions): #if you've used up all other values, take the next with highest percentage.
                    Peak_DF_sorted.sort_values(by='Percentage',ascending=False)
                    Peak_DF_sorted.reset_index(drop=True,inplace=True)
                    highest_next_val=Peak_DF_sorted.iloc[[0]]
                    row_index=Peak_DF_sorted[(Peak_DF_sorted['Peak_ID']==highest_next_val['Peak_ID'].iloc[0]) & (Peak_DF_sorted['Idx']==highest_next_val['Idx'].iloc[0])].index
                    Peak_DF_sorted.drop(row_index,inplace=True) #drop that value
                    Idx_used.append(highest_next_val['Idx'].iloc[0])
                    print('Stuck',str(Idx_used))
                    RollingPct+=highest_next_val['Percentage'].iloc[0]
                    if RollingPct>=SeventyPercent:
                        break

    else: #Expand until it reaches 70%
        Peak_Idx=sorted(IDX)
        Rolling_Pct=percentages.drop(Peak_Idx)

        while Sum_Peak_Pct<SeventyPercent: #Loop and add areas until you reach 70% of wind data
            #First get all indices +/- of the bounds
            Peak_Idx_Temp=copy.deepcopy(Peak_Idx)
            for i in range(len(Peak_Idx)):
                val=Peak_Idx[i]
                upperval=val+1
                lowerval=val-1
                if upperval>35:
                    upperval-=36
                if lowerval<0:
                    lowerval+=36
                Peak_Idx_Temp.append(upperval)
                Peak_Idx_Temp.append(lowerval)
            Peak_Idx_Temp=list(set(Peak_Idx_Temp))
            #find tehe values that have been added
            difference = [item for item in Peak_Idx_Temp if item not in Peak_Idx]
            Diff_Pct=percentages[difference]
            Diff_Pct_sorted = Diff_Pct.sort_values()
            #go through added parameters and add them one by one
            while len(Diff_Pct_sorted)>0:
                idx_to_add = Diff_Pct_sorted.index[0]
                pct_to_add=Diff_Pct_sorted.iloc[0]
                #Add this value to the rolling percentage and peaks.
                Peak_Idx.append(idx_to_add)
                Sum_Peak_Pct+=pct_to_add
                if Sum_Peak_Pct>SeventyPercent:
                    break
                Rolling_Pct=Rolling_Pct.drop(Diff_Pct_sorted.index[0])
                Diff_Pct_sorted=Diff_Pct_sorted.drop(Diff_Pct_sorted.index[0])
        Idx_used=Peak_Idx
        Num_Used_Peaks=len(peaks)
        Used_Peaks=[]
        for elem in peaks:
            Used_Peaks.append(elem)
    Num_Used_Peaks=len(Used_Peaks)
    Idx_used.sort()
    #At this point we have the number of peaks, and the indices of the directions we want.
    if Num_Used_Peaks==1 or is_continuous_circular(Idx_used,len(wind_directions)-1)[0]==True: #If you only have one peak or if direction values are continuous
        print('One Direction')
        Idx_used2=is_continuous_circular(Idx_used,len(wind_directions)-1)[1] #this is the sorted circular list
        Num_Used_Peaks=1
    else:
        _,_,num_brks,brk_idx=is_continuous_circular(Idx_used,len(wind_directions)-1)
        #create a list for each individual grouping
        Idx_used2=[]
        for i in range(num_brks+1):
            #print(i)
            if i==0:
                Idx_used2.append(Idx_used[:brk_idx[0]+1])
            elif i==num_brks:
                Idx_used2.append(Idx_used[brk_idx[i-1]+1:])
            else:
                Idx_used2.append(Idx_used[brk_idx[i-1]+1:brk_idx[i]+1])
        #chekc if some lists are continuous
        list_with_beginning = None
        list_with_end = None
        # Iterate through the nested list to find the lists containing 0 and 35
        for lst in Idx_used2:
            if 0 in lst:
                list_with_beginning = lst
            if int(len(wind_directions)-1) in lst:
                list_with_end = lst
        
        # If both lists are found, merge them
        if list_with_beginning and list_with_end:
            merged_list = list_with_beginning + list_with_end
            # Remove duplicates if necessary
            merged_list = list(set(merged_list))
        
            # Update the nested list by replacing the original lists with the merged list
            Idx_used2 = [lst for lst in Idx_used2 if lst != list_with_beginning and lst != list_with_end]
            Idx_used2.append(merged_list)
        Idx_used2 = [x for x in Idx_used2 if x != []] #remove empty lists
        Num_Used_Peaks=len(Idx_used2)
        
        if len(Idx_used2)>1: #check if anything can be merged if sufficiently close (within 10 degrees)
            combo_result = find_combinations(Idx_used2)
            if len(combo_result)>0: #If there are lists to be combined,
                while len(combo_result)>0:
                    Idx_used2[0]=Idx_used2[combo_result[0][0]]+Idx_used2[combo_result[0][1]]
                    Idx_used2.pop(combo_result[0][1])
                    combo_result = find_combinations(Idx_used2)
            Num_Used_Peaks=len(Idx_used2)

        if Num_Used_Peaks==1:
            print('One Direction')
        elif Num_Used_Peaks==2:
            print('Two Directions')
        else:
            print('3+ Directions')
    #NOTE:
    #At this point you know the number of segments (Num_Used_Peaks), you know that it covers 70% of wind conditions,
    #and you know the rage of wind direction to use (Idx_used) 
    
    #Find emission source center points.
    Center_Pts=[]
    for a in range(len(Components_DF)): #For each component
        if Components_DF['Emission_Source'][a]==True: #If the component is an emission source
            comp_coords=Components_DF['ComponentCoordsLonLat'][a] #get the lon/lat coordinates of component
            comp_poly=sh.geometry.Polygon(comp_coords) #make component polygon
            poly_center=comp_poly.centroid
            Center_Pts.append(poly_center)

    bdry_ring=sh.get_exterior_ring(site_bdry)
    intersection=[]
    Search_Angle=[]
    Middle_Angle=[]
    All_Lines=[]
    Test_MultiLine=[]

    for i in range(Num_Used_Peaks): # for each peak/direction used
        if Num_Used_Peaks==1:
            DW_range=Idx_used2
        else:
            DW_range=Idx_used2[i]
        DW_range=[x*10 for x in DW_range] #multiply idx values by 10 to get degrees of range
        #Currently the wind directions are based on where the wind is coming from. Here we want to change
        #The span to downwind directions for sensor placement
        downwind_area=[x+180 for x in DW_range]
        for j in range(len(downwind_area)):
            if downwind_area[j]>=360:
                downwind_area[j]-=360
        #don't re-sort if around north
        if any(120 <= value <= 240 for value in DW_range)==False:
            downwind_area.sort()
        #find the middle angle
        if len(downwind_area) % 2 ==0: #if it's an even number
            idx=math.ceil(len(downwind_area)/2)-1
            temp_middle=downwind_area[idx]+5 #add 5 degrees
            if temp_middle>=360:
                temp_middle-=360
            Middle_Angle.append(temp_middle)
        else: #an odd number of elements
            idx=math.ceil(len(downwind_area)/2)-1 #round up and subtract by 1 (for index)
            temp_middle=downwind_area[idx]
            Middle_Angle.append(temp_middle)
        #should be sorted in a clockwise manner.
        DW_start=downwind_area[0]
        if DW_start>360:
            DW_start-=360
        DW_end=downwind_area[-1]
        if DW_end>360:
            DW_end-=360
        Search_Angle.append([DW_start,DW_end])
        temp_middle1=DW_start+5
        if temp_middle1>=360:
            temp_middle1-=360
        temp_middle2=DW_end-5
        if temp_middle2<0:
            temp_middle2+=360

        for k in range(len(Center_Pts)): #For each equipment center point
            x_temp1,y_temp1,_=geod.fwd(Center_Pts[k].x,Center_Pts[k].y,DW_start,1000)
            x_temp2,y_temp2,_=geod.fwd(Center_Pts[k].x,Center_Pts[k].y,DW_end,1000)
            line1=LineString([(Center_Pts[k].x,Center_Pts[k].y),(x_temp1,y_temp1)])
            line2=LineString([(Center_Pts[k].x,Center_Pts[k].y),(x_temp2,y_temp2)])
            multi_line = MultiLineString([line1, line2])
            Test_MultiLine.append(multi_line)
            bdry_line = LineString(bdry_ring.coords)
            
            x_Middle,y_Middle,_=geod.fwd(Center_Pts[k].x,Center_Pts[k].y,temp_middle,1000)
            x_Middle1,y_Middle1,_=geod.fwd(Center_Pts[k].x,Center_Pts[k].y,temp_middle1,1000)
            x_Middle2,y_Middle2,_=geod.fwd(Center_Pts[k].x,Center_Pts[k].y,temp_middle2,1000)

            line_Middle=LineString([(Center_Pts[k].x,Center_Pts[k].y),(x_Middle,y_Middle)])
            line_Middle1=LineString([(Center_Pts[k].x,Center_Pts[k].y),(x_Middle1,y_Middle1)])
            line_Middle2=LineString([(Center_Pts[k].x,Center_Pts[k].y),(x_Middle2,y_Middle2)])
            pt1=sh.intersection(line1,bdry_line)
            pt2=sh.intersection(line2,bdry_line)
            intersection.append([pt1.x,pt1.y])
            intersection.append([pt2.x,pt2.y])
            split_ring = split(bdry_line, multi_line)
            
            segment = None
            for part in split_ring.geoms:
                # Check if the part contains both intersection lines
                if part.intersects(line_Middle) or part.intersects(line_Middle1) or part.intersects(line_Middle2):
                    segment = part
                    All_Lines.append(segment)
        
    #For development. Comment out when complete.
    fig, ax = plt.subplots()
    x, y = bdry_ring.xy
    plt.plot(x, y, color='blue', label='bdry_ring')
    #for pt in intersection:
    #    plt.plot(pt[0],pt[1],color='magenta',marker='o')
    for pt in Center_Pts:
        plt.plot(pt.x,pt.y,marker='o',color='red')
    # for line in Test_MultiLine:
    #     for line2 in line.geoms:
    #         x,y=line2.xy
    #         plt.plot(x, y,color='black')
    #Plot the lines in All_Lines2
    for line in All_Lines:
        x, y = line.xy
        plt.plot(x, y, color='red', linestyle='-', label='All_Lines2')
    min_x, min_y, max_x, max_y = bdry_ring.bounds
    # Set xlim and ylim to zoom into the polygon
    ax.set_xlim(min_x, max_x)
    ax.set_ylim(min_y, max_y)
    plt.show()

    All_Lines2=copy.deepcopy(All_Lines)
    idxs=list(range(len(All_Lines2)))
    #List all overlapping lines:
    for i in idxs:
        #print(i)
        if type(All_Lines2[i])==list:
            continue
        else:
            overlap_var=[]
            for j in idxs:
                if j==i:
                    overlap_var.append([[i,j],0])
                else:
                    segment1=All_Lines2[i]
                    if type(All_Lines2[j])==list:
                        overlap_var.append([[i,j],0])
                    else:
                        segment2=All_Lines2[j]
                        ask_overlap=check_overlap(segment1,segment2)
                        if ask_overlap:
                            overlap_var.append([[i,j],1]) 
                        else:
                            overlap_var.append([[i,j],0])
            #initialize an empty set to collect unique values:
            unique_values=set()
            #Iterate through each sublist:
            for sublist in overlap_var:
                #check if the second element is 1
                if sublist[1]==1:
                #then extract the first element
                    unique_values.update(sublist[0])
            #convert the set to a sorted list
            unique_values_list=list(sorted(unique_values))
            #only make modifications if there's anything to be merged.
            if len(unique_values_list)>0:
                coordinate_list=[]
                for index in unique_values_list:
                    line=All_Lines2[index]
                    coordinate_list.extend(list(line.coords))
                    #coordinate_list= a list of all coordinates in a merged line
                #now we need to remove duplicates
                unique_coordinates = []
                seen = set()
                for coord in coordinate_list:
                    if coord not in seen:
                        unique_coordinates.append(coord)
                        seen.add(coord)
                #now we have a merged line of unique coordinates.
                #Next we re-order the vertices clockwise:
                new_order=reorder_vertices_clockwise(unique_coordinates, Center_Pts[0],bdry)
                new_line=LineString(new_order)
                #now replace the new line at the index:
                All_Lines2[i]=new_line
                #lastly replace merged lines with empty list:
                unique_values_list.remove(i)
                for index2 in unique_values_list:
                    All_Lines2[index2]=[]
    #Now you have a list of merged lines. But we first need to remove all blanks.
    All_Lines2= [line for line in All_Lines2 if line]    
        
    #Now we want to make sure that the lines themselves are in clockwise order:
    StartPt=[]
    for i in range(len(All_Lines2)):
        #first extract starting point for all
        StartPt.append(All_Lines2[i].coords[0])
    #Now find the relative azimuthal direction of each
    Rel_Az=[]
    for i in range(len(StartPt)):
        RA,_,_ = geod.inv(Center_Pts[0].x,Center_Pts[0].y,StartPt[i][0],StartPt[i][1])
        if RA<0:
            RA+=360
        Rel_Az.append(RA)
    indexed_angles = list(enumerate(Rel_Az))
    sorted_indices = [index for index, _ in sorted(indexed_angles, key=lambda x: x[1])]
    All_lines_mod = [All_Lines2[idx] for idx in sorted_indices]
    All_Lines2=All_lines_mod    
    #Okay, now we have merged lines, all in clockwise order
    
    #Now we want to merge all coordinates in the boundary ring:
    Coords_bdry=sh.get_coordinates(bdry_ring).tolist()
    
    FinalCoords_bdry=Coords_bdry+intersection
    # Remove duplicates
    FinalCoords_bdry = list(set(tuple(coord) for coord in FinalCoords_bdry))
    # Convert back to list of lists
    FinalCoords_bdry = [list(coord) for coord in FinalCoords_bdry]
    
    reorder_coords=reorder_vertices_clockwise(FinalCoords_bdry, Center_Pts[0],bdry)
    #New boundary with reordered coordinates.
    new_bdry=LineString(reorder_coords)
    new_bdry_polygon=Polygon(new_bdry)

    start_coords=All_Lines2[0].coords[0]
    #reorganize polygon so it's going clockwise and starting at endpoint of first line 
    new_x,new_y=rearr_poly(new_bdry_polygon,start_coords[0],start_coords[1])
    new_bdry_coords=[[x, y] for x, y in zip(new_x, new_y)]
    new_bdry_coords.append(new_bdry_coords[0])
    new_bdry=LineString(new_bdry_coords)

    #Extract linestrings not covered in All_Lines2
    coord_doc=[]
    for i in range(len(All_Lines2)+1):
        #The first one should match up with the first line.
        #Here we grab the start/end of the first line segment,
        #eliminate points in between these lines
        #and make end of line segment the start of ones to keep
        if i==0 and new_bdry_coords[i][0]==All_Lines2[0].coords[0][0] and new_bdry_coords[i][1]==All_Lines2[0].coords[0][1]:
            idx=find_index(All_Lines2[0].coords[-1],new_bdry_coords)
            new_start=new_bdry_coords[idx]
            # Remove coordinates between start and stop index
            new_bdry_coords = new_bdry_coords[idx:]
        elif i==len(All_Lines2):
            idx_start=find_index(tuple(new_start),new_bdry_coords)
            idx_end=find_index(All_Lines2[0].coords[0],new_bdry_coords)
            contained_coords=new_bdry_coords
            coord_doc.append(LineString(new_bdry_coords))
        else:
            #The first one you want to save
            idx_start=find_index(tuple(new_start),new_bdry_coords) #find start of next line
            idx_end=find_index(All_Lines2[i].coords[0],new_bdry_coords)
            contained_coords=new_bdry_coords[idx_start:idx_end+1]
            coord_doc.append(LineString(contained_coords))
            new_start=new_bdry_coords[idx_end]
            #Remove coordinates between start and stop index
            new_bdry_coords = new_bdry_coords[idx_end:]
            #The second one you want to discard
            idx_start=find_index(tuple(new_start),new_bdry_coords) #find start of next line
            idx_end=find_index(All_Lines2[i].coords[-1],new_bdry_coords)
            new_start=new_bdry_coords[idx_end]
            new_bdry_coords = new_bdry_coords[idx_end:]
        #At this point we have two variables:
        #One (All_Lines2) includes all Downwind Weighted linestrings
        #Another (coord_doc) includes all Upwind Weighted Linestrings
    
    DW_Length = sum(calculate_geodesic_distance(line, geod) for line in All_Lines2)
    UW_Length = sum(calculate_geodesic_distance(line, geod) for line in coord_doc)
    DW_Lines=All_Lines2
    UW_Lines=coord_doc
    
    plt.figure()
    plt.plot(*bdry.exterior.xy,'black')
    for line in All_Lines2:
        x, y = line.xy
        plt.plot(x, y, color='red', linestyle='-', label='DW_Weighted')
    for line in coord_doc:
        x, y = line.xy
        plt.plot(x, y, color='blue', linestyle='-', label='UW_Weighted')
    plt.axis('equal') #Set axis as equal
    plt.xticks([])
    plt.yticks([])
    plt.show()
    
    return Search_Angle, DW_Lines, UW_Lines, DW_Length, UW_Length

def Create_Arc (Site_Center,pt1_x,pt1_y,pt2_x,pt2_y,pt_middle_x,pt_middle_y): #Create a circular arc polygon.
    endpoint1 = Point(pt1_x, pt1_y)
    endpoint2 = Point(pt2_x, pt2_y)
    # Calculate the azimuth (bearing) from the center to each endpoint and point_avg
    angle1, _, _ = geod.inv(Site_Center.x, Site_Center.y, pt1_x, pt1_y)
    angle1 %= 360
    angle2, _, _ = geod.inv(Site_Center.x, Site_Center.y, pt2_x, pt2_y)
    angle2 %= 360
    angle3, _, _ = geod.inv(Site_Center.x, Site_Center.y, pt_middle_x, pt_middle_y)
    angle3 %= 360

    # Determine the minimum and maximum angles between the center and the endpoints
    min_angle = min(angle1, angle2)
    max_angle = max(angle1, angle2)

    # Check if the angle between the center and point_avg is between min_angle and max_angle and populate angles that define the circle
    if min_angle <= angle3 <= max_angle: #if avg angle is between, then use this
        # Include the angle between the center and point_avg in the angles to iterate
        num_angles=int(max_angle-min_angle)
        angles = np.linspace(min_angle, max_angle, num_angles)
    else:
        min_angle_new=max_angle
        max_angle_new=min_angle+360
        num_angles=int(max_angle_new-min_angle_new)
        angles = np.linspace(min_angle_new,max_angle_new,num_angles)
        for i in range(len(angles)):
            if angles[i] >= 359.9:
                angles[i] -= 360

    # Calculate the coordinates of the circular arc
    arc_coords = []
    for angle in angles:
        lon, lat, _ = geod.fwd(Site_Center.x, Site_Center.y, angle, 1500)
        arc_coords.append((lon, lat))

    #Define start/endpoint for drawing the circular sector.
    if abs(angles[0]-angle1)< abs(angles[0]-angle2):
        start_point=endpoint1
        end_point=endpoint2
    else:
        start_point=endpoint2
        end_point=endpoint1

    # Append center and endpoints to the list of coordinates
    arc_coords2 = []
    arc_coords2.append((Site_Center.x, Site_Center.y))
    arc_coords2.append((start_point.x, start_point.y))
    arc_coords2.extend(arc_coords)  # Extend arc_coords2 with the contents of arc_coords
    arc_coords2.append((end_point.x, end_point.y))
    arc_coords2.append((Site_Center.x, Site_Center.y))

    # Convert to polygon
    wind_polygon = Polygon(arc_coords2)
    return wind_polygon

def Find_Angle_Difference(Az1,Az2): 
    #See if obtuse or acute. Az1=start angle, Az2=end angle
    Az1temp=Az1
    if Az1temp<0:
        Az1temp=(180+Az1temp)+180
    Az2temp=Az2
    if Az2temp<0:
        Az2temp=(180+Az2temp)+180
    angle=Az2temp-Az1temp
    if angle<0:
        angle=360+angle   
    if angle>180:
        angle_type='obtuse'
    else:
        angle_type='acute'
    return angle_type
    
#Even distance spacing
def EvenDistSpacing_LineStr(AllocateNum,LineStr):
    #find length of line segment:
    line_len=calculate_geodesic_distance(LineStr, geod)
    space=line_len/(AllocateNum+1)    
    #add point information to list of point coords
    pt_coords_x=[]
    pt_coords_y=[]
    #make sure that AllocateNum is an integer
    AllocateNum=int(AllocateNum)
    #Create list of indices to use
    a=list(range(0,len(LineStr.coords)))
    for i in range(AllocateNum+1): #for each SOOFIE to allocate
        if i==0:
            prevpt_x=LineStr.coords[0][0]
            prevpt_y=LineStr.coords[0][1]
        else: #find 2nd and 3rd pts
            dist_tot=0 #set distance between point
            remain_space=space
            for idx in range(len(LineStr.coords)): #for each vertex in LineString
                j=a[idx]
                dist1=geod.line_length([prevpt_x,LineStr.coords[j][0]],[prevpt_y,LineStr.coords[j][1]]) #get distance from prev. point and next vertex
                dist_tot+=dist1
                if dist_tot<space: #if distance to vertex is less than space
                    remain_space=space-dist_tot
                    prevpt_x=LineStr.coords[j][0] #make vertex previous point
                    prevpt_y=LineStr.coords[j][1] #make vertex previous point
                else: #if distance to vertex is greater than spacing
                    az1,_,_ = geod.inv(prevpt_x,prevpt_y,LineStr.coords[j][0],LineStr.coords[j][1])#determine forward az between two points
                    x1,y1,_ = geod.fwd(prevpt_x,prevpt_y,az1,remain_space)
                    pt_coords_x.append(x1) #This is the coordinate of the nth point
                    pt_coords_y.append(y1)
                    prevpt_x=x1 #make vertex previous point
                    prevpt_y=y1
                    a=a[idx:]
                    break #leave the j loop and move on to next device
                    
    return pt_coords_x,pt_coords_y

def DW_Weighted_Part2_EvenSpace(NumDev,DW_Lines,UW_Lines,DW_Length,UW_Length,xcoord,ycoord,ResultPct,bdry):
    import math
    '''
    Parameters
    ----------
    NumDev : integer
        Number of devices to use
    DW_Lines : list of linestrings for DW placement
        Each Linestring characterizes a DW segment.
    UW_Lines : list of linestrings for UW placement
        Each Linestring characterizes a UW segment.
    DW_Length : float
        Length (in meters) of all DW segments.
    UW_Length : float
        Length (in meters) of all UW segments.

    Returns
    -------
    None.

    '''
    #calculate proportion of total perimeter for DW vs. UW area
    DW_prop=DW_Length/(DW_Length+UW_Length)
    UW_prop=UW_Length/(DW_Length+UW_Length)
    #Calculate the number of devices for each
    n_d_init=(math.floor(NumDev/2)+1)
    n_u_init=NumDev-n_d_init
    
    #Adusted
    DW_adj=n_d_init*.5
    UW_adj=n_u_init*.5
    
    DW_Weights=DW_adj*DW_prop/0.5
    UW_Weights=UW_adj*UW_prop/0.5
    WeightTot=DW_Weights+UW_Weights
    
    DW_fract=DW_Weights/WeightTot
    UW_fract=UW_Weights/WeightTot
    
    DW_val=round(DW_fract*NumDev)
    if DW_val>NumDev:
        DW_val=NumDev
    UW_val=NumDev-DW_val
    
    #Get the number of segments for each.
    DW_segment_no=len(DW_Lines)
    UW_segment_no=len(UW_Lines)
    
    #Get site center
    Site_Center=bdry.centroid
    
    ##### DOWNWIND SEGMENT PROCESSING
    #Here we determine the number of SOOFIEs per line segment
    DW_segment_max_POD=[]
    DW_segment_length=[]
    DW_rel_segment_length=[]
    DW_Segment_Index=[]
    for i in range(DW_segment_no):
        xcoords_overlap=[]
        ycoords_overlap=[]
        PctPts_overlap=[]
        
        line1=DW_Lines[i]
        #get the length of the segment
        line1_len=calculate_geodesic_distance(line1, geod)
        DW_Segment_Index.append(i)
        DW_segment_length.append(line1_len)
        DW_rel_segment_length.append(line1_len/DW_Length)
        #get the max POD at the segment
        start_pt=line1.coords[0]
        end_pt=line1.coords[-1]
        #get azmuth from center of site to the points
        Az1,_,_ = geod.inv(Site_Center.x,Site_Center.y,start_pt[0],start_pt[1])
        Az2,_,_ = geod.inv(Site_Center.x,Site_Center.y,end_pt[0],end_pt[1])
        NewPt1_x,NewPt1_y,_=geod.fwd(Site_Center.x,Site_Center.y,Az1,1500)
        NewPt2_x,NewPt2_y,_=geod.fwd(Site_Center.x,Site_Center.y,Az2,1500)
        Az_M=Az1+5 
        Pt_M_x,Pt_M_y,_=geod.fwd(Site_Center.x,Site_Center.y,Az_M,1500)
        OverlapPoly=Create_Arc(Site_Center,NewPt1_x,NewPt1_y,NewPt2_x,NewPt2_y,Pt_M_x,Pt_M_y)
        #get x,y locations to build a large wind triangle to encompass all pts of interest:
        for n in range(len(xcoord)): #loop through all points within placement grid
            point1=sh.geometry.Point(xcoord[n],ycoord[n]) #make each coordinate in placement grid a point
            if point1.within(OverlapPoly)==True: #Check if point on grid is within these placemes to avoid
                xcoords_overlap.append(xcoord[n]) #If it is, add to the x-grid_comp_buff layer
                ycoords_overlap.append(ycoord[n])
                PctPts_overlap.append(ResultPct[n])
            else:
                continue
        DW_segment_max_POD.append(max(PctPts_overlap))
    #Here we have combined index, length of segment, max POD of segment
    DW_Line_Stat=pd.DataFrame({'Seg_idx': DW_Segment_Index,
                               'Seg_Length': DW_segment_length,
                               'RelSeg_Length': DW_rel_segment_length,
                               'SegmentMaxPOD':DW_segment_max_POD,
                               'AllocatedSensors': [0] * len(DW_Lines)})
    #Re-order based on POD
    DW_Line_Stat = DW_Line_Stat.sort_values(by='SegmentMaxPOD', ascending=False)
    
    if DW_val<len(DW_Lines): #if you have fewer SOOFIEs to allocate than there are segments:
        idx=DW_val
    else:
        idx=len(DW_Lines)
    #iteratively add the first n SOOFIEs (e.g. prioritize adding one SOOFIE per segment)
    for i in range(idx): #for each SOOFIE to allocate
        DW_Line_Stat.at[i,'AllocatedSensors']+=1 #add a sensor first.
    #Get index, length of segment, max POD of segment, and total # of soofies to allocate per line
    Remaining_SOOFIES_to_Allocate=DW_val-idx

    if Remaining_SOOFIES_to_Allocate>0: #if there are more to fill in...
        Total_Allocate=[]
        for i in range(len(DW_Line_Stat)):
            val_add=math.ceil(DW_val*DW_Line_Stat.iloc[i]['RelSeg_Length'])
            Total_Allocate.append(val_add)
        DW_Line_Stat['TotalToAllocate']=Total_Allocate
        #reorganize storted from greatest to least by # of SOOFIEs to allocate
        DW_Line_Stat = DW_Line_Stat.sort_values(by='TotalToAllocate', ascending=False)
        idx_start=0
        while Remaining_SOOFIES_to_Allocate>0:
            DW_Line_Stat.at[idx_start,'AllocatedSensors']+=1 #add sensor
            Remaining_SOOFIES_to_Allocate-=1 #subtrat 1 to remaining to allocate
            if DW_Line_Stat.iloc[idx_start]['AllocatedSensors']==DW_Line_Stat.iloc[idx_start]['TotalToAllocate']:
                idx_start+=1
    #At this point we have a dataframe with line indices, and the appropriate number of sensors to allocate for each.
    
    #make sure all Allocated Sensor values are integers:
    DW_Line_Stat['AllocatedSensors'] = DW_Line_Stat['AllocatedSensors'].astype(int)
    #Now we only need to evenly space the points within each line segment.
    DW_pts_X=[]
    DW_pts_Y=[]
    for i in range(len(DW_Line_Stat)):
        linestring_idx=int(DW_Line_Stat.iloc[i]['Seg_idx'])
        add_x,add_y=EvenDistSpacing_LineStr(DW_Line_Stat.iloc[i]['AllocatedSensors'],DW_Lines[linestring_idx])
        DW_pts_X.append(add_x)
        DW_pts_Y.append(add_y)
    #get coordinates
    
    ##### UPWIND SEGMENT PROCESSING
    if UW_val>0:
    #Here we determine the number of SOOFIEs per line segment
        UW_segment_max_POD=[]
        UW_segment_length=[]
        UW_rel_segment_length=[]
        UW_Segment_Index=[]
        for i in range(UW_segment_no):
            xcoords_overlap=[]
            ycoords_overlap=[]
            PctPts_overlap=[]
            
            line1=UW_Lines[i]
            #get the length of the segment
            line1_len=calculate_geodesic_distance(line1, geod)
            UW_Segment_Index.append(i)
            UW_segment_length.append(line1_len)
            UW_rel_segment_length.append(line1_len/UW_Length)
            #get the max POD at the segment
            start_pt=line1.coords[0]
            end_pt=line1.coords[-1]
            #get azmuth from center of site to the points
            Az1,_,_ = geod.inv(Site_Center.x,Site_Center.y,start_pt[0],start_pt[1])
            Az2,_,_ = geod.inv(Site_Center.x,Site_Center.y,end_pt[0],end_pt[1])
            NewPt1_x,NewPt1_y,_=geod.fwd(Site_Center.x,Site_Center.y,Az1,1500)
            NewPt2_x,NewPt2_y,_=geod.fwd(Site_Center.x,Site_Center.y,Az2,1500)
            Az_M=Az1+5 
            Pt_M_x,Pt_M_y,_=geod.fwd(Site_Center.x,Site_Center.y,Az_M,1500)
            OverlapPoly=Create_Arc(Site_Center,NewPt1_x,NewPt1_y,NewPt2_x,NewPt2_y,Pt_M_x,Pt_M_y)
            #get x,y locations to build a large wind triangle to encompass all pts of interest:
            for n in range(len(xcoord)): #loop through all points within placement grid
                point1=sh.geometry.Point(xcoord[n],ycoord[n]) #make each coordinate in placement grid a point
                if point1.within(OverlapPoly)==True: #Check if point on grid is within these placemes to avoid
                    xcoords_overlap.append(xcoord[n]) #If it is, add to the x-grid_comp_buff layer
                    ycoords_overlap.append(ycoord[n])
                    PctPts_overlap.append(ResultPct[n])
                else:
                    continue
            UW_segment_max_POD.append(max(PctPts_overlap))
        #Here we have combined index, length of segment, max POD of segment
        UW_Line_Stat=pd.DataFrame({'Seg_idx': UW_Segment_Index,
                                   'Seg_Length': UW_segment_length,
                                   'RelSeg_Length': UW_rel_segment_length,
                                   'SegmentMaxPOD':UW_segment_max_POD,
                                   'AllocatedSensors': [0] * len(UW_Lines)})
        #Re-order based on POD
        UW_Line_Stat = UW_Line_Stat.sort_values(by='SegmentMaxPOD', ascending=False)
        
        if UW_val<len(UW_Lines): #if you have fewer SOOFIEs to allocate than there are segments:
            idx=UW_val
        else:
            idx=len(UW_Lines)
        #iteratively add the first n SOOFIEs (e.g. prioritize adding one SOOFIE per segment)
        for i in range(idx): #for each SOOFIE to allocate
            UW_Line_Stat.at[i,'AllocatedSensors']+=1 #add a sensor first.
        #Get index, length of segment, max POD of segment, and total # of soofies to allocate per line
        Remaining_SOOFIES_to_Allocate=UW_val-idx
    
        if Remaining_SOOFIES_to_Allocate>0: #if there are more to fill in...
            Total_Allocate=[]
            for i in range(len(UW_Line_Stat)):
                val_add=math.ceil(UW_val*UW_Line_Stat.iloc[i]['RelSeg_Length'])
                Total_Allocate.append(val_add)
            UW_Line_Stat['TotalToAllocate']=Total_Allocate
            #reorganize storted from greatest to least by # of SOOFIEs to allocate
            UW_Line_Stat = UW_Line_Stat.sort_values(by='TotalToAllocate', ascending=False)
            idx_start=0
            while Remaining_SOOFIES_to_Allocate>0:
                UW_Line_Stat.at[idx_start,'AllocatedSensors']+=1 #add sensor
                Remaining_SOOFIES_to_Allocate-=1 #subtrat 1 to remaining to allocate
                if UW_Line_Stat.iloc[idx_start]['AllocatedSensors']==UW_Line_Stat.iloc[idx_start]['TotalToAllocate']:
                    idx_start+=1
        #At this point we have a dataframe with line indices, and the appropriate number of sensors to allocate for each.
        
        #make sure all Allocated Sensor values are integers:
        UW_Line_Stat['AllocatedSensors'] = UW_Line_Stat['AllocatedSensors'].astype(int)
        #Now we only need to evenly space the points within each line segment.
        UW_pts_X=[]
        UW_pts_Y=[]
        for i in range(len(UW_Line_Stat)):
            linestring_idx=int(UW_Line_Stat.iloc[i]['Seg_idx'])
            add_x,add_y=EvenDistSpacing_LineStr(UW_Line_Stat.iloc[i]['AllocatedSensors'],UW_Lines[linestring_idx])
            UW_pts_X.append(add_x)
            UW_pts_Y.append(add_y)
    else:
        UW_pts_X=[]
        UW_pts_Y=[]
    
    #get coordinates
    pts_x=DW_pts_X+UW_pts_X
    pts_x = [item for sublist in pts_x for item in sublist]
    pts_y=DW_pts_Y+UW_pts_Y
    pts_y = [item for sublist in pts_y for item in sublist]
    
    plt.figure()
    plt.plot(*bdry.exterior.xy,'black')
    for i in range(len(pts_x)):
        plt.scatter(pts_x[i],pts_y[i],marker='o',color='black')
    for line in DW_Lines:
        x, y = line.xy
        plt.plot(x, y, color='red', linestyle='-', label='DW_Weighted')
    for line in UW_Lines:
        x, y = line.xy
        plt.plot(x, y, color='blue', linestyle='-', label='UW_Weighted')
    
    plt.axis('equal') #Set axis as equal
    plt.xticks([])
    plt.yticks([])
    plt.legend()
    plt.show()
    
    return pts_x, pts_y

def indices_to_sort_desc(values):
    # Enumerate the list to keep track of original indices
    enumerated_values = list(enumerate(values))
    
    # Sort by the values in descending order
    sorted_enumerated_values = sorted(enumerated_values, key=lambda x: x[1], reverse=True)
    
    # Extract the indices from the sorted enumerated list
    sorted_indices = [index for index, value in sorted_enumerated_values]
    
    return sorted_indices

def sort_list_by_indices(values, indices):
    zipped_pairs = list(zip(indices, values))
    sorted_pairs = sorted(zipped_pairs)
    sorted_values = [value for index, value in sorted_pairs]
    return sorted_values

def DW_Weighted_Part2_Prob (NumDev,xcoord,ycoord,windTriID,windTriPct,ResultPct,bdry,DW_Lines,UW_Lines,DW_Length,UW_Length):
    import math
    xcoord2=copy.deepcopy(xcoord)
    ycoord2=copy.deepcopy(ycoord)
    windTriID2=copy.deepcopy(windTriID)
    windTriPct2=copy.deepcopy(windTriPct)
    ResultPct2=copy.deepcopy(ResultPct)
    #calculate proportion of total perimeter for DW vs. UW area
    DW_prop=DW_Length/(DW_Length+UW_Length)
    UW_prop=UW_Length/(DW_Length+UW_Length)
    #Calculate the number of devices for each
    n_d_init=(math.floor(NumDev/2)+1)
    n_u_init=NumDev-n_d_init
    
    #Adusted
    DW_adj=n_d_init*.5
    UW_adj=n_u_init*.5
    
    DW_Weights=DW_adj*DW_prop/0.5
    UW_Weights=UW_adj*UW_prop/0.5
    WeightTot=DW_Weights+UW_Weights
    
    DW_fract=DW_Weights/WeightTot
    UW_fract=UW_Weights/WeightTot
    
    DW_val=round(DW_fract*NumDev)
    if DW_val>NumDev:
        DW_val=NumDev
    UW_val=NumDev-DW_val
    
    #Get the number of segments for each.
    DW_segment_no=len(DW_Lines)
    UW_segment_no=len(UW_Lines)
    
    #Get site center
    Site_Center=bdry.centroid
    
    ##### DOWNWIND SEGMENT PROCESSING
    #Here we determine the number of SOOFIEs per line segment
    DW_segment_max_POD=[]
    DW_segment_length=[]
    DW_rel_segment_length=[]
    DW_Segment_Index=[]
    DW_xcoords=[]
    DW_ycoords=[]
    DW_windTriID=[]
    DW_windTriPct=[]
    DW_ResultPct=[]
    for i in range(DW_segment_no): #For each line segment
        xcoords_overlap=[]
        ycoords_overlap=[]
        Temp_windTriID=[]
        Temp_windTriPct=[]
        Temp_ResultPct=[]
        
        line1=DW_Lines[i]
        #get the length of the segment
        line1_len=calculate_geodesic_distance(line1, geod)
        DW_Segment_Index.append(i)
        DW_segment_length.append(line1_len)
        DW_rel_segment_length.append(line1_len/DW_Length)
        #get the max POD at the segment
        start_pt=line1.coords[0]
        end_pt=line1.coords[-1]
        #get azmuth from center of site to the points
        Az1,_,_ = geod.inv(Site_Center.x,Site_Center.y,start_pt[0],start_pt[1])
        Az2,_,_ = geod.inv(Site_Center.x,Site_Center.y,end_pt[0],end_pt[1])
        NewPt1_x,NewPt1_y,_=geod.fwd(Site_Center.x,Site_Center.y,Az1,1500)
        NewPt2_x,NewPt2_y,_=geod.fwd(Site_Center.x,Site_Center.y,Az2,1500)
        Az_M=Az1+5 
        Pt_M_x,Pt_M_y,_=geod.fwd(Site_Center.x,Site_Center.y,Az_M,1500)
        OverlapPoly=Create_Arc(Site_Center,NewPt1_x,NewPt1_y,NewPt2_x,NewPt2_y,Pt_M_x,Pt_M_y)
        #get x,y locations to build a large wind triangle to encompass all pts of interest:
        for n in range(len(xcoord)): #loop through all points within placement grid
            point1=sh.geometry.Point(xcoord[n],ycoord[n]) #make each coordinate in placement grid a point
            if point1.within(OverlapPoly)==True: #Check if point on grid is within these placemes to avoid
                xcoords_overlap.append(xcoord[n]) #If it is, add to the x-grid_comp_buff layer
                ycoords_overlap.append(ycoord[n])
                Temp_ResultPct.append(ResultPct[n])
                Temp_windTriPct.append(windTriPct[n])
                Temp_windTriID.append(windTriID[n])
                
            else:
                continue
        #Add in overlapping points info:
        DW_xcoords.append(xcoords_overlap)
        DW_ycoords.append(ycoords_overlap)
        DW_segment_max_POD.append(max(Temp_ResultPct))
        DW_windTriID.append(Temp_windTriID)
        DW_windTriPct.append(Temp_windTriPct)
        DW_ResultPct.append(Temp_ResultPct)
    #Here we have combined index, length of segment, max POD of segment
    DW_Line_Stat=pd.DataFrame({'Seg_idx': DW_Segment_Index,
                               'Seg_Length': DW_segment_length,
                               'RelSeg_Length': DW_rel_segment_length,
                               'SegmentMaxPOD':DW_segment_max_POD,
                               'WindTriID': DW_windTriID,
                               'WindTriPct': DW_windTriPct,
                               'ResultPct': DW_ResultPct,
                               'DW_xcoords': DW_xcoords,
                               'DW_ycoords': DW_ycoords,
                               'AllocatedSensors': [0] * len(DW_Lines)})
    #Re-order based on POD
    DW_Line_Stat = DW_Line_Stat.sort_values(by='SegmentMaxPOD', ascending=False)
    
    if DW_val<len(DW_Lines): #if you have fewer SOOFIEs to allocate than there are segments:
        idx=DW_val
    else:
        idx=len(DW_Lines)
    #iteratively add the first n SOOFIEs (e.g. prioritize adding one SOOFIE per segment)
    for i in range(idx): #for each SOOFIE to allocate
        DW_Line_Stat.at[i,'AllocatedSensors']+=1 #add a sensor first.
    #Get index, length of segment, max POD of segment, and total # of soofies to allocate per line
    Remaining_SOOFIES_to_Allocate=DW_val-idx

    if Remaining_SOOFIES_to_Allocate>0: #if there are more to fill in...
        Total_Allocate=[]
        for i in range(len(DW_Line_Stat)):
            val_add=math.ceil(DW_val*DW_Line_Stat.iloc[i]['RelSeg_Length'])
            Total_Allocate.append(val_add)
        DW_Line_Stat['TotalToAllocate']=Total_Allocate
        #reorganize storted from greatest to least by # of SOOFIEs to allocate
        DW_Line_Stat = DW_Line_Stat.sort_values(by='TotalToAllocate', ascending=False)
        idx_start=0
        while Remaining_SOOFIES_to_Allocate>0:
            DW_Line_Stat.at[idx_start,'AllocatedSensors']+=1 #add sensor
            Remaining_SOOFIES_to_Allocate-=1 #subtrat 1 to remaining to allocate
            if DW_Line_Stat.iloc[idx_start]['AllocatedSensors']==DW_Line_Stat.iloc[idx_start]['TotalToAllocate']:
                idx_start+=1
    #At this point we have a dataframe with line indices, and the appropriate number of sensors to allocate for each.
    
    #make sure all Allocated Sensor values are integers:
    DW_Line_Stat['AllocatedSensors'] = DW_Line_Stat['AllocatedSensors'].astype(int)
    #Now we only need to add sensors at locations of highest probability.
    DW_pts_X=[]
    DW_pts_Y=[]
    DW_pct=[]
    for i in range(len(DW_Line_Stat)): #for each Line,
        #Get the pct values for each line
        Line_xcoord=DW_Line_Stat.iloc[i]['DW_xcoords']
        Line_ycoord=DW_Line_Stat.iloc[i]['DW_ycoords']
        Line_ResultPct=DW_Line_Stat.iloc[i]['ResultPct']
        Line_WindTriID=DW_Line_Stat.iloc[i]['WindTriID']
        Line_WindTriPct=DW_Line_Stat.iloc[i]['WindTriPct']
        
        #Make sure that everything is sorted from high to low ResultPct
        sorted_indices = indices_to_sort_desc(Line_ResultPct)
        Sorted_Line_ResultPct = sort_list_by_indices(Line_ResultPct, sorted_indices)
        Sorted_Line_WindTriID = sort_list_by_indices(Line_WindTriID, sorted_indices)
        Sorted_Line_WindTriPct = sort_list_by_indices(Line_WindTriPct, sorted_indices)
        Sorted_Line_xcoord = sort_list_by_indices(Line_xcoord, sorted_indices)
        Sorted_Line_ycoord = sort_list_by_indices(Line_ycoord, sorted_indices)

        #Check how many sensors to place
        Sensors_To_Place=int(DW_Line_Stat.iloc[i]['AllocatedSensors'])
        for j in range(Sensors_To_Place): #For each sensor to place
            DW_pts_X.append(Sorted_Line_xcoord[0])
            DW_pts_Y.append(Sorted_Line_ycoord[0])
            DW_pct.append(Sorted_Line_ResultPct[0])
            Sorted_Line_xcoord, Sorted_Line_ycoord, Sorted_Line_WindTriID, Sorted_Line_WindTriPct, Sorted_Line_ResultPct,_=PctRefresh(Sorted_Line_xcoord,Sorted_Line_ycoord,Sorted_Line_WindTriID,Sorted_Line_WindTriPct,Sorted_Line_ResultPct,Sorted_Line_xcoord[0],Sorted_Line_ycoord[0],FigShow=None,DelVals=None)

    ##### UPWIND SEGMENT PROCESSING
    if UW_val>0:
        #First we modify the xcoord vals, etc. for updated POD from DW_values
        for idx in range(len(DW_pts_X)):
            used_coord_x=DW_pts_X[idx]
            used_coord_y=DW_pts_Y[idx]
            xcoord2,ycoord2,windTriID2,windTriPct2,ResultPct2,_=PctRefresh(xcoord2,ycoord2,windTriID2,windTriPct2,ResultPct2,used_coord_x,used_coord_y,FigShow=None,DelVals=None)
                
        #Here we determine the number of SOOFIEs per line segment
        UW_segment_max_POD=[]
        UW_segment_length=[]
        UW_rel_segment_length=[]
        UW_Segment_Index=[]
        UW_xcoords=[]
        UW_ycoords=[]
        UW_windTriID=[]
        UW_windTriPct=[]
        UW_ResultPct=[]
        for i in range(UW_segment_no): #For each line segment
            xcoords_overlap=[]
            ycoords_overlap=[]
            Temp_windTriID=[]
            Temp_windTriPct=[]
            Temp_ResultPct=[]
            
            line1=UW_Lines[i]
            #get the length of the segment
            line1_len=calculate_geodesic_distance(line1, geod)
            UW_Segment_Index.append(i)
            UW_segment_length.append(line1_len)
            UW_rel_segment_length.append(line1_len/UW_Length)
            #get the max POD at the segment
            start_pt=line1.coords[0]
            end_pt=line1.coords[-1]
            #get azmuth from center of site to the points
            Az1,_,_ = geod.inv(Site_Center.x,Site_Center.y,start_pt[0],start_pt[1])
            Az2,_,_ = geod.inv(Site_Center.x,Site_Center.y,end_pt[0],end_pt[1])
            NewPt1_x,NewPt1_y,_=geod.fwd(Site_Center.x,Site_Center.y,Az1,1500)
            NewPt2_x,NewPt2_y,_=geod.fwd(Site_Center.x,Site_Center.y,Az2,1500)
            Az_M=Az1+5 
            Pt_M_x,Pt_M_y,_=geod.fwd(Site_Center.x,Site_Center.y,Az_M,1500)
            OverlapPoly=Create_Arc(Site_Center,NewPt1_x,NewPt1_y,NewPt2_x,NewPt2_y,Pt_M_x,Pt_M_y)
            #get x,y locations to build a large wind triangle to encompass all pts of interest:
            for n in range(len(xcoord2)): #loop through all points within placement grid
                point1=sh.geometry.Point(xcoord2[n],ycoord2[n]) #make each coordinate in placement grid a point
                if point1.within(OverlapPoly)==True: #Check if point on grid is within these placemes to avoid
                    xcoords_overlap.append(xcoord2[n]) #If it is, add to the x-grid_comp_buff layer
                    ycoords_overlap.append(ycoord2[n])
                    Temp_ResultPct.append(ResultPct2[n])
                    Temp_windTriPct.append(windTriPct2[n])
                    Temp_windTriID.append(windTriID2[n])
                    
                else:
                    continue
            #Add in overlapping points info:
            UW_xcoords.append(xcoords_overlap)
            UW_ycoords.append(ycoords_overlap)
            UW_segment_max_POD.append(max(Temp_ResultPct))
            UW_windTriID.append(Temp_windTriID)
            UW_windTriPct.append(Temp_windTriPct)
            UW_ResultPct.append(Temp_ResultPct)
        #Here we have combined index, length of segment, max POD of segment
        UW_Line_Stat=pd.DataFrame({'Seg_idx': UW_Segment_Index,
                                   'Seg_Length': UW_segment_length,
                                   'RelSeg_Length': UW_rel_segment_length,
                                   'SegmentMaxPOD':UW_segment_max_POD,
                                   'WindTriID': UW_windTriID,
                                   'WindTriPct': UW_windTriPct,
                                   'ResultPct': UW_ResultPct,
                                   'UW_xcoords': UW_xcoords,
                                   'UW_ycoords': UW_ycoords,
                                   'AllocatedSensors': [0] * len(UW_Lines)})
        #Re-order based on POD
        UW_Line_Stat = UW_Line_Stat.sort_values(by='SegmentMaxPOD', ascending=False)
    
        if UW_val<len(UW_Lines): #if you have fewer SOOFIEs to allocate than there are segments:
            idx=UW_val
        else:
            idx=len(UW_Lines)
        #iteratively add the first n SOOFIEs (e.g. prioritize adding one SOOFIE per segment)
        for i in range(idx): #for each SOOFIE to allocate
            UW_Line_Stat.at[i,'AllocatedSensors']+=1 #add a sensor first.
        #Get index, length of segment, max POD of segment, and total # of soofies to allocate per line
        Remaining_SOOFIES_to_Allocate=UW_val-idx
    
        if Remaining_SOOFIES_to_Allocate>0: #if there are more to fill in...
            Total_Allocate=[]
            for i in range(len(UW_Line_Stat)):
                val_add=math.ceil(UW_val*UW_Line_Stat.iloc[i]['RelSeg_Length'])
                Total_Allocate.append(val_add)
            UW_Line_Stat['TotalToAllocate']=Total_Allocate
            #reorganize storted from greatest to least by # of SOOFIEs to allocate
            UW_Line_Stat = UW_Line_Stat.sort_values(by='TotalToAllocate', ascending=False)
            idx_start=0
            while Remaining_SOOFIES_to_Allocate>0:
                UW_Line_Stat.at[idx_start,'AllocatedSensors']+=1 #add sensor
                Remaining_SOOFIES_to_Allocate-=1 #subtrat 1 to remaining to allocate
                if UW_Line_Stat.iloc[idx_start]['AllocatedSensors']==UW_Line_Stat.iloc[idx_start]['TotalToAllocate']:
                    idx_start+=1
        #At this point we have a dataframe with line indices, and the appropriate number of sensors to allocate for each.
    
        #make sure all Allocated Sensor values are integers:
        UW_Line_Stat['AllocatedSensors'] = UW_Line_Stat['AllocatedSensors'].astype(int)
        #Now we only need to add sensors at locations of highest probability.
        UW_pts_X=[]
        UW_pts_Y=[]
        UW_pct=[]
        for i in range(len(UW_Line_Stat)): #for each Line,
            #Get the pct values for each line
            Line_xcoord=UW_Line_Stat.iloc[i]['UW_xcoords']
            Line_ycoord=UW_Line_Stat.iloc[i]['UW_ycoords']
            Line_ResultPct=UW_Line_Stat.iloc[i]['ResultPct']
            Line_WindTriID=UW_Line_Stat.iloc[i]['WindTriID']
            Line_WindTriPct=UW_Line_Stat.iloc[i]['WindTriPct']
            
            #Make sure that everything is sorted from high to low ResultPct
            sorted_indices = indices_to_sort_desc(Line_ResultPct)
            Sorted_Line_xcoord = sort_list_by_indices(Line_xcoord, sorted_indices)
            Sorted_Line_ycoord = sort_list_by_indices(Line_ycoord, sorted_indices)
            Sorted_Line_ResultPct = sort_list_by_indices(Line_ResultPct, sorted_indices)
            Sorted_Line_WindTriID = sort_list_by_indices(Line_WindTriID, sorted_indices)
            Sorted_Line_WindTriPct = sort_list_by_indices(Line_WindTriPct, sorted_indices)
            #Check how many sensors to place
            Sensors_To_Place=int(UW_Line_Stat.iloc[i]['AllocatedSensors'])
            for j in range(Sensors_To_Place): #For each sensor to place
                UW_pts_X.append(Sorted_Line_xcoord[0])
                UW_pts_Y.append(Sorted_Line_ycoord[0])
                UW_pct.append(Sorted_Line_ResultPct[0])
                Sorted_Line_xcoord,Sorted_Line_ycoord,Sorted_Line_WindTriID,Sorted_Line_WindTriPct,Sorted_Line_ResultPct,_=PctRefresh(Sorted_Line_xcoord,Sorted_Line_ycoord,Sorted_Line_WindTriID,Sorted_Line_WindTriPct,Sorted_Line_ResultPct,Sorted_Line_xcoord[0],Sorted_Line_ycoord[0],FigShow=None,DelVals=None) 
    else:
        UW_pts_X=[]
        UW_pts_Y=[]
    
    #get coordinates
    pts_x=DW_pts_X+UW_pts_X
    #pts_x = [item for sublist in pts_x for item in sublist]
    pts_y=DW_pts_Y+UW_pts_Y
    #pts_y = [item for sublist in pts_y for item in sublist]
    
    plt.figure()
    plt.plot(*bdry.exterior.xy,'black')
    for i in range(len(pts_x)):
        plt.scatter(pts_x[i],pts_y[i],marker='o',color='black')
    for line in DW_Lines:
        x, y = line.xy
        plt.plot(x, y, color='red', linestyle='-', label='DW_Weighted')
    for line in UW_Lines:
        x, y = line.xy
        plt.plot(x, y, color='blue', linestyle='-', label='UW_Weighted')
    
    plt.axis('equal') #Set axis as equal
    plt.xticks([])
    plt.yticks([])
    plt.legend()
    plt.show()
    
    return pts_x, pts_y

def ProbOnly(NumDev, xcoord, ycoord, windTriID, windTriPct, ResultPct,Fig=None):
     
    Pts_x=[]
    Pts_y=[]
    Pts_pct=[]
    for i in range(NumDev): #For each point
        print('Calculating for',i+1,'Device(s)')
        if ResultPct[0]>0:
            Pts_x.append(xcoord[0])
            Pts_y.append(ycoord[0])
            Pts_pct.append(ResultPct[0])
            
            if Fig==None:
                xcoord,ycoord,windTriID,windTriPct,ResultPct,_=PctRefresh(xcoord,ycoord,windTriID,windTriPct,ResultPct,xcoord[0],ycoord[0],FigShow='Off')
            else:
                xcoord,ycoord,windTriID,windTriPct,ResultPct,_=PctRefresh(xcoord,ycoord,windTriID,windTriPct,ResultPct,xcoord[0],ycoord[0],FigShow='On')
            
        else: #break out of loop if you have exhausted grid (e.g. all wind triangles covered)
            print('exhausted loop')    
            #val_left=NumDev-len(Pts_x)
            break
    
    fnl_x=Pts_x
    fnl_y=Pts_y
    fnl_pct=Pts_pct

    return fnl_x, fnl_y, fnl_pct

# Set up query
def query(strg,val):
    output_val=False
    for i in range(len(strg)):
        if strg[i].isnumeric():
            if int(strg[i])==val:
                output_val=True
                break
            else:
                continue
        else:
            continue
    return output_val

def extract_kml_from_kmz(kmz_file_path):
    with zipfile.ZipFile(kmz_file_path, 'r') as kmz:
        # Get the KML file from the KMZ
        kml_filename = [name for name in kmz.namelist() if name.endswith('.kml')][0]
        with kmz.open(kml_filename) as kml_file:
            return kml_file.read()

def parse_kml(kml_content):
    root = ET.fromstring(kml_content)
    polygons = []
    for placemark in root.findall('.//{http://www.opengis.net/kml/2.2}Placemark'):
        description_element = placemark.find('.//{http://www.opengis.net/kml/2.2}description')
        description = description_element.text if description_element is not None else ""
        polygon = placemark.find('.//{http://www.opengis.net/kml/2.2}Polygon')
        if polygon is not None:
            coordinates = polygon.find('.//{http://www.opengis.net/kml/2.2}coordinates').text
            # Convert coordinates to Shapely Polygon
            coords = [tuple(map(float, coord.split(','))) for coord in coordinates.split()]
            polygon_geom = Polygon(coords)
            polygons.append((description, polygon_geom))
    return polygons

def find_bounds(peak_val,WindDirs,WindPcts,val_type):
    '''
    Parameters
    ----------
    peak_val : int
        Index in wind_directions that is the peak value.
    WindDirs : series object
        series of wind direction categories
    WindPcts : series object
        percentage associated with each wind direction category
    val_type : string
        'lower' or 'upper' bound.

    Returns
    -------
    bound_idx : The index in wind_directions/percentages that is associated with the lower or upper bound
    no_idxs: Number of indexes to get to LB/UB
    '''
    #Find minimum bound of peak
    slo=99
    doc=[]
    slo_val=[]
    while slo>0:
        for j in range(len(WindDirs)):
            if j==0:
                temp_idx=j+peak_val
            if val_type=='lower':
                temp_idx_next=temp_idx-1
            elif val_type=='upper':
                temp_idx_next=temp_idx+1
            else:
                print('error')
                break
            if temp_idx_next<0:
                temp_idx_next+=len(WindDirs)
            if temp_idx_next>len(WindDirs)-1:
                temp_idx_next-=len(WindDirs)
            slo=WindPcts[temp_idx]-WindPcts[temp_idx_next]
            # Check if slo is less than or equal to zero to break the loop
            if slo <= 0:
                break  # Break out of the for loop
            doc.append(temp_idx)
            slo_val.append(slo)
            temp_idx=temp_idx_next
    bound_idx=temp_idx
    no_idxs=doc[1:]
    
    return bound_idx, no_idxs

def is_continuous_circular(lst, max_index):
    result_sum=0
    result_val=True
    if not lst:
        result_val=False
    
    sorted_lst = sorted(lst)
    num_elements = len(sorted_lst)
    break_idx=[]
    continuous_list=[]
    for i in range(num_elements): #for each value
        current= sorted_lst[i] #get current value
        #print(current)
        prev_expect=current-1
        if prev_expect<0:
            prev_expect+=max_index+1
        next_expect=current+1
        if next_expect>max_index:
            next_expect-=max_index+1
        next_expect_plus_one=next_expect+1
        if next_expect_plus_one>max_index:
            next_expect_plus_one-=max_index+1
        prev_expect_minus_one=next_expect-1
        if prev_expect_minus_one<0:
            prev_expect_minus_one+=max_index+1
        #print('previous expect:',prev_expect)
        #print('next expect:',next_expect)
        if next_expect in sorted_lst or next_expect_plus_one in sorted_lst:
            #print('continuous')
            continue
        else:
            if current==0 and 35 in sorted_lst:
                continue  
            else:
                result_sum+=1
                #print('break')
                break_idx.append(i)
    
    if result_sum<2:
        result_val=True
        continuous_list=sorted_lst
        if min(sorted_lst)==0 and max(sorted_lst)==max_index:
            continuous_list=lst[break_idx[0]+1:] + lst[:break_idx[0]+1]
    else:
        result_val=False
        continuous_list=[]

    return result_val, continuous_list, result_sum, break_idx

def check_within_two_values_between_lists(list1, list2):
    for num1 in list1:
        for num2 in list2:
            if abs(num1 - num2) <= 2:
                return True
    return False

def find_combinations(nested_list):
    combinations = []
    n = len(nested_list)
    for i in range(n):
        for j in range(i + 1, n):
            if check_within_two_values_between_lists(nested_list[i], nested_list[j]):
                combinations.append((i, j))
    return combinations
