from app.services.imports import *
from app.services.functions import *


# region Step 1
#%% Step 1: Navigate to the relevant file you'd like to upload.

if __name__ == "__main__":
    #Ask the user to input the operator name:
    Operator_Name=input('Enter operator name:')
    
    #Ask the user to input the site name they would like to save created files under:
    Project_Name=input('Enter name of site:')
    
    print('Please navigate to the image of the site.')
    root = tk.Tk()
    root.withdraw()
    #file_path = filedialog.askopenfilename(filetypes=[(".tif files","*.tif *.tiff),(".jpg files","*.jpg"),(".png files","*.png")])
    file_path = filedialog.askopenfilename(filetypes=[(".tif/.jpg/.png files","*.tif *.tiff *.jpg *.png")])
    
    #Check if file is a Geotiff or a jpg/png that need to be georeferenced:
    if file_path.split('.')[-1]=='tif' or file_path.split('.')[-1]=='tiff':
        ImgType='GeoTiff'
    else:
        ImgType='Jpg/Png'
    
    #Verify the folder where the user will like to save all of their files:
    Chg_Path=input('Your current file path is: '+os.path.dirname(file_path)+'\n'+'Do you want to: \n'
                                                +'1. Stay at current folder path \n'
                                                +'2. Create new folder with project name and store everything there, or\n'
                                                +'3. Change to another folder\n'
                                                +'Your selection:')
    if Chg_Path=='3': #Change to another folder
        new_path=filedialog.askdirectory()
        os.chdir(os.path.dirname(new_path))
    elif Chg_Path=='1': #don't change path
        os.chdir(os.path.dirname(file_path))
        new_path=os.path.dirname(file_path)
    else: #Change path to a new directory, named after the project name.
        print('select root directory (e.g. where your folder will be located)')
        new_file_dir=filedialog.askdirectory()
        new_path=new_file_dir+'/'+Project_Name
        makemydir(new_path)
        
    # endregion


    #Step 3: Upload imagery, crop GeoTiffs, or Georeference png/jpg image and make into GeoTiff.
    
    #If it is a Geotiff
    if ImgType=='GeoTiff': #If you upload a geotiff, ask if it needs to be cropped
        ds=gdal.Open(file_path) #open the file
        prj_file_name=str(new_path+'/'+str(Project_Name)+'_proj.tif')
        #print(ds.GetGeoTransform)
        #print(ds.GetProjection())
        
        dsReproj=gdal.Warp(prj_file_name,ds,dstSRS="EPSG:4326") #reproject to WGS84 and name it 'Project_Name_proj'
        dsReproj=None #close image
        ds=None #close image
        
        IfCrop= input('Would you like to crop the image?: \n'
                      +'1) Yes \n'
                      +'2) No \n'
                      +'Your selection:')
        if IfCrop=='Yes' or IfCrop=='1': #This means you need to crop the image
            #First open the image in rasterio and get its dimensions
            picture=rio.open(prj_file_name)
            #show(picture)
            #print(picture.height,picture.width) #get image size:
            ref_point = []
            # load the image, clone it, and setup the mouse callback function
            image = cv.imread(prj_file_name)
            clone = image.copy()
            cv.namedWindow("image", cv.WINDOW_NORMAL)
            cv.setMouseCallback("image", shape_selection)
    
            # keep looping until escape is pressed
            while True:
                # display the image and wait for a keypress
                cv.imshow("image", image)
                key = cv.waitKey(1) & 0xFF
                # press 'r' to reset the window
                if key == ord("r"):
                    image = clone.copy()
                # if the 'c' key is pressed, break from the loop
                elif key == 27:
                    break
            # close all open windows
            cv.destroyAllWindows()       
            #The value 'ref_point' has the pixel coordinates of the rectangle
            with rio.open(prj_file_name) as src:
            # Read the raster data
                data = src.read(1)  # Assuming you want to read the first band
            
                # Get the geotransform (affine transformation matrix)
                transform = src.transform
            
                # Get the coordinate reference system (CRS)
                crs = src.crs
                
                Crop_coords_x=[]
                Crop_coords_y=[]
                
                for val in ref_point:
                # Convert cropping pixel coordinates to lat/lon
                    crop_x,crop_y=transform*(val[0],val[1])
                    Crop_coords_x.append(crop_x)
                    Crop_coords_y.append(crop_y)

            new_tiff_name=Project_Name+'_clip'+'.tif'
            ds2=gdal.Open(prj_file_name)
            ds2=gdal.Translate(new_tiff_name,ds2,projWin=[Crop_coords_x[0], Crop_coords_y[0], Crop_coords_x[1], Crop_coords_y[1]])
            ds2=None #close image
            FileNameToUse=new_tiff_name
        else:
            FileNameToUse=prj_file_name
    
    if ImgType=='Jpg/Png': #If image is a Jpg/Png, convert it to a .tif
        #convert image to a tif
        conv_img=new_path+'/'+Project_Name+'.tif'
        #conv_img=file_path.split(".")[0]+'.tif'
        im = Image.open(file_path) #take jpg/png image
        im.save(conv_img)  #Save image as .tif and save as project_name.tif'
        #Get Image size
        Size=im.size
        #Step 2: Get Pixel coordinates of the GCPs
        cv.namedWindow('Point Coordinates', cv.WINDOW_NORMAL)
        # of the points clicked on the image
        coords_X=[]
        coords_Y=[]
        def click_event(event, x, y, flags, params):
            if event == cv.EVENT_LBUTTONDOWN:
               print(f'({x},{y})')
               coords_X.append(x)
               coords_Y.append(y)
               # put coordinates as text on the image
               cv.putText(img, f'({x},{y})',(x,y),
               cv.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
               
               # draw point on the image
               cv.circle(img, (x,y), 5, (0,255,255), -1)
            return coords_X,coords_Y
         
        # read the input image
        img = cv.imread(file_path)
        # bind the callback function to window
        cv.setMouseCallback('Point Coordinates', click_event)
    
        # display the image
        while True:
           cv.imshow('Point Coordinates',img)
           k = cv.waitKey(1) & 0xFF
           if k== 27:
               break
        cv.destroyAllWindows()
        #Step 3: Get Long/Lat Coordinates of GCPs
    
        # Load the KMZ file and extract the KML data
        print('Please load the .kmz point files of your ground control points:')
        kmz_path = filedialog.askopenfilename(filetypes=[(".kmz files","*.kmz")])
        kmz = zipfile.ZipFile(kmz_path, 'r')  # extract zip file first, then read kmz file inside the extracted folder
        kml_content = kmz.open('doc.kml', 'r').read()  # kml content
        # create KML object
        k = kml.KML()
        k.from_string(kml_content)
    
        # read features from docs to folders to records and then extract geometries - in my case, Shapely points
        docs = list(k.features())
        folders = []
        for d in docs:
            folders.extend(list(d.features()))
        records = []
        for f in folders:
            records.extend(list(f.features()))
        geoms = [element.geometry for element in records]  # extract geometry
    
        Coords_X=[]
        Coords_Y=[]
        for point in geoms:
            Coords_X.append(point.coords[0][0])
            Coords_Y.append(point.coords[0][1])
        # Step 4: Upload converted image and georeference
        orig_fn = conv_img
        output_fn = new_path+'/'+Project_Name+'_proj.tif' #projected file name
    
        # Create a copy of the original file and save it as the output filename:
        shutil.copy(orig_fn, output_fn)
        # Open the output file for writing:
        ds = gdal.Open(output_fn, gdal.GA_Update)
        # Set spatial reference:
        sr = osr.SpatialReference()
        sr.ImportFromEPSG(4326) #Projection
    
        # Enter the GCPs--one for transforming the raster, and another for transforming pixel points to raster.
        #   Format: [map x-coordinate(longitude)], [map y-coordinate (latitude)], [elevation],
        #   [image column index(x)], [image row index (y)]
        gcps=[]
        gcps2=[]
        for i in range(len(Coords_X)):
            if i < len(Coords_X)-1:
                gcps.append(gdal.GCP(Coords_X[i],Coords_Y[i],0,coords_X[i],coords_Y[i]),)
                gcps2.append(GroundControlPoint(row=coords_X[i],col=coords_Y[i],x=Coords_X[i],y=Coords_Y[i],z=0,id=str(i),info=''),)
            else:
                gcps.append(gdal.GCP(Coords_X[i],Coords_Y[i],0,coords_X[i],coords_Y[i]),)
                gcps2.append(GroundControlPoint(row=coords_X[i],col=coords_Y[i],x=Coords_X[i],y=Coords_Y[i],z=0,id=str(i),info=''))
    
    
        # Apply the GCPs to the open output file:
        ds.SetGCPs(gcps, sr.ExportToWkt())
    
        # Close the output file in order to be able to work with it in other programs:
        ds = None
        
        transformer=rio.transform.GCPTransformer(gcps2)
        FileNameToUse=output_fn


# region Step 2
#%% Step 2: Ask about off-site emissions
if __name__ == "__main__":
    img_path=FileNameToUse
    ask_offsite=input('Are there any off-site emissions that you would like to delineate and detect? \n'
                      +'1) Yes \n'
                      +'2) No \n'
                      +'Your selection:')
    
    if int(ask_offsite)==1:
        FINAL_LINE_COLOR = (255, 255, 255)
        WORKING_LINE_COLOR = (255, 255, 255)
        FINAL_POLY_COLOR=(255,255,255)
    
        class PolygonDrawer(object):
            def __init__(self, window_name):
                self.window_name = window_name # Name for our window
    
                self.done = False # Flag signalling we're done
                self.current = (0, 0) # Current position, so we can draw the line-in-progress
                self.points = [] # List of points defining our polygon
    
    
            def on_mouse(self, event, x, y, buttons, user_param):
                # Mouse callback that gets called for every mouse event (i.e. moving, clicking, etc.)
    
                if self.done: # Nothing more to do
                    return
    
                if event == cv.EVENT_MOUSEMOVE:
                    # We want to be able to draw the line-in-progress, so update current mouse position
                    self.current = (x, y)
                elif event == cv.EVENT_LBUTTONDOWN:
                    # Left click means adding a point at current position to the list of points
                    print("Adding point #%d with position(%d,%d)" % (len(self.points), x, y))
                    self.points.append((x, y))
                elif event == cv.EVENT_RBUTTONDOWN:
                    # Right click means we're done
                    print("Completing polygon with %d points." % len(self.points))
                    self.done = True
    
            def run(self):
                # Let's create our working window and set a mouse callback to handle events
                canvas = cv.imread(img_path)
                cv.namedWindow(self.window_name, flags=cv.WINDOW_NORMAL)
                cv.imshow(self.window_name, canvas)
                cv.waitKey(1)
                cv.setMouseCallback(self.window_name, self.on_mouse)
                alpha=0.5
                while(not self.done):
                    # This is our drawing loop, we just continuously draw new images
                    # and show them in the named window
                    canvas = cv.imread(img_path)
                    if (len(self.points) > 0):
                        # Draw all the current polygon segments
                        cv.polylines(canvas, np.array([self.points]), False, FINAL_LINE_COLOR, 4)
                        # And  also show what the current segment would look like
                        cv.line(canvas, self.points[-1], self.current, WORKING_LINE_COLOR,4)
                    # Update the window
                    cv.imshow(self.window_name, canvas)
                    # And wait 50ms before next iteration (this will pump window messages meanwhile)
                    if cv.waitKey(50) == 27: # ESC hit
                        self.done = True
    
                # User finished entering the polygon points, so let's make the final drawing
                canvas = cv.imread(img_path)
                overlay=canvas.copy()
                output=canvas.copy()
                # of a filled polygon
                alpha=0.5
                if (len(self.points) > 0):
                    cv.fillPoly(overlay, np.array([self.points]), FINAL_POLY_COLOR)
                    # apply the overlay
                    cv.addWeighted(overlay, alpha, output, 1 - alpha,0, output)
                # And show it
                cv.imshow(self.window_name, output)
                # Waiting for the user to press any key
                cv.waitKey()
    
                cv.destroyWindow(self.window_name)
                return output
        # ============================================================================
        
        if __name__ == "__main__":
            polyd = PolygonDrawer("OffSite")
            image = polyd.run()
            #cv2.imwrite("OffSiteBdry.png", image)
            print("Offsite Boundary = %s" % polyd.points)
        
        OffSitePoly_Pixels=polyd.points #points of polygon for site boundary
        OffSitePoly_LatLon=[]
        for i in range(len(OffSitePoly_Pixels)):
            #print(SiteBdryPoly_Pixels[i])
            if ImgType=='GeoTiff':
                with rio.open(img_path) as src: # Read the raster data
                    data = src.read(1)  # Assuming you want to read the first band
                    # Get the geotransform (affine transformation matrix)
                    transform = src.transform
                    # Get the coordinate reference system (CRS)
                    crs = src.crs
                    # Convert pixel coordinates to map coordinates (lat/lon)
                    pIxl_off=transform * (OffSitePoly_Pixels[i][0], OffSitePoly_Pixels[i][1])
                    OffSitePoly_LatLon.append(pIxl_off)
            
            else:
                OffSitePoly_LatLon.append(transformer.xy(OffSitePoly_Pixels[i][0],OffSitePoly_Pixels[i][1]))
            if i== len(OffSitePoly_Pixels)-1:
                if ImgType=='GeoTiff':
                    pIxl_off=transform * (OffSitePoly_Pixels[0][0], OffSitePoly_Pixels[0][1])
                    OffSitePoly_LatLon.append(pIxl_off)
                else:
                    OffSitePoly_LatLon.append(transformer.xy(OffSitePoly_Pixels[0][0],OffSitePoly_Pixels[0][1]))
            else:
                continue
        OffSitebdry=sh.geometry.Polygon(OffSitePoly_LatLon)

# endregion


# region Step 3
#%% Step 3: Draw the site boundary
if __name__ == "__main__":

    FINAL_LINE_COLOR = (255, 255, 255)
    WORKING_LINE_COLOR = (255, 255, 255)
    FINAL_POLY_COLOR=(255,255,255)
    
    class PolygonDrawer(object):
        def __init__(self, window_name):
            self.window_name = window_name # Name for our window
    
            self.done = False # Flag signalling we're done
            self.current = (0, 0) # Current position, so we can draw the line-in-progress
            self.points = [] # List of points defining our polygon
    
    
        def on_mouse(self, event, x, y, buttons, user_param):
            # Mouse callback that gets called for every mouse event (i.e. moving, clicking, etc.)
    
            if self.done: # Nothing more to do
                return
    
            if event == cv.EVENT_MOUSEMOVE:
                # We want to be able to draw the line-in-progress, so update current mouse position
                self.current = (x, y)
            elif event == cv.EVENT_LBUTTONDOWN:
                # Left click means adding a point at current position to the list of points
                print("Adding point #%d with position(%d,%d)" % (len(self.points), x, y))
                self.points.append((x, y))
            elif event == cv.EVENT_RBUTTONDOWN:
                # Right click means we're done
                print("Completing polygon with %d points." % len(self.points))
                self.done = True
    
        def run(self):
            # Let's create our working window and set a mouse callback to handle events
            canvas = cv.imread(img_path)
            cv.namedWindow(self.window_name, flags=cv.WINDOW_NORMAL)
            cv.imshow(self.window_name, canvas)
            cv.waitKey(1)
            cv.setMouseCallback(self.window_name, self.on_mouse)
            alpha=0.5
            while(not self.done):
                # This is our drawing loop, we just continuously draw new images
                # and show them in the named window
                canvas = cv.imread(img_path)
                if (len(self.points) > 0):
                    # Draw all the current polygon segments
                    cv.polylines(canvas, np.array([self.points]), False, FINAL_LINE_COLOR, 4)
                    # And  also show what the current segment would look like
                    cv.line(canvas, self.points[-1], self.current, WORKING_LINE_COLOR,4)
                # Update the window
                cv.imshow(self.window_name, canvas)
                # And wait 50ms before next iteration (this will pump window messages meanwhile)
                if cv.waitKey(50) == 27: # ESC hit
                    self.done = True
    
            # User finished entering the polygon points, so let's make the final drawing
            canvas = cv.imread(img_path)
            overlay=canvas.copy()
            output=canvas.copy()
            # of a filled polygon
            alpha=0.5
            if (len(self.points) > 0):
                cv.fillPoly(overlay, np.array([self.points]), FINAL_POLY_COLOR)
                # apply the overlay
                cv.addWeighted(overlay, alpha, output, 1 - alpha,0, output)
            # And show it
            cv.imshow(self.window_name, output)
            # Waiting for the user to press any key
            cv.waitKey()
    
            cv.destroyWindow(self.window_name)
            return output
    # ============================================================================
    
    if __name__ == "__main__":
        polyd = PolygonDrawer("Polygon")
        image = polyd.run()
        cv.imwrite("SiteBoundary.png", image)
        print("Polygon = %s" % polyd.points)
    
    #Get long/lat coordinates of site boundary, looping back to first point
    SiteBdryPoly_Pixels=polyd.points #points of polygon for site boundary
    SiteBdryPoly_LatLon=[]
 #  
    for i in range(len(SiteBdryPoly_Pixels)):
        #print(SiteBdryPoly_Pixels[i])
        if ImgType=='GeoTiff':
            with rio.open(img_path) as src: # Read the raster data
                data = src.read(1)  # Assuming you want to read the first band
                # Get the geotransform (affine transformation matrix)
                transform = src.transform
                # Get the coordinate reference system (CRS)
                crs = src.crs
                # Convert pixel coordinates to map coordinates (lat/lon)
                pIxl=transform * (SiteBdryPoly_Pixels[i][0], SiteBdryPoly_Pixels[i][1])
                SiteBdryPoly_LatLon.append(pIxl)
        else:
            SiteBdryPoly_LatLon.append(transformer.xy(SiteBdryPoly_Pixels[i][0],SiteBdryPoly_Pixels[i][1]))
        if i== len(SiteBdryPoly_Pixels)-1: #add the initial point in at the end
            if ImgType=='GeoTiff':
                pIxl=transform * (SiteBdryPoly_Pixels[0][0], SiteBdryPoly_Pixels[0][1])
                SiteBdryPoly_LatLon.append(pIxl)
            else:
                SiteBdryPoly_LatLon.append(transformer.xy(SiteBdryPoly_Pixels[0][0],SiteBdryPoly_Pixels[0][1]))
        else:
            continue
#
    #Next, we try to plot the buffer area on top of the figure.
    bdry=sh.geometry.Polygon(SiteBdryPoly_LatLon)
    
    #Calculate 15 meters distance between a point, to get the decimal degree difference equivalent to 15 m at that part of the world
    x1,y1,_ = geod.fwd(SiteBdryPoly_LatLon[0][0],SiteBdryPoly_LatLon[0][1],0,15)
    dist_15=abs(y1-SiteBdryPoly_LatLon[0][1]) #Lat/long decimal degrees equivalent to 15m
    
    PolyBuff=sh.buffer(bdry,-(dist_15/15*10),join_style="mitre") #get 10 m internal buffer
    Internal_pts=list(PolyBuff.exterior.coords) #Extract points from internal buffer
    
    #Placement area polygon
    PlacementPoly=sh.geometry.Polygon(SiteBdryPoly_LatLon, [Internal_pts])
    IntPoly_lonlat=sh.geometry.Polygon(Internal_pts)
    
    #Bring Long/Lat back to image index for plotting
    internal_pixel=[]
    external_pixel=[]
    
    for i in range(len(SiteBdryPoly_LatLon)): #lon/lat into pixel
        if ImgType=='GeoTiff':
            pix_ext = ~transform * (SiteBdryPoly_LatLon[i][0], SiteBdryPoly_LatLon[i][1])
            external_pixel.append(pix_ext)
        else:
            external_pixel.append(transformer.rowcol(SiteBdryPoly_LatLon[i][0],SiteBdryPoly_LatLon[i][1]))
    
    for i in range(len(Internal_pts)):
        if ImgType=='GeoTiff':
            pix_int = ~transform * (Internal_pts[i][0], Internal_pts[i][1])
            internal_pixel.append(pix_int)
        else:
            internal_pixel.append(transformer.rowcol(Internal_pts[i][0],Internal_pts[i][1]))
    
    IntPoly=sh.geometry.Polygon(internal_pixel)    
    #Placement area polygon (in pixels)
    PlacementPoly_Px=sh.geometry.Polygon(external_pixel, [internal_pixel])
    
    img_plt = plt.imread(img_path)
    fig, ax = plt.subplots(1, 1)
    plt.imshow(img_plt)
    plt.plot(*PlacementPoly_Px.exterior.xy,'blue')
    plt.plot(*IntPoly.exterior.xy,'blue')
    plt.show()
    
    # Code for component drawings
    FINAL_LINE_COLOR = (0, 0, 255)
    WORKING_LINE_COLOR = (0, 0, 255)
    FINAL_POLY_COLOR=(0,0,255)
    shutil.copy("SiteBoundary.png","Components.png")
    img_path="Components.png"
    class PolygonDrawer(object):
        def __init__(self, window_name):
            self.window_name = window_name # Name for our window
    
            self.done = False # Flag signalling we're done
            self.current = (0, 0) # Current position, so we can draw the line-in-progress
            self.points = [] # List of points defining our polygon
    
        def on_mouse(self, event, x, y, buttons, user_param):
            # Mouse callback that gets called for every mouse event (i.e. moving, clicking, etc.)
    
            if self.done: # Nothing more to do
                return
    
            if event == cv.EVENT_MOUSEMOVE:
                # We want to be able to draw the line-in-progress, so update current mouse position
                self.current = (x, y)
            elif event == cv.EVENT_LBUTTONDOWN:
                # Left click means adding a point at current position to the list of points
                print("Adding point #%d with position(%d,%d)" % (len(self.points), x, y))
                self.points.append((x, y))
            elif event == cv.EVENT_RBUTTONDOWN:
                # Right click means we're done
                print("Completing polygon with %d points." % len(self.points))
                self.done = True
    
        def run(self):
            # Let's create our working window and set a mouse callback to handle events
            canvas = cv.imread(img_path)
            cv.namedWindow(self.window_name, flags=cv.WINDOW_NORMAL)
            cv.imshow(self.window_name, canvas)
            cv.waitKey(1)
            cv.setMouseCallback(self.window_name, self.on_mouse)
            alpha=0.5
            while(not self.done):
                # This is our drawing loop, we just continuously draw new images
                # and show them in the named window
                canvas = cv.imread(img_path)
                if (len(self.points) > 0):
                    # Draw all the current polygon segments
                    cv.polylines(canvas, np.array([self.points]), False, FINAL_LINE_COLOR, 2)
                    # And  also show what the current segment would look like
                    cv.line(canvas, self.points[-1], self.current, WORKING_LINE_COLOR,2)
                # Update the window
                cv.imshow(self.window_name, canvas)
                # And wait 50ms before next iteration (this will pump window messages meanwhile)
                if cv.waitKey(50) == 27: # ESC hit
                    self.done = True
    
            # User finished entering the polygon points, so let's make the final drawing
            canvas = cv.imread(img_path)
            overlay=canvas.copy()
            output=canvas.copy()
            # of a filled polygon
            alpha=0.5
            if (len(self.points) > 0):
                cv.fillPoly(overlay, np.array([self.points]), FINAL_POLY_COLOR)
                # apply the overlay
                cv.addWeighted(overlay, alpha, output, 1 - alpha,0, output)
            # And show it
            cv.imshow(self.window_name, output)
            # Waiting for the user to press any key
            cv.waitKey()
    
            cv.destroyWindow(self.window_name)
            return output
        
# endregion



# region Step 4
#%% Step 4: Get all component info 
if __name__ == "__main__":
    ID_components=input('Select how you would like to ingest site components: \n'
                        +'1) Draw components myself \n'
                        +'2) Upload .kmz file with all components \n'
                        + 'Your selection:')
    
    if int(ID_components)==1:
        #Get user to select component type, give component name, and extract source height info/location.
        #NOTE: Here is the chance for the user to select areas that we would like a buffer around, but
        #that may not be an emission source. In this case the emission source will be marked as 'False'.
        
        #Set up lists that will later make up the dictionary
        Name=[]
        Comp_Type=[]
        S_Height=[]
        Comp_Coords=[]
        E_Source=[]
        Comp_Coords_LonLat=[]
        Comp_Add_Rsp=1
        
        while Comp_Add_Rsp == 1:
            #Ask user to input value
            Component_Name= input("Component Name:") #This is the specific customer-based name
            
            # Let user select a component type
            while True:
                try:
                    component_type_des= input('Select Component: \n'
                                          +'1) High Pressure Flare \n'
                                          +'2) Low Pressure Flare \n'
                                          +'3) Heater Treater \n'
                                          +'4) Tank \n'
                                          +'5) Well \n'
                                          +'6) Compressor \n'
                                          +'7) Scrubber \n'
                                          +'8) Separator \n'
                                          +'9) Tester \n'
                                          +'10) Landfill \n'
                                          +'11) Exclusion Zone (road/no structure) \n'
                                          +'12) Exclusion Zone (structure) \n'
                                          +'13) Offsite Source \n'
                                          +'14) Other \n'
                                          +'Your selection:')
                    if int(component_type_des) < 1 or int(component_type_des) > 14:
                        print("Please enter a valid number.")
                        continue
                    break
                except ValueError:
                    print("Please enter a valid number.")
                    continue
            #Extract source height information from component:
            if component_type_des =='1':
                component_type= 'High Pressure Flare'
                Source_Height=10
                Emis_Source=True
            elif component_type_des =='2':
                component_type='Low Pressure Flare'
                Source_Height=5
                Emis_Source=True
            elif component_type_des=='3':
                component_type='Heater Treater'
                Source_Height=3
                Emis_Source=True
            elif component_type_des=='4':
                component_type='Tank'
                Source_Height=5
                Emis_Source=True
            elif component_type_des=='5':
                component_type='Well'
                Source_Height=3
                Emis_Source=True
            elif component_type_des=='6':
                component_type='Compressor'
                Source_Height=3
                Emis_Source=True
            elif component_type_des=='7': 
                component_type='Scrubber'
                Source_Height=3
                Emis_Source=True
            elif component_type_des=='8': 
                component_type='Separator'
                SepType=input('Select separator type: \n'
                              +'1) Horizontal \n'
                              +'2) Vertical \n'
                              +'Your selection:')
                if SepType=='1':
                    Source_Height=3
                    Emis_Source=True
                else:
                    Source_Height=4
                    Emis_Source=True
            elif component_type_des=='9': 
                component_type='Tester'
                Source_Height=3
                Emis_Source=True
            elif component_type_des=='10': 
                component_type='Landfill'
                Source_Height=0
                Emis_Source=True
            elif component_type_des=='11':  
                component_type='Exclusion Zone (road/no structure)'
                Source_Height=float('nan')
                Emis_Source=False
            elif component_type_des=='12':  
                component_type='Exclusion Zone (structure)'
                Source_Height=float('nan')
                Emis_Source=False
            elif component_type_des=='13':  
                component_type='Offsite Source'
                Emis_Source=True
                Source_Height= int(input("Enter Height (in meters) of Component:"))
            else:
                component_type='Other'
                Emis_Source_Des=input('Select whether area is a potential emissions source. \n'
                                     +'1) True, it is a potential emission \n'
                                     +'2) False, it is not a potential emission \n'
                                     +'Your selection:')
                if Emis_Source_Des=='1':
                    Emis_Source=True
                    Source_Height_str= float(input("Enter Height (in meters) of Component:"))
                else:
                    Emis_Source=False
                    Source_Height=float('nan')
            
            #This is the command to interactively draw the polygon.
            if __name__ == "__main__":
                polyd = PolygonDrawer("Polygon")
                image = polyd.run()
                cv.imwrite("Components.png", image)
                print("Polygon = %s" % polyd.points)
            
            #Here we translate pixel polygon coordinates to Long/Lat
            Coords=polyd.points
            Coords_LL=[]
            
            for pt in Coords: #pixel to long/lat
                if ImgType=='GeoTiff':
                    Coords_LLTemp=transform * (pt[0], pt[1])
                    Coords_LL.append(Coords_LLTemp)
                else:
                    Coords_LL.append(transformer.xy(pt[0],pt[1]))
        
            #Add data to pre-defined variables
            Name.append(Component_Name)
            Comp_Type.append(component_type)
            S_Height.append(Source_Height)
            E_Source.append(Emis_Source)
            Comp_Coords.append(Coords)
            Comp_Coords_LonLat.append(Coords_LL)
            
            while True:
                try:
                    Comp_Add_Rsp = int(input('Add another component? \n'
                               + '1) Yes \n'
                               + '2) No \n'
                               + 'Your selection: '))
                    if Comp_Add_Rsp not in [1, 2]:
                        print("Please enter either 1 or 2.")
                        continue
                    break
                except ValueError:
                    print("Please enter a valid number (1 or 2).")
                    continue
            
    else:
        Name=[]
        Comp_Type=[]
        S_Height=[]
        Comp_Coords=[]
        E_Source=[]
        Comp_Coords_LonLat=[]
        
        kmz_file_path = filedialog.askopenfilename(filetypes=[(".kmz files","*.kmz")])
        kml_content = extract_kml_from_kmz(kmz_file_path)
        polygons = parse_kml(kml_content)
        #polygons[0][1].coords
        
        for index, (description, polygon) in enumerate(polygons):
            
            #Extract client name
            pattern = re.compile(re.escape('Name:') + r'(.*?)' + re.escape('\n'), re.DOTALL)
            match_N = pattern.search(description)
            Comp_Name = match_N.group(1)
            #If the component name starts with a space, take that away.
            if Comp_Name.startswith(" "):
                Comp_Name = Comp_Name.lstrip()
            Name.append(Comp_Name)
            
            #Extract component type
            pattern1 = re.compile(re.escape('Comp_Type:') + r'(.*?)' + re.escape('\n'), re.DOTALL)
            match_T = pattern1.search(description)
            Comp_T = match_T.group(1)
            #If the component name starts with a space, take that away.
            if Comp_T.startswith(" "):
                Comp_T = Comp_T.lstrip()
            Comp_Type.append(Comp_T)
            
            #Extract Source Height
            pattern2 = re.compile(re.escape('S_Height:') + r'(.*?)' + re.escape('\n'), re.DOTALL)
            match_SH = pattern2.search(description)
            Comp_SH = match_SH.group(1)
            #If the component name starts with a space, take that away.
            if Comp_SH.startswith(" "):
                Comp_SH = Comp_SH.lstrip()
            S_Height.append(float(Comp_SH))
            
            #Extract Emission Source
            pattern3 = re.compile(r'E_Source: (True|False)')
            matchES = pattern3.search(description)
            e_source_value = matchES.group(1)
            E_Source.append(eval(e_source_value))
            
            #Get component lon/lat
            coordinates = [(x, y) for x, y, _ in polygon.exterior.coords]
            Comp_Coords_LonLat.append(coordinates)
            
            #Get component pixels
            Comp_Coords.append([])
            for coord in coordinates:
                if ImgType=='GeoTiff':
                    pt_px=~transform * (coord[0],coord[1])
                    Comp_Coords[index].append(pt_px)
                else:
                    pt_px=transformer.rowcol(coord[0],coord[1])
                    Comp_Coords[index].append(pt_px)
                    
        #Validate data input:
        Type_list=['High Pressure Flare','Low Pressure Flare', 'Heater Treater',
                   'Tank','Well','Compressor','Scrubber','Separator','Tester',
                   'Landfill','Exclusion Zone (road/no structure)',
                   'Exclusion Zone (structure)','Offsite Source','Other']
        
        #check if type is in the pre-populated list (no matter capitalization)
        for comp_val in range(len(Name)):
            item=(Comp_Type[comp_val])
            word_found = False
            for word in Type_list:
                if word.lower() == item.lower():
                    print(Name[comp_val], 'component type valid')
                    word_found = True
                    #If the cases don't match, replace it with matching one.
                    if word != item:
                        Comp_Type[comp_val]=word
                    break
            if word_found==False: #If the word hasn't been found in the list
                print('It looks like there is not an exact match to this component type:',Comp_Type[comp_val])
                component_type_des= input('Select Component: \n'
                                      +'1) High Pressure Flare \n'
                                      +'2) Low Pressure Flare \n'
                                      +'3) Heater Treater \n'
                                      +'4) Tank \n'
                                      +'5) Well \n'
                                      +'6) Compressor \n'
                                      +'7) Scrubber \n'
                                      +'8) Separator \n'
                                      +'9) Tester \n'
                                      +'10) Landfill \n'
                                      +'11) Exclusion Zone (road/no structure) \n'
                                      +'12) Exclusion Zone (structure) \n'
                                      +'13) Offsite Source \n'
                                      +'14) Other \n'
                                      +'Your selection:')
                if component_type_des =='1':
                    component_type= 'High Pressure Flare'
                elif component_type_des =='2':
                    component_type= 'Low Pressure Flare'
                elif component_type_des =='3':
                    component_type= 'Heater Treater'
                elif component_type_des =='4':
                    component_type= 'Tank'
                elif component_type_des =='5':
                    component_type= 'Well'
                elif component_type_des =='6':
                    component_type= 'Compressor'
                elif component_type_des =='7':
                    component_type= 'Scrubber'
                elif component_type_des =='8':
                    component_type= 'Separator'
                elif component_type_des =='9':
                    component_type= 'Tester'
                elif component_type_des =='10':
                    component_type= 'Landfill'
                elif component_type_des =='11':
                    component_type= 'Exclusion Zone (road/no structure)'
                elif component_type_des =='12':
                    component_type= 'Exclusion Zone (structure)'
                elif component_type_des =='13':
                    component_type= 'Offsite Source'
                else:
                    component_type= 'Other'
                
                #Overwrite with correct output
                Comp_Type[comp_val]= component_type
        
        #check if source height is valid
        for comp_val in range(len(Name)):
            item=S_Height[comp_val] #Source height to evaluate
            item2=E_Source[comp_val] #Emission source to evaluate
            
            if item2 != True: #If it's not a source, 
                S_Height[comp_val]=float('nan') #make sure 'source height' is marked as 'nan'
            
            if not (math.isnan(item) or isinstance(item, (int, float))):
                input_SHeight=input('Please enter a valid source height for the component named: '
                                    + Name[comp_val] 
                                    + '\n'
                                    + 'Your input:')
                
    #Store all accumulated data into a data frame, that will be exported to an Excel table.
    Components_DF=pd.DataFrame({'ClientName': Name,
                         'ComponentType': Comp_Type,
                         'SourceHeight': S_Height,
                         'Emission_Source': E_Source,
                         'ComponentCoordsPx': Comp_Coords,
                         'ComponentCoordsLonLat': Comp_Coords_LonLat})
    save_path=str(new_path+'/'+'ComponentInfo.xlsx')
    Components_DF.to_excel(save_path)
    #Note: Final Image showing component locations will be saved as 'Polygon.png'
    
    # Write Site Boundary and Component Shapes to Shapefile, with all info
    
    #Create new folder in which to store site shapefiles
    newpath=new_path+'/SiteShapefiles'
    if os.path.exists(newpath): #Delete/wipe existing folder if it exists & re-write otherwise python crashes.
        shutil.rmtree(newpath)
        os.makedirs(newpath)
    else:
        os.makedirs(newpath)
    
    #STEP 1: Output polygon of site boundary
    Shape_path=newpath+'/SiteBoundary.shp'
    driver = ogr.GetDriverByName('Esri Shapefile') #Set up the shapefile driver
    ds = driver.CreateDataSource(Shape_path) #Create the data source
    srs =  osr.SpatialReference() # create the spatial reference system, WGS84
    srs.ImportFromEPSG(4326)
    layer = ds.CreateLayer('', srs, ogr.wkbPolygon) #Create one layer
    layer.CreateField(ogr.FieldDefn('id', ogr.OFTInteger)) # Add one attribute/ID field
    defn = layer.GetLayerDefn() #Creat ethe feature and set values
    feat = ogr.Feature(defn) # Create a new feature (attribute and geometry)
    feat.SetField('id', 123)
    geom = ogr.CreateGeometryFromWkb(bdry.wkb) # Make a geometry, from site boundary Shapely object
    feat.SetGeometry(geom)
    layer.CreateFeature(feat)
    feat = geom = None  # destroy these
    # Save and close everything
    ds = layer = feat = geom = None
    
    #STEP 2: Output polygon of site components
    for i in range(len(Components_DF)):
        if Components_DF['Emission_Source'][i]: #If something is an emissions source, create shapefile
            Shape_path=newpath+'/'+Components_DF['ClientName'][i]+'.shp' #get name of the polygon
            driver = ogr.GetDriverByName('Esri Shapefile') #Set up the shapefile driver
            ds = driver.CreateDataSource(Shape_path) #Create the data source
            srs =  osr.SpatialReference() # create the spatial reference system, WGS84
            srs.ImportFromEPSG(4326)
            layer = ds.CreateLayer('', srs, ogr.wkbPolygon) #Create one layer
            layer.CreateField(ogr.FieldDefn('ClientName', ogr.OFTString)) # Add one attribute/ID field
            layer.CreateField(ogr.FieldDefn('Type', ogr.OFTString)) # Add one attribute/ID field
            layer.CreateField(ogr.FieldDefn('SrcHght', ogr.OFTInteger64)) # Add one attribute/ID field
            defn = layer.GetLayerDefn() #Createthe feature and set values
            feat = ogr.Feature(defn) # Create a new feature (attribute and geometry)
            feat.SetField('ClientName', Components_DF['ClientName'][i])
            feat.SetField('Type', Components_DF['ComponentType'][i])
            feat.SetField('SrcHght', float(Components_DF['SourceHeight'][i]))
            shape_poly=sh.geometry.Polygon(Components_DF['ComponentCoordsLonLat'][i])
            geom = ogr.CreateGeometryFromWkb(shape_poly.wkb) # Make a geometry
            feat.SetGeometry(geom)
            layer.CreateFeature(feat)
            feat = geom = None  # destroy these
            # Save and close everything
            ds = layer = feat = geom = None
        else: #Otherwise do not create a shapefile
            continue
# endregion


# region Step 5
#%% Step 5: Bring in wind data   
if __name__ == "__main__":
    #Database credentials to use
    influx_username = 'analyticsreader'
    influx_password = 'Al@l1ticsP@55w0rd0521'
    influx_host_url= 'aurainflux.centralus.cloudapp.azure.com'
    dbname='Soofiedata'
    influx_client=InfluxDBClient(host=influx_host_url,port=8086,username=influx_username,password=influx_password,database=dbname)
        
    Upload_wind=input('Select whether would like to upload your own wind data: \n'
                      +'1) Yes. note the specific input format \n'
                      +'2) No, use nearby wind data (if available) \n'
                      +'Your selection:')    
    if Upload_wind=='1':
        wind_dat = filedialog.askopenfilename(filetypes=[(".csv files"," *.csv")])
        
        #HERE WE UPLOAD THE WIND DATA FROM A CSV FILE.
        FieldDat= pd.read_csv(wind_dat)
        FieldDat.columns=['Time','WindSp','WindDir']
        total_count = len(FieldDat) #Total number of data points
        calm_count = len(FieldDat.query("WindSp <= 0.4")) #Number of data points with calm wind condition
        print('Of {} total observations, {} have calm wind conditions.'.format(total_count, calm_count))
        date_begin=datetime.strptime(FieldDat['Time'].iloc[0], "%m/%d/%y %H:%M")
        date_end=datetime.strptime(FieldDat['Time'].iloc[-1], "%m/%d/%y %H:%M")
        if date_begin<date_end:
            print('Data used is from:', date_begin.strftime("%B %d, %Y"), '-', date_end.strftime("%B %d, %Y"))
        else:
            print('Data used is from:', date_end.strftime("%B %d, %Y"), '-', date_begin.strftime("%B %d, %Y"))
        spd_bins=[0, 0.4, 1, 2, 3, 4.5, 6.5, 8.5, 10.5, np.inf]
        spd_labels = speed_labels(spd_bins, units='m/s')
            
        dir_bins=np.linspace(-5,355,num=37)
        dir_labels=np.linspace(0,350,num=36)
    
        for i in range(len(FieldDat)):
            if FieldDat.iloc[i]['WindDir']>=355:
                FieldDat.iloc[i]['WindDir']=FieldDat.iloc[i]['WindDir']-360
    
        rose = (
            FieldDat.assign(WindSpd_bins=lambda df:
                    pd.cut(df['WindSp'], bins=spd_bins, labels=spd_labels, right=True)
                 )
                .assign(WindDir_bins=lambda df:
                    pd.cut(df['WindDir'], bins=dir_bins, labels=dir_labels, right=False)
                 )
                .replace({'WindDir_bins': {360: 0}})
                .groupby(by=['WindSpd_bins', 'WindDir_bins'],observed=False)
                .size()
                .unstack(level='WindSpd_bins')
                .fillna(0)
                .assign(calm=lambda df: calm_count / len(df))
                .sort_index(axis=1)
                .map(lambda x: x / total_count * 100)
        )
            
        #Plot wind rose:
        directions=np.arange(0,360,10)
        fig=wind_rose(rose,directions)
        fig.savefig(new_path+'/WindRose.png')
        #Change data for simulation runs
        Wind_Dat=rose.drop('calm', axis=1)
        Wind_Dat.reset_index(inplace=True) #Make index values into a column of data frame so you can work with values 
        #Rename columns
        Wind_Dat=Wind_Dat.rename(columns={'WindDir_bins':'WDIR','0.4 - 1 m/s':0.5, '1 - 2 m/s':1.5, '2 - 3 m/s':2.5, 
                                 '3 - 4.5 m/s':3.75, '4.5 - 6.5 m/s':5.5, '6.5 - 8.5 m/s':7.5, '8.5 - 10.5 m/s':9.5, '>10.5 m/s':11})
    
        Col_Val=[]
        Row_Val=[]
        Likely_Val=[]
        #Go through the data frame, and extract values, rows, and cols for each point
        for i in range(Wind_Dat.shape[1]-1): #For each column
            for o in range(Wind_Dat.shape[0]): #For each row
                Col_Val.append(Wind_Dat.columns[i+1])
                Row_Val.append(Wind_Dat.iloc[o,0])
                Likely_Val.append(float(Wind_Dat.iloc[o,i+1]))
    
        WTriSize=[]
        for i in range(len(Col_Val)):
            if Col_Val[i]==0.5:
                WTriSize.append(25.73)
            elif Col_Val[i]==1.5:
                WTriSize.append(20.37)
            elif Col_Val[i]==2.5:
                WTriSize.append(16.28)
            elif Col_Val[i]==3.75:
                WTriSize.append(12.33)
            elif Col_Val[i]==5.5:
                WTriSize.append(10.48)
            elif Col_Val[i]==7.5:
                WTriSize.append(8.74)
            elif Col_Val[i]==9.5:
                WTriSize.append(7.66)
            elif Col_Val[i]==11:
                WTriSize.append(6.93)
            else:
                WTriSize.append(0)
    
        wind_list = pd.DataFrame(
            {'Wsp_MpS': Col_Val,
             'Wdir': Row_Val,
             'WTri_Size':WTriSize,
             'Percentage': Likely_Val
            })
    
        #Sort wind data by descending order
        wind_list = wind_list[wind_list['Percentage'] !=0]
        wind_list=wind_list.sort_values(by=['Percentage'], ascending=False)
        wind_list = wind_list.reset_index(drop=True)
    
        #Get cumulative precentage   
        test=wind_list.cumsum()
        wind_list['Cumulative_Sum']=test['Percentage']
    elif Upload_wind=='2':
        #First, find all wind sites within a given radius of the site.
        
        #CREATE SEARCH RADIUS
        wind_stations=pd.read_excel(r'StationLookup2.xlsx') #Read in data of location of all online wind data
        CentroidPt=PlacementPoly.centroid #Get site center point
        Wind_Search_Rad=input('Enter wind search radius (in km) from site (as default we recommend 5km):')
        rad_meas=dist_15/15*1000*float(Wind_Search_Rad) #Using 15m long/lat dist, get long/lat dist equivalent to 5 km (ratios used: 1000m to 1km, 5km, dist to 15m)
        circle=CentroidPt.buffer(rad_meas) #Create a 5km radius polygon from center of site
        
        ############# BEGIN Data From Online Airport Wind Stations ############
        
        #Create locations to fill in of places within 5km of point
        Location_StID=[]
        Location_Name=[]
        Location_Lat=[]
        Location_Lon=[]
        Location_NTWK=[]
        
        #Loop through all stations, and see if they fall within 5km radius
        for idx in wind_stations.index:
            point2=sh.geometry.Point(wind_stations['lon'][idx],wind_stations['lat'][idx]) #Make e/ wind station a point
            if point2.within(circle)==True: #Check if site coordinate is within 5km radius polygon
                Location_StID.append(wind_stations['stid'][idx])
                Location_Name.append(wind_stations['station_name'][idx])
                Location_Lat.append(wind_stations['lat'][idx])
                Location_Lon.append(wind_stations['lon'][idx])
                Location_NTWK.append(wind_stations['iem_network'][idx])
            else:
                continue
        
        #Calculate distance between site and stations within polygon
        Distance_Stations=[]
        if len(Location_Name)>0:
            for i in range(len(Location_Name)):
                _,_,dist_2 = geod.inv(CentroidPt.coords[0][0],CentroidPt.coords[0][1],Location_Lon[i],Location_Lat[i])
                Distance_Stations.append(dist_2/1000) #Distance in km
        
        #Create final data frame of online data within search radius
        Site_Type=['Online']*len(Location_Name) #designate data source
        OnlineWind_InRad=[]
        OnlineWind_InRad=pd.DataFrame({'SiteName': Location_Name,
                                'SiteID': Location_StID,
                                'SiteLon': Location_Lon,
                                'SiteLat': Location_Lat,
                                'LocationNTWK': Location_NTWK,
                                'Site_Type': Site_Type,
                                'Distance': Distance_Stations,
                                })
        ############# END Data From Online Airport Wind Stations ############
        
        ############# BEGIN Data From ChampionX Sites ############
        
        #Here we are going to add any ChampionX sites. First we are going to create a list of all active sites.
        df=json.load(open(r'soofie-active-sites.json')) #Load ChampionX sites information
        
        #Declare blank variables
        Site_ID=[]
        Site_Name=[]
        Site_X=[]
        Site_Y=[]
        #Get list of site center coords, and site name, and site id
        for i in range(len(df)): #For each ChampionX site,
            dat=df[i] #query into specific site
            if dat['active']==True and len(dat['devices'])>0: #only use active sites that have SOOFIE sensors
                Site_ID.append(dat['id']) #get site ID
                Site_Name.append(dat['site']) #get site name
                dev_pts = [] #Create empty list of device points
                for device in dat['devices']: #query into each device, and get lat/long
                    dev_pts.append((float(device['longitude']),float(device['latitude'])))
                if len(dev_pts)>2: #if >2 devices at site, use center of all dev. locations for site center
                    site_ctr=Polygon([[p[0],p[1]] for p in dev_pts]).centroid
                else: #if <=2 pts, use the first location of a device as the site center
                    site_ctr=Point(dev_pts[0])
                Site_X.append(site_ctr.x) #add x and y locations as the site center locations.
                Site_Y.append(site_ctr.y)
            else:
                continue
        
        #Create a dataframe of all of the ChampionX site locations.    
        ChX_Site_Loc=[]
        ChX_Site_Loc=pd.DataFrame({'SiteName': Site_Name,
                                'SiteID': Site_ID,
                                'SiteLon': Site_X,
                                'SiteLat': Site_Y,
                                })
        
        #Loop through all ChX stations, and see if they fall within 5km radius
        ChX_Site_ID=[]
        ChX_Site_Name=[]
        ChX_Site_X=[]
        ChX_Site_Y=[]
        for idx2 in ChX_Site_Loc.index:
            pointChX=sh.geometry.Point(ChX_Site_Loc['SiteLon'][idx2],ChX_Site_Loc['SiteLat'][idx2]) #Make e/ wind station a point
            if pointChX.within(circle)==True: #Check if site coordinate is within 5km radius polygon
                ChX_Site_ID.append(ChX_Site_Loc['SiteID'][idx2])
                ChX_Site_Name.append(ChX_Site_Loc['SiteName'][idx2])
                ChX_Site_X.append(ChX_Site_Loc['SiteLon'][idx2])
                ChX_Site_Y.append(ChX_Site_Loc['SiteLat'][idx2])
            else:
                continue

        #Calculate distance between site center and ChampionX sites
        Distance_StationsChX=[]
        if len(ChX_Site_Name)>0:
            for i in range(len(ChX_Site_Name)):
                _,_,dist_ChX = geod.inv(CentroidPt.coords[0][0],CentroidPt.coords[0][1],ChX_Site_X[i],ChX_Site_Y[i])
                Distance_StationsChX.append(dist_ChX/1000) #Distance in km
        
        #Create final data frame of ChampionX sites within search radius
        Site_TypeChX=['ChX']*len(ChX_Site_Name) #designate data source
        ChX_InRad=[]
        ChX_InRad=pd.DataFrame({'SiteName': ChX_Site_Name,
                                'SiteID': ChX_Site_ID,
                                'SiteLon': ChX_Site_X,
                                'SiteLat': ChX_Site_Y,
                                'Site_Type': Site_TypeChX,
                                'Distance': Distance_StationsChX,
                                })
        ############# END Data From ChampionX Sites ############
        
        #Merge data of ChampionX and online data.
        mergeframes=[ChX_InRad, OnlineWind_InRad]
        AllWindData=pd.concat(mergeframes)
        AllWindData=AllWindData.sort_values(by=["Distance"],ascending=[True])
        AllWindData = AllWindData.reset_index(drop=True)
        No_Wind=False #designate that there is wind data to be used (only changed if no wind data is available, see below)
        #Print out how much data is available, and distance from site.
        if len(AllWindData)==0:
            print('No wind data within',Wind_Search_Rad,'km of site found')
            No_Wind=True #designate that no wind data to use exists
        else:
            print(str(len(AllWindData)),'location(s) with wind data found within',str(Wind_Search_Rad),'km of site')
        
            #First we want to check that we are using a site with enough wind data.
            for idx_val in range(len(AllWindData)):
                if AllWindData['Site_Type'][idx_val]=='Online': #The online site automatically has >1 years worth of data. If ChX data, check data length
                    print('Location closest to the site is:',str(AllWindData['SiteName'][idx_val]),',',str(int(AllWindData['Distance'][idx_val])),'km away from site')
                    break
                else:# Otherwise it is a ChampionX site
                    CurrentTime=datetime.now(timezone.utc) #Get current time
                    start_year = CurrentTime.year-1         #Get start year (today's year - 1 year)
                    LastYr=CurrentTime.replace(year=start_year) #Post as last year as beginning of data collection
                    CurrentTime_Fmt = CurrentTime.strftime("%Y-%m-%dT%H:%M") #reformat
                    LastYr_Fmt = LastYr.strftime("%Y-%m-%dT%H:%M") #reformat
                    CurrentTime_Fmt=CurrentTime_Fmt + ':00Z' #reformat for influx database query
                    LastYr_Fmt=LastYr_Fmt + ':00Z' #reformat for influx database query
                    #Set up Influx DB Query
                    # site_name='METEC 2023'
                    # query_where='select C9,C10,C11 from  Readings WHERE assetname=$assetname and time >= $time1 and time < $time2 ;'
                    # bind_params = {'assetname':site_name,
                    #                 'time1':LastYr_Fmt,
                    #                 'time2':CurrentTime_Fmt}
                    query_where='select C9,C10,C11 from  Readings WHERE assetid=$assetid and time >= $time1 and time < $time2 ;' #Create query, querying for wind direction, WDStd Dev, and Wind Speed
                        
                    bind_params = {'assetid':AllWindData['SiteID'][idx_val],
                                    'time1':LastYr_Fmt,
                                    'time2':CurrentTime_Fmt}
                    #Get raw data
                    influx_data=influx_client.query(query_where,bind_params=bind_params) #Access the data from the database    
                    
                    #Parse data out
                    records=[]
                    for site_data in json.loads(json.dumps(influx_data.raw)).get('series')[0].get("values"):
                        records.append(site_data)
                    if len(records)<390000: #If data is less than ~3/4 year, move on to next-closest station (e.g. next idx_val)
                        if idx_val==len(AllWindData)-1: #If you got to the last station and it doesn't have enough data,
                            print('There are no sites with sufficient wind data within 5km of site')
                            No_Wind=True #designate that no wind data to use exists
                        else: #Otherwise go to the next-closest station.
                            continue
                    else:
                        print('Location closest to the site is: a ChampionX site,',str(int(AllWindData['Distance'][idx_val])),'km away from site')
                        break
        
            #If from championX site, get site data
            if AllWindData['Site_Type'][idx_val]=='ChX' and No_Wind==False:
                    
                FieldDat=pd.DataFrame(records[:])
                FieldDat.columns=['Time','WindDir','WindSp','WindDirSD']
                
                total_count = len(FieldDat) #Total number of data points
                calm_count = len(FieldDat.query("WindSp <= 0.4")) #Number of data points with calm wind condition
                print('Of {} total observations, {} have calm wind conditions.'.format(total_count, calm_count))
                date_begin=datetime.strptime(FieldDat['Time'].iloc[0], "%Y-%m-%dT%H:%M:%SZ")
                date_end=datetime.strptime(FieldDat['Time'].iloc[-1], "%Y-%m-%dT%H:%M:%SZ")
                print('Data used is from:', date_begin.strftime("%B %d, %Y"), '-', date_end.strftime("%B %d, %Y"))
                spd_bins=[0, 0.4, 1, 2, 3, 4.5, 6.5, 8.5, 10.5, np.inf]
                spd_labels = speed_labels(spd_bins, units='m/s')
            
                dir_bins=np.linspace(-5,355,num=37)
                dir_labels=np.linspace(0,350,num=36)
                
                for i in range(len(FieldDat)):
                    if FieldDat.iloc[i]['WindDir']>=355:
                        FieldDat.iloc[i]['WindDir']=FieldDat.iloc[i]['WindDir']-360
                
                rose = (
                    FieldDat.assign(WindSpd_bins=lambda df:
                            pd.cut(df['WindSp'], bins=spd_bins, labels=spd_labels, right=True)
                         )
                        .assign(WindDir_bins=lambda df:
                            pd.cut(df['WindDir'], bins=dir_bins, labels=dir_labels, right=False)
                         )
                        .replace({'WindDir_bins': {360: 0}})
                        .groupby(by=['WindSpd_bins', 'WindDir_bins'],observed=False)
                        .size()
                        .unstack(level='WindSpd_bins')
                        .fillna(0)
                        .assign(calm=lambda df: calm_count / len(df))
                        .sort_index(axis=1)
                        .applymap(lambda x: x / total_count * 100)
                )
                    
                #Plot wind rose:
                directions=np.arange(0,360,10)
                fig=wind_rose(rose,directions)
                fig.savefig(new_path+'/WindRose.png')
                
                #Change data for simulation runs
                Wind_Dat=rose.drop('calm', axis=1)
                Wind_Dat.reset_index(inplace=True) #Make index values into a column of data frame so you can work with values 
                #Rename columns
                Wind_Dat=Wind_Dat.rename(columns={'WindDir_bins':'WDIR','0.4 - 1 m/s':0.5, '1 - 2 m/s':1.5, '2 - 3 m/s':2.5, 
                                         '3 - 4.5 m/s':3.75, '4.5 - 6.5 m/s':5.5, '6.5 - 8.5 m/s':7.5, '8.5 - 10.5 m/s':9.5, '>10.5 m/s':11})
                
                Col_Val=[]
                Row_Val=[]
                Likely_Val=[]
                #Go through the data frame, and extract values, rows, and cols for each point
                for i in range(Wind_Dat.shape[1]-1): #For each column
                    for o in range(Wind_Dat.shape[0]): #For each row
                        Col_Val.append(Wind_Dat.columns[i+1])
                        Row_Val.append(Wind_Dat.iloc[o,0])
                        Likely_Val.append(float(Wind_Dat.iloc[o,i+1]))
                
                WTriSize=[]
                for i in range(len(Col_Val)):
                    if Col_Val[i]==0.5:
                        WTriSize.append(25.73)
                    elif Col_Val[i]==1.5:
                        WTriSize.append(20.37)
                    elif Col_Val[i]==2.5:
                        WTriSize.append(16.28)
                    elif Col_Val[i]==3.75:
                        WTriSize.append(12.33)
                    elif Col_Val[i]==5.5:
                        WTriSize.append(10.48)
                    elif Col_Val[i]==7.5:
                        WTriSize.append(8.74)
                    elif Col_Val[i]==9.5:
                        WTriSize.append(7.66)
                    elif Col_Val[i]==11:
                        WTriSize.append(6.93)
                    else:
                        WTriSize.append(0)
                
                wind_list = pd.DataFrame(
                    {'Wsp_MpS': Col_Val,
                     'Wdir': Row_Val,
                     'WTri_Size':WTriSize,
                     'Percentage': Likely_Val
                    })
                
                #Sort wind data by descending order
                wind_list = wind_list[wind_list['Percentage'] !=0]
                wind_list=wind_list.sort_values(by=['Percentage'], ascending=False)
                wind_list = wind_list.reset_index(drop=True)
                
                #Get cumulative precentage   
                test=wind_list.cumsum()
                wind_list['Cumulative_Sum']=test['Percentage']
            #If from online source, create URL and pull data from there.  
            elif AllWindData['Site_Type'][idx_val]=='Online' and No_Wind==False:
                #Fill the URL with the appropriate data info
                URL1='https://mesonet.agron.iastate.edu/cgi-bin/mywindrose.py?nsector=36&station='
                URL2=str(AllWindData['SiteID'][idx_val])
                URL3='&network='
                URL4=str(AllWindData['LocationNTWK'][idx_val])
                URL5='&year1=1970&day1=1&day2=1&month2=1&minute1=0&minute2=0&units=mph&justdata=true&hour1=0&hour2=0&year2=2024&month1=1'
                URL=URL1+URL2+URL3+URL4+URL5
                
                #Pull data from online
                r = requests.get(URL) 
                 
                # Parsing the HTML text you get from online, and make data into a data frame.
                #Data is in terms of proportion.
                soup = BeautifulSoup(r.content, 'html.parser')
                text = soup.get_text() #Extract text string from webpage
                text_split = text.split("+") #Extract text of the data
                data=text_split[1]
                split_data = [row.split(',') for row in data.split('\n')]
                meso_df = pd.DataFrame(split_data, columns=['WDIR','DR','1.56','2.68','3.8','5.59','7.82','8.94']) #Columns in MPH, changed to median of range, and to m/s
                meso_df=meso_df.drop('DR', axis=1)
                meso_df=meso_df.drop(0,axis=0)
                meso_df=meso_df.drop(len(meso_df),axis=0)
                meso_df['WDIR']=np.linspace(0,350,36) #Assign wind direction value to column
                
                #Get length of dataset of wind data
                dat_info=text_split[0]
                dat_len=dat_info.splitlines()[2]
                dat_len=dat_len[2:]
                print('Data used is from:', dat_len)
                RoseURL=URL1+URL2+URL3+URL4
                print('URL of wind rose: ',RoseURL)
                
                Col_Val=[]
                Row_Val=[]
                Likely_Val=[]
                #Go through the data frame, and extract values, rows, and cols for each point
                for i in range(meso_df.shape[1]-1):
                    for o in range(meso_df.shape[0]):
                        Col_Val.append(meso_df.columns[i+1])
                        Row_Val.append(meso_df.iloc[o,0])
                        Likely_Val.append(float(meso_df.iloc[o,i+1]))
                WTriSize=[]
                for i in range(len(Col_Val)):
                    if float(Col_Val[i])<1.56:
                        WTriSize.append(25.73)
                    elif float(Col_Val[i])==1.56:
                        WTriSize.append(20.37)
                    elif float(Col_Val[i])==2.68:
                        WTriSize.append(16.28)
                    elif float(Col_Val[i])==3.8:
                        WTriSize.append(12.33)
                    elif float(Col_Val[i])==5.59:
                        WTriSize.append(10.48)
                    elif float(Col_Val[i])==7.82:
                        WTriSize.append(8.74)
                    elif float(Col_Val[i])==8.94:
                        WTriSize.append(7.66)
                    elif float(Col_Val[i])>8.94:
                        WTriSize.append(6.93)
                    else:
                        WTriSize.append(0)
                        
                wind_list = pd.DataFrame(
                    {'Wsp_MpS': Col_Val,
                     'Wdir': Row_Val,
                     'WTri_Size':WTriSize,
                     'Percentage': Likely_Val
                    })       
                for l in range(len(wind_list)):
                    if wind_list.loc[l, 'Percentage']==0:
                        wind_list.loc[l, 'Percentage']=0.01
                
                #Sort wind data by descending order
                wind_list=wind_list.sort_values(by=['Percentage'], ascending=False)
                wind_list = wind_list.reset_index(drop=True)
                
                #Get cumulative precentage   
                test=wind_list.cumsum()
                wind_list['Cumulative_Sum']=test['Percentage']
            else:
                wind_list=[]

# endregion

# region Step 6
#%% Step 6: Create a grid for the site
if __name__ == "__main__":

    #Step 1: PREP CREATING GRID
    print('Creating Site Grid')
    #get most SW point

    #CHECK IF YOU WANT TO INCLUDE OFFSITE SOURCE INTO GRID
    if int(ask_offsite)==1:
        xx,yy=OffSitebdry.exterior.coords.xy
        SWpt_X,SWpt_Y=FindSWPt(xx,yy,OffSitebdry)
        #get max site length
        maxDist=MaxSiteDist(OffSitebdry)
        OffSitebdry=OffSitebdry
    else:
        xx,yy=bdry.exterior.coords.xy
        SWpt_X,SWpt_Y=FindSWPt(xx,yy,bdry)
        #get max site length
        maxDist=MaxSiteDist(bdry)
        OffSitebdry=bdry

    #GET MOST SOUTHWEST POINT
    #Declare starting point a bit southwest of that point (to accommodate more western points)
    Lon1,Lat1,_=geod.fwd(SWpt_X,SWpt_Y,225,int(maxDist))

    #Designate resolution of the grid
    #SOURCE RESOLUTION
    source_grid_res=3 #Source grid resolution is 3 meters

    #PLACEMENT RESOLUTION
    grid_res=int(input('Enter the grid resolution (in meters) for sensor placement. \n'
                   +'Your selection:'))
    #SOURCE STEP SIZE
    step_size_source=dist_15/15*source_grid_res #calc step size in decimal degrees
    num_points_source=int((maxDist*3)/source_grid_res)#want grid dist, using xm (resolution) spacing

    #PLACEMENT STEP SIZE
    #Get step size and number of points to make
    step_size=dist_15/15*grid_res #calc step size in decimal degrees
    num_points=int((maxDist*3)/grid_res)#want grid dist, using xm (resolution) spacing

    #SOURCE CREATE GRID
    #Create grid
    x_range_source = np.arange(Lon1, Lon1+(num_points_source*step_size_source), step_size_source)
    y_range_source = np.arange(Lat1, Lat1+(num_points_source*step_size_source), step_size_source)
    grid_points_source = np.array([[x, y] for x in x_range_source for y in y_range_source])  # cartesian prod

    #Get grid points
    x1_grid_source = grid_points_source[:,0]
    y1_grid_source = grid_points_source[:,1]

    #PLACEMENT CREATE GRID
    #Create grid
    x_range = np.arange(Lon1, Lon1+(num_points*step_size), step_size)
    y_range = np.arange(Lat1, Lat1+(num_points*step_size), step_size)
    grid_points = np.array([[x, y] for x in x_range for y in y_range])  # cartesian prod

    #Get grid points
    x1_grid = grid_points[:,0]
    y1_grid = grid_points[:,1]

    #Next Step: CREATE GRID FOR SENSOR PLACEMENT
    if len(wind_list)==0:
        Placement_Type=1
    else:
        Placement_Type=int(input('Select the type of SOOFIE placement: \n'
                         +'1) Fenceline \n'
                         +'2) Internal (only if you have wind data)\n'
                         +'Your selection:'))
    if Placement_Type==1:
        Placement_Selection='Fenceline'
    else:
        Placement_Selection='Internal'
        
    #Test to see what points of mesh grid are within site limits, and get point locations within site
    x_grid=[]
    y_grid=[]
    within_site_x=[]
    within_site_y=[]
    for i in range(len(x1_grid)): #for each point,
        #print(i)
        point1=sh.geometry.Point(x1_grid[i],y1_grid[i]) #make each coordinate a point
        if point1.within(bdry)==True:
            within_site_x.append(x1_grid[i])
            within_site_y.append(y1_grid[i])
            if point1.within(bdry)==True and Placement_Selection=='Internal': #If internal placement options
                x_grid.append(x1_grid[i])
                y_grid.append(y1_grid[i])
            if point1.within(PlacementPoly)==True and Placement_Selection=='Fenceline': #Check if coordinate is fenceline polygon
                x_grid.append(x1_grid[i])
                y_grid.append(y1_grid[i])
        else:
            continue

    #Combine all points that are within the placement area for the initial placement grid:
    placement_grid=np.vstack((x_grid,y_grid)).transpose(1,0)
    placement_grid = tuple(map(tuple, placement_grid)) #Original placement grid within site boundaries, 15m buffer from site perimeter

    #Get all grid coordinates that are contained in component buffer
    x_grid_comp_buff=[]
    y_grid_comp_buff=[]
    for l in range(len(Components_DF)): #Loop through e/ site component
        comp_coords=Components_DF['ComponentCoordsLonLat'][l] #Go through and select component
        poly2=sh.geometry.Polygon(comp_coords)#Make a geometry for that particular component
        if Components_DF['Emission_Source'][l]==True: #If component is an emissions source,
            BuffHeight=float(Components_DF['SourceHeight'][l]*1.5)
            TempPoly_Buff=sh.buffer(poly2,(dist_15/15*BuffHeight),join_style="mitre") #Then create a x-m buffer around component
        elif Components_DF['ComponentType'][l]=='Exclusion Zone (structure)':
            BuffHeight=float(5)
            TempPoly_Buff=sh.buffer(poly2,(dist_15/15*BuffHeight),join_style="mitre") #Then create a 4-m buffer around component
        else:
            TempPoly_Buff=poly2 #If it's not an emissions ource (e.g. road), then just use original component polygon lines to avoid
        for n in range(len(x_grid)): #loop through all points within placement grid
            point1=sh.geometry.Point(x_grid[n],y_grid[n]) #make each coordinate in placement grid a point
            if point1.within(TempPoly_Buff)==True: #Check if point on grid is within these placemes to avoid
                x_grid_comp_buff.append(x_grid[n]) #If it is, add to the x-grid_comp_buff layer
                y_grid_comp_buff.append(y_grid[n])
            else:
                continue
            
    #Create 'buffer' grid...e.g. all points within placement polygon to avoid
    buff=np.vstack((x_grid_comp_buff,y_grid_comp_buff)).transpose(1,0)
    buff = tuple(map(tuple, buff))

    #Get all points within site placement area, not within adequate distance of component buffer.
    newlist=[]
    for coords in placement_grid:
        if coords not in buff:
            newlist.append(coords)
    #Extract the resulting x and y coordinates of potential placement locations
    newlist_x,newlist_y=zip(*newlist)

    #Create grid for source location
    #Test to see what points of mesh grid are within Off-site boundary, and get point locations
    OffSite_X=[]
    OffSite_Y=[]
    for i in range(len(x1_grid_source)): #for each point,
        point1=sh.geometry.Point(x1_grid_source[i],y1_grid_source[i]) #make each coordinate a point
        if point1.within(OffSitebdry)==True:
            OffSite_X.append(x1_grid_source[i])
            OffSite_Y.append(y1_grid_source[i])
        else:
            continue
    
    grid_pts=[]
    Comp_Name=[]
    Comp_Type2=[]
    Emis_Source=[]
    for a in range(len(Components_DF)): #For each component
        temp_grid_pts_x=[]
        temp_grid_pts_y=[]
        if Components_DF['Emission_Source'][a]==False: #If the component is NOT an emission source
            temp_grid_pts=[] #Then fill with null values
            Emis_Source.append(0)
            #continue
        else: #If the component IS an emission source
            comp_coords=Components_DF['ComponentCoordsLonLat'][a] #get the lon/lat coordinates of component
            poly2=sh.geometry.Polygon(comp_coords) #make component polygon
            Emis_Source.append(1)
            for i in range(len(OffSite_X)): #go to original site-wide grid points
                #print(a,i)
                point1=sh.geometry.Point(OffSite_X[i],OffSite_Y[i]) #make each grid point coordinate a shapely point
                if point1.within(poly2)==True: #Check if coordinate is in component #If the point lies inside the component geometry
                    temp_grid_pts_x.append(OffSite_X[i]) #then add its coordinates to the temp grid points
                    temp_grid_pts_y.append(OffSite_Y[i])
                else:
                    continue #Otherwise, go to the next grid point
            temp_grid_pts=np.vstack((temp_grid_pts_x,temp_grid_pts_y)).transpose(1,0) #Combine all x and y coordinates into one variable
            if len(temp_grid_pts)==0:
                result_grid=([0] * len(newlist_x))
                pt_x,pt_y,_=FindClosestPt(newlist_x,newlist_y,poly2.centroid.x,poly2.centroid.y,result_grid,windTriID=None,windTriPct=None) #find closest pt to center of polygon
                temp_grid_pts=([[pt_x,pt_y]])
        grid_pts.append(temp_grid_pts) #this is a list of pts that lie within each component.
        Comp_Name.append(Components_DF['ClientName'][a])
        Comp_Type2.append(Components_DF['ComponentType'][a])
    Components_DF['GridPts']=grid_pts #Add points to data frame
    
    #Get index of values to not consider in dataframe
    del_idx=[]
    for i in range(len(Components_DF)):
        if len(Components_DF.iloc[i].GridPts)==0:
            del_idx.append(i)
        else:
            continue
    TempDF=Components_DF.copy()
    TempDF=TempDF.drop(del_idx, axis=0)

# endregion


# region Step 6A
#%%Step 6A: Define Weighting
if __name__ == "__main__":
    if len(wind_list)!=0:
        #Designate whether you would like equal or differential weighting of likelihood of leak
        wght_q=input('Select whether you want the likelihood of leak to be equal across all components or to modify it: \n'
                     '1. Footprint-based weighting (default) \n'
                     '2. Even component distribution \n'
                     '3. Change weighting of components \n'
                     'Your input:')
        if wght_q=='1':
            TempDF['Wght']=[1]*len(TempDF)
        elif wght_q=='2':
            wght_entry=[]
            for i in range(len(TempDF)):
                wght_entry.append((1/sum(Components_DF['Emission_Source'])))
            TempDF['Wght']=wght_entry
        elif wght_q=='3':
            wght_entry=[]
            wht_entrymod=[]
            for i in range(len(TempDF)):
                wght_q_entry=input('Select weight for component named\''+TempDF.iloc[i]['ClientName']+'\' of type \''+TempDF.iloc[i]['ComponentType']+'\'\n Enter weighting value here:')
                wght_entry.append(float(wght_q_entry))
            sum_whts=sum(wght_entry)
            for j in range(len(TempDF)):
                wht_entrymod.append(wght_entry[j]/sum_whts)#the weight of e/ equipment
            TempDF['Wght']=wht_entrymod
        else:
            print('oops, wrong entry. Everything will be weighted evenly (default).')
            TempDF['Wght']=[1]*len(TempDF)

        #Combine all grid points into one variable of lat/long:
        SrcPts_Grid=[]
        SrcPt_SumTemp=[]
        for i in range(len(TempDF)):
            val1=TempDF.iloc[i]
            val2=TempDF.iloc[i]['Wght']
            for j in range(len(val1['GridPts'])):
                if wght_q=='2' or wght_q=='3':
                    SrcPts_Grid.append([val1['GridPts'][j][0],val1['GridPts'][j][1],i,(val2/len(val1['GridPts']))])
                else:
                    SrcPts_Grid.append([val1['GridPts'][j][0],val1['GridPts'][j][1],i,val2])
                    SrcPt_SumTemp.append(val2)
        SrcPt_Sum=sum(SrcPt_SumTemp)
        for i in range(len(SrcPts_Grid)):
            if wght_q=='2' or wght_q=='3':
                SrcPts_Grid[i].append(SrcPts_Grid[i][3])
            else:
                SrcPts_Grid[i].append(SrcPts_Grid[i][3]/SrcPt_Sum)

#%% Plot the site grid and source points you will be using for the simulations
if __name__ == "__main__":
    #Plotting
    plt.figure()
    #plt.scatter(x1_grid,y1_grid,s=1,marker='.') #all grid
    plt.plot(*bdry.exterior.xy,'blue')
    #plt.scatter(within_site_x,within_site_y,s=1,marker='.')
    #plt.scatter(OffSite_X,OffSite_Y,s=10,marker='.',color='blue')
    #plt.scatter(x_grid,y_grid,s=1,marker='.') #Plot placement grid
    plt.scatter(newlist_x,newlist_y,s=10,marker='.',color='orange')#plot remaining/clipped grid after buffer
    for i in range(len(SrcPts_Grid)):
        plt.scatter(SrcPts_Grid[i][0],SrcPts_Grid[i][1],s=10,marker='.',color='red')
    #plt.plot(*PlacementPoly.exterior.xy,'blue') #Outer placement polygon
    #plt.plot(Int*Poly_lonlat.exterior.xy,'blue') #Inner placement polygon
    #plt.scatter(sample_x,sample_y,s=10,marker='.',color='red') #Plot points that are within a given component
    #Graph polygon of all components
    for i in range(len(Components_DF)):
        comp_coords=Components_DF['ComponentCoordsLonLat'][i]
        poly2=sh.geometry.Polygon(comp_coords)
        if Components_DF['Emission_Source'][i]==True:
            TempPoly_Buff=poly2
            #TempPoly_Buff=shapely.buffer(poly2,dist,join_style="mitre")
            x1,y1=TempPoly_Buff.exterior.xy
            plt.plot(x1,y1,color='red',linewidth=.5)
        else:
            TempPoly_Buff=poly2
            #TempPoly_Buff=poly2
            x1,y1=TempPoly_Buff.exterior.xy
            plt.plot(x1,y1,color='gray',linewidth=.5)
    plt.axis('equal') #Set axis as equal
    plt.xticks([])
    plt.yticks([])
    plt.savefig('plot_with_transparent_background.png', transparent=True)
    plt.show()

# endregion

# region Step 6B
#%% Step 6B: Define distance of detection.
if __name__ == "__main__":
    if len(wind_list)!=0:
        LengthOfDetection=input('Select the length of detection you would like to use: \n'
                                 +'1) 100m \n'
                                 +'2) 200m \n'
                                 +'3) 300m \n'
                                 +'4) Other \n'
                                 +'Enter your selection here:')
        
        if LengthOfDetection=='1':
            Detection_Len=100
        elif LengthOfDetection=='2':
            Detection_Len=200
        elif LengthOfDetection=='3':
            Detection_Len=300
        else: #LengthOfDetection=='4' or mistype
            Det_input=input('enter custom amount (in meters):')
            Detection_Len=int(Det_input)
        
        Obs_Consideration=input('Select whether you would like to consider obstructions: \n'
                                 +'1) Yes \n'
                                 +'2) No \n'
                                 +'Enter your selection here:')
# endregion

# region Step 7
#%% Step 7: Run Wind Simulations
if __name__ == "__main__":
    if len(wind_list)!=0:
        # Define the number of processes
        num_processes = multiprocessing.cpu_count()
        #num_processes=1
        # Divide wind list into chunks for parallel processing
        chunk_size = max(1, len(wind_list) // num_processes)
        wind_chunks = [wind_list[i:i+chunk_size] for i in range(0, len(wind_list), chunk_size)]
    
        # Create a multiprocessing pool
        pool = multiprocessing.Pool(processes=num_processes)
        
        # Parallel processing for each wind chunk
        results = []
        
        for wind_chunk in wind_chunks:
            result = pool.apply_async(process_wind_condition, args=(wind_chunk, SrcPts_Grid, Obs_Consideration, Detection_Len, newlist_x, newlist_y, Components_DF))
            results.append(result)
    
        # Close the pool and wait for all processes to finish
        pool.close()
        pool.join()
        
        # Extract results from multiprocessing pool
        final_result = []
        for result in results:
            final_result.extend(result.get())
            
        #convert to dataframe
        final_df = pd.DataFrame(final_result, columns=['newlist_x', 'newlist_y','sim_grid_ID','sim_grid_Val'])
        subset_df = final_df[['newlist_x', 'newlist_y']]
        #get unique x and y values
        unique_combinations = subset_df.drop_duplicates(subset=['newlist_x', 'newlist_y'])
        
        # Create an empty list to store the appended WindID and WindVal
        appended_values = []
        
        # Group final_df by 'newlist_x' and 'newlist_y' and aggregate WindID and WindVal into lists
        GridDF = final_df.groupby(['newlist_x', 'newlist_y']).agg({'sim_grid_ID': list, 'sim_grid_Val': list}).reset_index()
        
        # Rename the columns for clarity
        GridDF.columns = ['newlist_x', 'newlist_y', 'sim_grid_ID', 'sim_grid_Val']
        
        # Remove empty strings ('') from 'WindID_List' and zeros (0) from 'WindVal_List'
        GridDF['sim_grid_ID'] = [[value for value in sublist if value != ''] for sublist in GridDF['sim_grid_ID']]
        GridDF['sim_grid_Val'] = [[value for value in sublist if value != 0] for sublist in GridDF['sim_grid_Val']]
    
        # Get the sum of the 'sim_grid_Val' column
        GridDF['result_grid'] = GridDF['sim_grid_Val'].apply(sum_of_list)
        
        #Sort GridDF from highest percent of detection to lowest
        GridDF = GridDF.sort_values(by='result_grid', ascending=False)

# region Step 7A
#%% Step 7A: Create initial percentage graph and load simulation code
if __name__ == "__main__":
    if len(wind_list)!=0:
        result_grid=GridDF['result_grid']
        #Set max and min for visual
        max_graph=max(result_grid)
        min_graph=0
        
        #Plot the result grid
        plt.plot()
        for i in range(len(Components_DF)):
            comp_coords=Components_DF['ComponentCoordsLonLat'][i]
            poly2=sh.geometry.Polygon(comp_coords)
            if Components_DF['Emission_Source'][i]==True:
                TempPoly_Buff=poly2
                x1,y1=TempPoly_Buff.exterior.xy
                plt.plot(x1,y1,color='red',linewidth=.5)
            else:
                TempPoly_Buff=poly2
                x1,y1=TempPoly_Buff.exterior.xy
                plt.plot(x1,y1,color='gray',linewidth=.5)
        plt.scatter(GridDF.newlist_x,GridDF.newlist_y,s=8,c=GridDF.result_grid,cmap='turbo')
        plt.clim(min_graph,max_graph)
        plt.colorbar(label='Percent of Detection')
        plt.show()

# endregion

# region Step 8
#%% Step 8: Run desired scenarios
if __name__ == "__main__":
    #Get site perimeter to get general size of site
    xx1,yy1=bdry.exterior.coords.xy
    dist_temp_sum=[]
    for i in range(len(xx1)-1):
        dist_temp=geod.line_length([xx1[i],xx1[i+1]],[yy1[i],yy1[i+1]])
        dist_temp_sum.append(dist_temp)
    perim=sum(dist_temp_sum) 
    
    if len(wind_list)!=0:
        xcoord1=tuple(GridDF['newlist_x'].values)
        ycoord1=tuple(GridDF['newlist_y'].values)
        windTriID1=list(GridDF['sim_grid_ID'])
        windTriPct1=list(GridDF['sim_grid_Val'])
        ResultPct1=list(GridDF['result_grid'].values)
    
    #We want to ask if they want us to output the ideal number of sensors for maximum coverage.
    print('Would you like to know the recommended number of sensors for your site?: \n',
          '1. Yes \n',
          '2. No')
    response_val=input('Your selection:')

    #Set parameters
    print('Next, we would like to input the range of sensors you are considering on using.')
    mininput=int(input('Please input the minimum number of sensors:'))
    maxinput_val=int(input('Please input the maximum number of sensors:'))
    if response_val=='1':
        maxinput=20
        maxview=maxinput_val
    else:
        maxinput=maxinput_val
        maxview=maxinput_val
    
    Dev_Val=np.arange(mininput,maxinput+1,1)
    Even_Equal=[]
    for i in range(len(Dev_Val)):
        Even_Equal.append([])
    DevResults=pd.DataFrame({'DevCount': Dev_Val})    
    
    if Placement_Selection=='Fenceline':
        if len(wind_list)==0:
            scen_sel='1,2'
        else:
            print('To limit processing times, please select the scenarios that you would like to consider: \n',
                  '1. Even Direction \n',
                  '2. Even Distance Spacing \n',
                  '3. Downwind Weighted, with Even Distance Spacing \n',
                  '4. Downwind Weighted, with Wind Probability-Based Positioning \n',
                  '5. Only Wind Probability-Based Positioning')
            scen_sel=input('Enter all scenarios to apply:')
        if query(scen_sel,1)==True:
            DevResults['Even_Dir']=Even_Equal
            DevResults['Even_Dir_X']=Even_Equal
            DevResults['Even_Dir_Y']=Even_Equal
        if query(scen_sel,2)==True:
            DevResults['Even_Equal']=Even_Equal
            DevResults['Even_Equal_X']=Even_Equal
            DevResults['Even_Equal_Y']=Even_Equal
        if query(scen_sel,3)==True:
            DevResults['DW_Weight_Equal']=Even_Equal
            DevResults['DW_Weight_Equal_X']=Even_Equal
            DevResults['DW_Weight_Equal_Y']=Even_Equal
        if query(scen_sel,4)==True:
            DevResults['DW_Weight_Prob']=Even_Equal
            DevResults['DW_Weight_Prob_X']=Even_Equal
            DevResults['DW_Weight_Prob_Y']=Even_Equal
        if query(scen_sel,5)==True:
            DevResults['Prob_Only']=Even_Equal
            DevResults['Prob_Only_X']=Even_Equal
            DevResults['Prob_Only_Y']=Even_Equal
        if query(scen_sel,1)==True or query(scen_sel,2)==True:
            if len(wind_list)==0: #If there is no wind
                xx1,yy1=bdry.exterior.coords.xy #take the exterior boundary
                Start_X,Start_Y=FindNWPt(xx1,yy1,bdry) #start at the most northwest point automatically 
            else:
                print('Next, we will decide where we would like to position the initial/first point: \n',
                      '1. At the point of highest probability of detection. \n',
                      '2. At the northwest corner of the site.')
                Init_Sel=input('Select start point option:')
                if int(Init_Sel)==1: #Start pt is probability based
                    Start_X=xcoord1[0]
                    Start_Y=ycoord1[0]
                else: #Start pt is nw corner of the site
                    Start_X,Start_Y=FindNWPt(xcoord1,ycoord1,bdry)
    else: #Internal placement only does probability-based placement.
            DevResults['Prob_Only']=Even_Equal
            DevResults['Prob_Only_X']=Even_Equal
            DevResults['Prob_Only_Y']=Even_Equal
            scen_sel='0'
    #
    #RUN THE SELECTED PLACEMENT SCENARIOS
    #
    if Placement_Selection=='Fenceline': #Only run the following if you want fenceline placement.
        if query(scen_sel,1)==True:    
            #Find Even Spacing Based on Direction Coordinates
            for i in range(len(Dev_Val)): #For each num of devices, run a simulation.
                if len(wind_list)!=0:
                    xcoord=copy.deepcopy(xcoord1)
                    ycoord=copy.deepcopy(ycoord1)
                    windTriID=copy.deepcopy(windTriID1)
                    windTriPct=copy.deepcopy(windTriPct1)
                    ResultPct=copy.deepcopy(ResultPct1)
                Dev_No=DevResults.iloc[i]['DevCount']
                print('No of Sensors:',Dev_No)
                x1,y1=EvenSpaceDir(Dev_No,bdry,Start_X,Start_Y)
                #snap points to closest grid point
                x1_fnl=[]
                y1_fnl=[]
                if len(wind_list)!=0:
                    pct_fnl=[]
                    wind_TriID=[]
                    wind_Tripct=[]
                    Result_val2=[]
                    for j in range(len(x1)): #Extract DF data from each of closest point
                        CP_x,CP_y,CP_Result,CP_WindTriID,CP_WindTriPct=FindClosestPt(xcoord,ycoord,x1[j],y1[j],ResultPct,windTriID,windTriPct)
                        x1_fnl.append(CP_x)
                        y1_fnl.append(CP_y)
                        wind_TriID.append(CP_WindTriID)
                        wind_Tripct.append(CP_WindTriPct)
                        Result_val2.append(CP_Result)
                else:
                    for j in range(len(x1)): #Extract DF data from each of closest point
                        CP_x,CP_y=FindClosestPt(newlist_x,newlist_y,x1[j],y1[j],ResultPct=None,windTriID=None,windTriPct=None)
                        x1_fnl.append(CP_x)
                        y1_fnl.append(CP_y)
                x_val=[]
                y_val=[]
                pct_fnl=[]
                for idx in range(len(x1_fnl)):
                    print(idx)
                    x_val.append(x1_fnl[0])
                    y_val.append(y1_fnl[0])
                    if len(wind_list)!=0:
                        pct_fnl.append(Result_val2[0])
                        x1_fnl,y1_fnl,wind_TriID,wind_Tripct,Result_val2,_=PctRefresh(x1_fnl,y1_fnl,wind_TriID,wind_Tripct,Result_val2,x1_fnl[0],y1_fnl[0],FigShow='Off')
                        #print(Result_val2)
                
                if len(wind_list)!=0:
                    pct_fnl2=sum(pct_fnl)
                    if pct_fnl2>100:
                        pct_fnl2=100
                
                    DevResults['Even_Dir'][i]=pct_fnl2
                else:
                    DevResults['Even_Dir'][i]='nan'
                DevResults['Even_Dir_X'][i]=x1_fnl
                DevResults['Even_Dir_Y'][i]=y1_fnl
                
                plt.figure()
                plt.plot(*bdry.exterior.xy,'blue')
                plt.scatter(x1_fnl,y1_fnl,marker='o',color='green')
                plt.title('Even Directions Spacing')
                plt.axis('equal') #Set axis as equal
                plt.xticks([])
                plt.yticks([])
                plt.show()
            print('Finished Calculating Even Spacing by Direction')
   
        if query(scen_sel,2)==True:
            #Find Even Spacing Based on Distance Coordinates
            for i in range(len(Dev_Val)):
                if len(wind_list)!=0:
                    xcoord=copy.deepcopy(xcoord1)
                    ycoord=copy.deepcopy(ycoord1)
                    windTriID=copy.deepcopy(windTriID1)
                    windTriPct=copy.deepcopy(windTriPct1)
                    ResultPct=copy.deepcopy(ResultPct1)
                Dev_No=DevResults.iloc[i]['DevCount']
                print('No of Sensors:',Dev_No)
                x1,y1=EvenDistSpacing(Dev_No,bdry,Start_X,Start_Y)
                #snap points to closest grid point
                x1_fnl=[]
                y1_fnl=[]
                if len(wind_list)!=0:
                    pct_fnl=[]
                    wind_TriID=[]
                    wind_Tripct=[]
                    Result_val2=[]
                    for j in range(len(x1)): #Extract DF data from each of closest point
                        CP_x,CP_y,CP_Result,CP_WindTriID,CP_WindTriPct=FindClosestPt(xcoord,ycoord,x1[j],y1[j],ResultPct,windTriID,windTriPct)
                        x1_fnl.append(CP_x)
                        y1_fnl.append(CP_y)
                        wind_TriID.append(CP_WindTriID)
                        wind_Tripct.append(CP_WindTriPct)
                        Result_val2.append(CP_Result)
                else:
                    for j in range(len(x1)): #Extract DF data from each of closest point
                        CP_x,CP_y=FindClosestPt(newlist_x,newlist_y,x1[j],y1[j],ResultPct=None,windTriID=None,windTriPct=None)
                        x1_fnl.append(CP_x)
                        y1_fnl.append(CP_y)
                x_val=[]
                y_val=[]
                pct_fnl=[]
                for idx in range(len(x1_fnl)):
                    x_val.append(x1_fnl[0])
                    y_val.append(y1_fnl[0])
                    if len(wind_list)!=0:
                        pct_fnl.append(Result_val2[0])
                        x1_fnl,y1_fnl,wind_TriID,wind_Tripct,Result_val2,_=PctRefresh(x1_fnl,y1_fnl,wind_TriID,wind_Tripct,Result_val2,x1_fnl[0],y1_fnl[0],FigShow='Off')
                        #print(Result_val2)
                
                if len(wind_list)!=0:
                    pct_fnl2=sum(pct_fnl)
                    if pct_fnl2>100:
                        pct_fnl2=100
                
                    DevResults['Even_Equal'][i]=pct_fnl2
                else:
                    DevResults['Even_Equal'][i]='nan'
                DevResults['Even_Equal_X'][i]=x1_fnl
                DevResults['Even_Equal_Y'][i]=y1_fnl
            
            print('Finished Calculating Even Spacing by Distance')
        
        if query(scen_sel,3)==True or query(scen_sel,4)==True:
            #Downwind Weighting
            xcoord=copy.deepcopy(xcoord1)
            ycoord=copy.deepcopy(ycoord1)
            ResultPct=copy.deepcopy(ResultPct1)
            
            #Part 1: Find Downwind Area
            Search_Angle, DW_Lines, UW_Lines, DW_Length, UW_Length=DW_Weighted_Part1(wind_list,bdry,Components_DF,xcoord,ycoord,ResultPct)

        if query(scen_sel,3)==True:
            #Part 2A: DW Weighted, using even spacing
            for i in range(len(Dev_Val)):
                xcoord=copy.deepcopy(xcoord1)
                ycoord=copy.deepcopy(ycoord1)
                windTriID=copy.deepcopy(windTriID1)
                windTriPct=copy.deepcopy(windTriPct1)
                ResultPct=copy.deepcopy(ResultPct1)
                
                Dev_No=DevResults.iloc[i]['DevCount']
                print('No of Sensors:',Dev_No)
                x1,y1=DW_Weighted_Part2_EvenSpace(Dev_No,DW_Lines,UW_Lines,DW_Length,UW_Length,xcoord,ycoord,ResultPct,bdry)
                #snap points to closest grid point
                x1_fnl=[]
                y1_fnl=[]
                pct_fnl=[]
                wind_TriID=[]
                wind_Tripct=[]
                Result_val2=[]
                for j in range(len(x1)): #Extract DF data from each of closest point
                    CP_x,CP_y,CP_Result,CP_WindTriID,CP_WindTriPct=FindClosestPt(xcoord,ycoord,x1[j],y1[j],ResultPct,windTriID,windTriPct)
                    x1_fnl.append(CP_x)
                    y1_fnl.append(CP_y)
                    wind_TriID.append(CP_WindTriID)
                    wind_Tripct.append(CP_WindTriPct)
                    Result_val2.append(CP_Result)
                x_val=[]
                y_val=[]
                pct_fnl=[]
                for idx in range(len(x1_fnl)):
                    x_val.append(x1_fnl[0])
                    y_val.append(y1_fnl[0])
                    pct_fnl.append(Result_val2[0])
                    x1_fnl,y1_fnl,wind_TriID,wind_Tripct,Result_val2,_=PctRefresh(x1_fnl,y1_fnl,wind_TriID,wind_Tripct,Result_val2,x1_fnl[0],y1_fnl[0],FigShow=False)
                    #print(Result_val2)
                pct_fnl2=sum(pct_fnl)
                if pct_fnl2>100:
                    pct_fnl2=100
                
                DevResults['DW_Weight_Equal'][i]=pct_fnl2
                DevResults['DW_Weight_Equal_X'][i]=x1_fnl
                DevResults['DW_Weight_Equal_Y'][i]=y1_fnl
            
            print('Finished Calculating DW Weighting by Even Spacing')
        
        if query(scen_sel,4)==True:
            #Part 2B: DW Weighted, prioritizing probability of detection:
            for i in range(len(Dev_Val)):
                xcoord=copy.deepcopy(xcoord1)
                ycoord=copy.deepcopy(ycoord1)
                windTriID=copy.deepcopy(windTriID1)
                windTriPct=copy.deepcopy(windTriPct1)
                ResultPct=copy.deepcopy(ResultPct1)
                Dev_No=DevResults.iloc[i]['DevCount']
                print('Simulation of', Dev_No, 'Devices')
                x1,y1=DW_Weighted_Part2_Prob (Dev_No,xcoord,ycoord,windTriID,windTriPct,ResultPct,bdry,DW_Lines,UW_Lines,DW_Length,UW_Length)
                
                xcoord=copy.deepcopy(xcoord1)
                ycoord=copy.deepcopy(ycoord1)
                windTriID=copy.deepcopy(windTriID1)
                windTriPct=copy.deepcopy(windTriPct1)
                ResultPct=copy.deepcopy(ResultPct1)
        
                #snap points to closest grid point
                x1_fnl=[]
                y1_fnl=[]
                pct_fnl=[]
                wind_TriID=[]
                wind_Tripct=[]
                Result_val2=[]
                for j in range(len(x1)): #Extract DF data from each of closest point
                    CP_x,CP_y,CP_Result,CP_WindTriID,CP_WindTriPct=FindClosestPt(xcoord,ycoord,x1[j],y1[j],ResultPct,windTriID,windTriPct)
                    x1_fnl.append(CP_x)
                    y1_fnl.append(CP_y)
                    wind_TriID.append(CP_WindTriID)
                    wind_Tripct.append(CP_WindTriPct)
                    Result_val2.append(CP_Result)
                x_val=[]
                y_val=[]
                pct_fnl=[]
                for idx in range(len(x1_fnl)):
                    x_val.append(x1_fnl[0])
                    y_val.append(y1_fnl[0])
                    pct_fnl.append(Result_val2[0])
                    x1_fnl,y1_fnl,wind_TriID,wind_Tripct,Result_val2,_=PctRefresh(x1_fnl,y1_fnl,wind_TriID,wind_Tripct,Result_val2,x1_fnl[0],y1_fnl[0], FigShow='Off')
                    print(Result_val2)
                pct_fnl2=sum(pct_fnl)
                if pct_fnl2>100:
                    pct_fnl2=100
                
                DevResults['DW_Weight_Prob'][i]=pct_fnl2
                DevResults['DW_Weight_Prob_X'][i]=x1_fnl
                DevResults['DW_Weight_Prob_Y'][i]=y1_fnl
                print(pct_fnl2)
            
            print('Finished Calculating DW Weighting by Probability of Detection')
    
    if Placement_Selection=='Fenceline' and query(scen_sel,5)==True or Placement_Selection=='Internal':
        #Only by probability of detection
        Dev_No=max(DevResults['DevCount'])
        xcoord=copy.deepcopy(xcoord1)
        ycoord=copy.deepcopy(ycoord1)
        windTriID=copy.deepcopy(windTriID1)
        windTriPct=copy.deepcopy(windTriPct1)
        ResultPct=copy.deepcopy(ResultPct1)
        print('Simulation of', Dev_No, 'Devices')
        fnl_x,fnl_y,fnl_pct=ProbOnly(Dev_No, xcoord, ycoord, windTriID, windTriPct, ResultPct,Fig='On')
        
        for i in range(len(Dev_Val)):
            idx=Dev_Val[i]
            pts_x=fnl_x[0:idx]
            pts_y=fnl_y[0:idx]
            pts_pct=fnl_pct[0:idx]
            pct_fnl2=sum(pts_pct)
            if pct_fnl2>100:
                pct_fnl2=100
            
            DevResults['Prob_Only'][i]=pct_fnl2
            DevResults['Prob_Only_X'][i]=pts_x
            DevResults['Prob_Only_Y'][i]=pts_y
        print('Finished Calculating POD method')

# region Num SOOFIE
#%% Calculate recommended number of SOOFIEs
if __name__ == "__main__":
    from scipy.optimize import curve_fit
    No_Sims=int((len(DevResults.columns)-1)/3) #get number of simulations run (e.g. number of lines to plot)
    Flat_Pts=[]
    for i in range(No_Sims):
        col_to_use=1+(i*3)
        lab1=DevResults.columns[col_to_use]
        
        val1=DevResults["DevCount"].tolist()
        val2=DevResults[DevResults.columns[col_to_use]].tolist()
        dy = np.diff(val2)  # First difference (delta y)
        dx = np.diff(val1)  # First difference (delta x)

        # Ensure dx and dy have the same length (remove last element of x)
        val1 = val1[:-1]

        # Compute first derivative dy/dx
        dy_dx = dy / dx   # First derivative dy/dx

        # Smooth the derivative curve for better visualization
        smooth_window = 3  # Adjust window size for smoothing
        smoothed_dy_dx = np.convolve(dy_dx, np.ones(smooth_window)/smooth_window, mode='valid')

        # Find the point where the curve flattens out (change in slope)
        flattening_index = np.argmin(np.abs(smoothed_dy_dx))  # Index of minimum derivative

        flattening_point = val1[flattening_index + (smooth_window - 1) // 2]  # Adjust for smoothing effect
        Flat_Pts.append(flattening_point)

# region Plot Change
#%% Results: Plot change in detection by device
if __name__ == "__main__":
    No_Sims=int((len(DevResults.columns)-1)/3) #get number of simulations run (e.g. number of lines to plot)
    
    fig = plt.figure(figsize=(8, 5))
    for i in range(No_Sims):
        col_to_use=1+(i*3)
        lab1=DevResults.columns[col_to_use]
        if lab1=='Even_Equal':
            lab2='Even Distance Spacing Around Site Perimeter'
        elif lab1=='Even_Dir':
            lab2='Even Directional Spacing'
        elif lab1=='DW_Weight_Equal':
            lab2='Downwind Weighted, using Even Spacing'
        elif lab1=='DW_Weight_Prob':
            lab2='Downwind Weighted, using Probability'
        else:
            lab2='Probability Only'
            
        val1=DevResults["DevCount"]
        val2=DevResults[DevResults.columns[col_to_use]]
        
        if mininput <= 3:
            PlotX_val = pd.concat([pd.Series([0]), val1], ignore_index=True)
            PlotY_val= pd.concat([pd.Series([0]), val2], ignore_index=True)
            plt.plot(PlotX_val,PlotY_val,'o-',label=lab2)
        else:
            plt.plot(val1,val2,'o-',label=lab2)
    plt.ylabel('Percent of Detection\n (for quick detection)')
    plt.xlabel('Number of Sensors')
    plt.legend(title='Type of Simulation:')
    plt.ylim(0,85)
    plt.title('Probability of Detection vs. Number of SOOFIE Sensors')
    #Setting x-ticks as integers
    plt.xticks(range(maxview+1))
    plt.xlim(0,maxview+.5)
    #plt.xticks(range(len(PlotX_val)), map(int, PlotX_val))
    
    fig.savefig(new_path+'/POD_Figure.png') #Save the figure
    plt.show()
    plt.close()


# region Final Map
#%% Results: Final map of placement
if __name__ == "__main__":
    #Plot scenario
    if No_Sims>1:
        print('Select the scenario to use:')
        for i in range(No_Sims):
            col_to_use=1+(i*3)
            lab1=DevResults.columns[col_to_use]
            if lab1=='Even_Equal':
                lab2='Even Distance Spacing Around Site Perimeter'
            elif lab1=='Even_Dir':
                lab2='Even Directional Spacing'
            elif lab1=='DW_Weight_Equal':
                lab2='Downwind Weighted, using Even Spacing'
            elif lab1=='DW_Weight_Prob':
                lab2='Downwind Weighted, using Probability'
            else:
                lab2='Probability Only'
            print(str(i+1)+') '+lab2)
        scen=input('Your Selection:')
        col_to_use=int(scen)-1
    else:
        col_to_use=1
    
    if No_Sims>1:    
        col_to_use=((int(scen)-1)*3)+1
    else:
        col_to_use=1
    lab1=DevResults.columns[col_to_use]
    
    if lab1=='Even_Equal':
        lab2='Even Distance Spacing Around Site Perimeter'
    elif lab1=='Even_Dir':
        lab2='Even Directional Spacing'
    elif lab1=='DW_Weight_Equal':
        lab2='Downwind Weighted, using Even Spacing'
    elif lab1=='DW_Weight_Prob':
        lab2='Downwind Weighted, using Probability'
    else:
        lab2='Probability Only'
            
    #Take no. of sensors and config.
    print('Select the number of sensors to view:')
    for i in range(len(DevResults['DevCount'])):
        print(str(i+1)+') Scenario with '+str(int(DevResults.iloc[i]['DevCount']))+' sensor(s)')
    no_soofi=input('Your input:')
    #Start creating plot here
    no_instr=DevResults.iloc[int(no_soofi)-1]['DevCount']
    temp_df=DevResults.iloc[int(no_soofi)-1]
    x_val=temp_df[int(col_to_use+1)]
    y_val=temp_df[int(col_to_use+2)]
    fig, ax = plt.subplots(1, 1)
    plt.imshow(img_plt)
    plt.plot(*PlacementPoly_Px.exterior.xy,'darkblue')
    if hasattr(x_val, "__len__"): #If it is a list
        len_graph=len(x_val)
    else:
        len_graph=x_val.size
    for i in range(len(Components_DF)):
        outline=sh.geometry.Polygon(Components_DF['ComponentCoordsPx'][i])
        if Components_DF.iloc[i]['Emission_Source']==True:
            plt.plot(*outline.exterior.xy,'red',linewidth=0.5)
        else:
            plt.plot(*outline.exterior.xy,'darkslategrey',linewidth=0.5)
    for i in range(len_graph): #for each SOOFIE in the scenario
        if len_graph==1:
            x_val1=x_val.tolist()
            y_val1=y_val.tolist()
            if ImgType=='GeoTiff': #lon/lat to pixel
                pt_px=~transform * (x_val1,y_val1)
            else:
                pt_px=transformer.rowcol(x_val1,y_val1)
        else:
            if ImgType=='GeoTiff':
                pt_px=~transform * (x_val[i],y_val[i])
            else:
                pt_px=transformer.rowcol(x_val[i],y_val[i])
        plt.scatter(pt_px[0],pt_px[1],s=45,color='green')
    plt.xticks([])
    plt.yticks([])
    plt.title('SOOFIE Locations: '+str(len_graph)+' sensors, \''+lab2+'\' scenario')
    
    
    SaveFig=input('Do you want to save the figure? \n'
                  +'1) Yes \n'
                  +'2) No \n'
                  +'Your input:')
    if SaveFig=='1':
        FigName=input('Enter Figure Name:')
        plt.savefig(new_path+'/'+str(FigName)+'.png') #Save the figure
    plt.show

# region Export KML & JSON
#%% Export kml and json files
if __name__ == "__main__":
    exportpts=input('Do you want to save sensor placement locations (as kmz/json)? \n'
                    +'1) Yes \n'
                    +'2) No \n'
                    +'Your input:')
    if exportpts=='1':
        #Plot scenario
        if No_Sims>1:
            print('Select the scenario to use:')
            for i in range(No_Sims):
                col_to_use=1+(i*3)
                lab1=DevResults.columns[col_to_use]
                if lab1=='Even_Equal':
                    lab2='Even Distance Spacing Around Site Perimeter'
                elif lab1=='Even_Dir':
                    lab2='Even Directional Spacing'
                elif lab1=='DW_Weight_Equal':
                    lab2='Downwind Weighted, using Even Spacing'
                elif lab1=='DW_Weight_Prob':
                    lab2='Downwind Weighted, using Probability'
                else:
                    lab2='Probability Only'
                print(str(i+1)+') '+lab2)
            scen=input('Your Selection:')
            col_to_use=int(scen)-1
        else:
            col_to_use=1
        
        if No_Sims>1:    
            col_to_use=((int(scen)-1)*3)+1
        else:
            col_to_use=1
        lab1=DevResults.columns[col_to_use]
        
        if lab1=='Even_Equal':
            lab2='Even Distance Spacing Around Site Perimeter'
        elif lab1=='Even_Dir':
            lab2='Even Directional Spacing'
        elif lab1=='DW_Weight_Equal':
            lab2='Downwind Weighted, using Even Spacing'
        elif lab1=='DW_Weight_Prob':
            lab2='Downwind Weighted, using Probability'
        else:
            lab2='Probability Only'
                
        #Take no. of sensors and config.
        print('Select the number of sensors to use:')
        for i in range(len(DevResults['DevCount'])):
            print(str(i+1)+') Scenario with '+str(int(DevResults.iloc[i]['DevCount']))+' sensor(s)')
        no_soofi=input('Your input:')
        #Start creating plot here
        no_instr=DevResults.iloc[int(no_soofi)-1]['DevCount']
        temp_df=DevResults.iloc[int(no_soofi)-1]
        x_val=list(temp_df[int(col_to_use+1)]) #array of x values
        y_val=list(temp_df[int(col_to_use+2)]) #array of y values
        
        #support instruments in a clockwise order.
        az=[]
        #if x_val.ndim == 0:
        if not isinstance(x_val,list):
            x_val2=x_val.item()
            y_val2=y_val.item()
            _,az12,_=geod.inv(x_val2,y_val2,bdry.centroid.x,bdry.centroid.y)
            if az12<0:
                az12=az12+360
            az.append(az12)
            sorted_points = [(x_val2,y_val2,az)]
        else:
            for k in range(len(x_val)):
                _,az12,_=geod.inv(x_val[k],y_val[k],bdry.centroid.x,bdry.centroid.y)
                if az12<0:
                    az12=az12+360
                az.append(az12)
            sorted_points = sorted(zip(x_val, y_val, az), key=lambda point: point[2])
        
        # Extract the sorted coordinates
        sorted_x_val = [point[0] for point in sorted_points]
        sorted_y_val = [point[1] for point in sorted_points]
            
        #Create a list of devices (a dictionary in each column):
        Device_info=[]
        #if x_val.ndim==0:
        if not isinstance(x_val,list):
            dev_no=1
        else:
            dev_no=len(x_val)
        for j in range(dev_no): #For each instrument,
            device_name='SOOFIE-'+str(j+1)
            Device_info2={'DeviceName': device_name, 'Latitude': float(sorted_y_val[j]), 'Longitude': float(sorted_x_val[j])}
            Device_info.append(Device_info2)
        len_graph=dev_no
        
        #CREATE JSON
        # Define the data
        data = {
            "Operator": Operator_Name,
            "Site": Project_Name,
            "Devices": Device_info
        }
        
        # Define the file path
        modified_scenario = lab2.replace(" ", "_") #take out all spaces in file name
        modified_scenario = modified_scenario.replace(",", "") #take out all commas in file name
        json_path = Project_Name+'_'+modified_scenario+'_'+str(int(len_graph))+'sensors'+'.json'
        
        # Write the data to a JSON file
        with open(json_path, 'w') as json_file:
            json.dump(data, json_file, indent=4)  # Use indent for pretty printing
        
        #CREATE KML
        kml = simplekml.Kml()
        
        # Define point style
        point_style = simplekml.Style()
        point_style.iconstyle.icon.href = 'http://maps.google.com/mapfiles/kml/shapes/placemark_circle.png'

        # Add placemarks for each device location
        for location in Device_info:
            name = location["DeviceName"]
            latitude = location["Latitude"]
            longitude = location["Longitude"]
            pnt = kml.newpoint(name=name, coords=[(longitude, latitude)])
            pnt.style = point_style
        
        # Save the KML to a KMZ file
        kmz_file = Project_Name+'_'+modified_scenario+'_'+str(int(len_graph))+'sensors'+'.kmz'
        kml.savekmz(kmz_file)

#%% Export simulation results and coordinates:
#dataset.close()
if __name__ == "__main__":
    export_file_name=str(new_path+'/SimulationResults.xlsx')
    DevResults.to_excel(export_file_name)

