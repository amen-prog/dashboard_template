#%%Load all needed subroutines and packages

import os
import json
import shutil
from osgeo import gdal, osr
import rasterio as rio
from rasterio.plot import show
import numpy as np
import tkinter as tk
from tkinter import filedialog
#Change from PNG to TIFF
from PIL import Image
import cv2 as cv
import matplotlib.pyplot as plt
import shapely as sh
from rasterio.control import GroundControlPoint
import zipfile
from fastkml import kml
from shapely.geometry import Polygon, Point, LineString, MultiPolygon, MultiLineString, GeometryCollection
from pyproj import Geod
import pandas as pd
from osgeo import ogr
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timezone
from influxdb import InfluxDBClient
import seaborn
seaborn.set_style('ticks') 
import warnings
warnings.filterwarnings("ignore") 
from shapely.ops import nearest_points, split, unary_union, linemerge
import multiprocessing
import copy
from itertools import count
import math
import zipfile
import xml.etree.ElementTree as ET
import re
import json
import simplekml
from functools import reduce
from scipy.signal import find_peaks
from statistics import mean

geod = Geod(ellps='WGS84')