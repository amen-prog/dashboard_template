// src/App.tsx
import React, { useState, useEffect, useRef, useCallback } from 'react';
import axios from 'axios';
import mapboxgl from 'mapbox-gl';
import MapboxDraw from '@mapbox/mapbox-gl-draw';
import '@mapbox/mapbox-gl-draw/dist/mapbox-gl-draw.css';
import * as turf from '@turf/turf';
import '../../mapbox-custom.css';
import { Button } from "@/components/ui/button"
import ControlsDropdown from "./ControlsDropdown";
import { Input } from "@/components/ui/input"
import {
    DropdownMenu,
    DropdownMenuContent,
    DropdownMenuItem,
    DropdownMenuTrigger,
    DropdownMenuLabel,
} from "@/components/ui/dropdown-menu"
import { ChevronDown, Pencil, Trash2, Check} from 'lucide-react';

mapboxgl.accessToken = 'pk.eyJ1IjoibWFobW91ZGFsaTEiLCJhIjoiY2x0cW1rc3dhMDd4dTJpbW8wemp0ZHRyMyJ9.OFxJ3NcR8gGBVzlgVZ_ADw';

interface EquipmentType {
    id: string;
    name: string;
    sourceHeight: number;
    isEmissionSource: boolean;
  }

//#region Equipment 
const equipmentTypes: EquipmentType[] = [
  { id: '1', name: 'High Pressure Flare', sourceHeight: 10, isEmissionSource: true },
  { id: '2', name: 'Low Pressure Flare', sourceHeight: 5, isEmissionSource: true },
  { id: '3', name: 'Heater Treater', sourceHeight: 3, isEmissionSource: true },
  { id: '4', name: 'Tank', sourceHeight: 5, isEmissionSource: true },
  { id: '5', name: 'Well', sourceHeight: 3, isEmissionSource: true },
  { id: '6', name: 'Compressor', sourceHeight: 3, isEmissionSource: true },
  { id: '7', name: 'Scrubber', sourceHeight: 3, isEmissionSource: true },
  { id: '8', name: 'Separator', sourceHeight: 3, isEmissionSource: true },
  { id: '9', name: 'Tester', sourceHeight: 3, isEmissionSource: true },
  { id: '10', name: 'Landfill', sourceHeight: 0, isEmissionSource: true },
  { id: '11', name: 'Exclusion Zone (road/no structure)', sourceHeight: NaN, isEmissionSource: false },
  { id: '12', name: 'Exclusion Zone (structure)', sourceHeight: NaN, isEmissionSource: false },
  { id: '13', name: 'Offsite Source', sourceHeight: 3, isEmissionSource: true },
  { id: '14', name: 'Other', sourceHeight: 3, isEmissionSource: true },
];

//#endregion 


//#region MapProps
interface MapProps {   
    drawingEnabled: boolean;
    searchEnabled: boolean;
    equipmentDrawingEnabled: boolean;
    sensorEnabled: boolean;
    onBoundaryChange?: (boundary: GeoJSON.Feature | null) => void;
    onEquipmentConfirm?: (equipment: Array<{ equipment: EquipmentType, polygon: GeoJSON.Feature }>) => void;
    initialBoundary?: GeoJSON.Feature | null;
  }

  const mapStyles = [
    { name: 'Satellite', url: 'mapbox://styles/mapbox/satellite-v9' },
    { name: 'Streets', url: 'mapbox://styles/mapbox/streets-v11' },
    { name: 'Light', url: 'mapbox://styles/mapbox/light-v10' },
    { name: 'Dark', url: 'mapbox://styles/mapbox/dark-v10' },
  ];


//#region Begin Component -----------------------------------------------------------------------------
const Map: React.FC<MapProps> = ({
    drawingEnabled, 
    searchEnabled, 
    equipmentDrawingEnabled,
    sensorEnabled,
    onBoundaryChange,
    onEquipmentConfirm,
    initialBoundary,
}) => {

  //#region Const States
  const [mapStyle, setMapStyle] = useState(mapStyles[0].url);
    const mapContainerRef = useRef<HTMLDivElement | null>(null);
    const mapRef = useRef<mapboxgl.Map | null>(null);
    const drawRef = useRef<MapboxDraw | null>(null);
    const barrierDrawRef = useRef<MapboxDraw | null>(null);
    const equipmentDrawRef = useRef<MapboxDraw | null>(null);
    const [state, setState] = useState(false);
    const [lat, setLat] = useState('');
    const [lng, setLng] = useState('');
    const [searchPerformed, setSearchPerformed] = useState(false);
    const [polygonArea, setPolygonArea] = useState<number | null>(null);
    const [selectedEquipment, setSelectedEquipment] = useState<EquipmentType | null>(null);
    const [drawnEquipment, setDrawnEquipment] = useState<Array<{ equipment: EquipmentType, polygon: GeoJSON.Feature }>>([]);
    const [currentBoundary, setCurrentBoundary] = useState<GeoJSON.Feature | null>(null);
    const [isBoundaryConfirmed, setIsBoundaryConfirmed] = useState(false);
    const [isEquipmentConfirmed, setIsEquipmentConfirmed] = useState(false);
    const [points, setPoints] = useState<GeoJSON.Feature[]>([]);
    const [pointPlacementMode, setPointPlacementMode] = useState(false);

    //#region Functions
    const satView = () => {
        setState(!state);
        if (mapRef.current) {
            const newStyle = state ? 'mapbox://styles/mapbox/streets-v11' : 'mapbox://styles/mapbox/satellite-v9';
            mapRef.current.setStyle(newStyle);
        }
    };

    const [viewState, setViewState] = useState({
      longitude: -102.099118,
      latitude: 31.97298,
      zoom: 9,
      bearing: 0,
      pitch: 0
    });

    // change the map style
   const changeMapStyle = (styleUrl: string) => {
    setMapStyle(styleUrl);
    if (mapRef.current) {
      mapRef.current.setStyle(styleUrl);
    }
  };

  // Search location using lat & lng
    const searchLocation = () => {
    if (mapRef.current) {
      const latitude = parseFloat(lat);
      const longitude = parseFloat(lng);
      if (!isNaN(latitude) && !isNaN(longitude)) {
        mapRef.current.flyTo({
          center: [longitude, latitude],
          essential: true,
          zoom: 17,
        });
      }
    }
  };
  //#endregion


  // Update area for Equipment Display
  const updateArea = useCallback(() => {
    if (drawRef.current) {
      const data = drawRef.current.getAll();
      const polygon = data.features[0];

      if (polygon) {
        const area = turf.area(polygon);
        setPolygonArea(area);
        setCurrentBoundary(polygon);
    
        if (equipmentDrawingEnabled && selectedEquipment) {
          setDrawnEquipment((prev) => [
            ...prev,
            { equipment: selectedEquipment, polygon },
          ]);
        }
      } else {
        setPolygonArea(null);
        setCurrentBoundary(null);
      }
    }
  }, [equipmentDrawingEnabled, selectedEquipment]);


  // Place Points for sensors on map
  const handlePointPlacement = useCallback((e: mapboxgl.MapMouseEvent & mapboxgl.EventData) => {
    if (pointPlacementMode && mapRef.current) {
      const coordinates = e.lngLat;
      
      const newPoint: GeoJSON.Feature = {
        type: 'Feature',
        geometry: {
          type: 'Point',
          coordinates: [coordinates.lng, coordinates.lat]
        },
        properties: {}
      };
  
      setPoints(prevPoints => [...prevPoints, newPoint]);
  
      // Add the new point to the map
      if (mapRef.current.getSource('placed-points')) {
        (mapRef.current.getSource('placed-points') as mapboxgl.GeoJSONSource).setData({
          type: 'FeatureCollection',
          features: [...points, newPoint]
        });
      }
    }
  }, [pointPlacementMode, points]);

  // confirm the drawn boundary
  const confirmBoundary = () => {
    if (currentBoundary) {
      setIsBoundaryConfirmed(true);
      if (onBoundaryChange) {
        onBoundaryChange(currentBoundary);
      }
    }
  };

  // confirm the drawn equipment
  const confirmEquipment = () => {
    setIsEquipmentConfirmed(true);
    if (onEquipmentConfirm) {
      onEquipmentConfirm(drawnEquipment);
    }
  };

//#region useEffect
  useEffect(() => {
    if (mapRef.current && drawRef.current) {
      mapRef.current.on('draw.create', updateArea);
      mapRef.current.on('draw.delete', updateArea);
      mapRef.current.on('draw.update', updateArea);
    }
  
    return () => {
      if (mapRef.current) {
        mapRef.current.off('draw.create', updateArea);
        mapRef.current.off('draw.delete', updateArea);
        mapRef.current.off('draw.update', updateArea);
      }
    };
  }, [mapRef, drawRef, updateArea]);

    useEffect(() => {
        if (mapContainerRef.current) {
            const map = new mapboxgl.Map({
                container: mapContainerRef.current,
                style: state ? 'mapbox://styles/mapbox/streets-v11' : 'mapbox://styles/mapbox/satellite-v9',
                center: [-102.6, 32],
                zoom: 9,
                attributionControl: false
            });

            map.addControl(new mapboxgl.AttributionControl({
                compact: true
            }), 'bottom-right');

            //#region Draw
            const drawStyles = [
              // Styles for barriers (blue)
              {
                'id': 'gl-draw-polygon-fill-inactive',
                'type': 'fill',
                'filter': ['all', ['==', '$type', 'Polygon']],
                'paint': {
                  'fill-color': '#3bb2d0',
                  'fill-outline-color': '#3bb2d0',
                  'fill-opacity': 0.1
                }
              },
              {
                'id': 'gl-draw-polygon-stroke-inactive',
                'type': 'line',
                'filter': ['all', ['==', '$type', 'Polygon']],
                'paint': {
                  'line-color': '#3bb2d0',
                  'line-width': 2
                }
              },
              // Styles for equipment (red)
              {
                'id': 'gl-draw-polygon-fill-active',
                'type': 'fill',
                'filter': ['all', ['==', '$type', 'Polygon']],
                'paint': {
                  'fill-color': '#ff0000',
                  'fill-outline-color': '#ff0000',
                  'fill-opacity': 0.1
                }
              },
              {
                'id': 'gl-draw-polygon-stroke-active',
                'type': 'line',
                'filter': ['all', ['==', '$type', 'Polygon']],
                'paint': {
                  'line-color': '#ff0000',
                  'line-width': 2
                }
              },
              // Additional styles for active drawing state
              {
                'id': 'gl-draw-polygon-and-line-vertex-active',
                'type': 'circle',
                'filter': ['all', ['==', 'meta', 'vertex'], ['==', '$type', 'Point'], ['!=', 'mode', 'static']],
                'paint': {
                  'circle-radius': 5,
                  'circle-color': '#fff'
                }
              },
              {
                'id': 'gl-draw-polygon-and-line-midpoint-active',
                'type': 'circle',
                'filter': ['all', ['==', 'meta', 'midpoint'], ['==', '$type', 'Point'], ['!=', 'mode', 'static']],
                'paint': {
                  'circle-radius': 3,
                  'circle-color': '#fbb03b'
                }
              }
            ];

            //#region Map on Event
            map.on('load', () => {

                    const draw = new MapboxDraw({
                        displayControlsDefault: false,
                        controls: {
                            polygon: false,
                            trash: false
                        },
                        userProperties: true,
                        styles: drawStyles
                    });

                    map.addControl(draw as unknown as mapboxgl.IControl);
                    drawRef.current = draw;
                //#endregion


                map.addSource('placed-points', {
                  type: 'geojson',
                  data: {
                    type: 'FeatureCollection',
                    features: []
                  }
                });
              
                map.addLayer({
                  id: 'placed-points',
                  type: 'circle',
                  source: 'placed-points',
                  paint: {
                    'circle-radius': 8,
                    'circle-color': '#00ff00'
                  }
                });
                
                // Add a source for the markers
        map.addSource('markers', {
          type: 'geojson',
          data: {
            type: 'FeatureCollection',
            features: [
              { type: 'Feature', geometry: { type: 'Point', coordinates: [-102.099118, 31.97298] }, properties: { id: 1 } },
              { type: 'Feature', geometry: { type: 'Point', coordinates: [-102.099118, 31.5] }, properties: { id: 2 } },
            ]
          },
          cluster: true,
          clusterMaxZoom: 14,
          clusterRadius: 50
        });

        // Add a layer for the clusters
        map.addLayer({
          id: 'clusters',
          type: 'circle',
          source: 'markers',
          filter: ['has', 'point_count'],
          paint: {
            'circle-color': [
              'step',
              ['get', 'point_count'],
              '#51bbd6',
              100,
              '#f1f075',
              750,
              '#f28cb1'
            ],
            'circle-radius': [
              'step',
              ['get', 'point_count'],
              20,
              100,
              30,
              750,
              40
            ]
          }
        });

        // Add a layer for the cluster count
        map.addLayer({
          id: 'cluster-count',
          type: 'symbol',
          source: 'markers',
          filter: ['has', 'point_count'],
          layout: {
            'text-field': '{point_count_abbreviated}',
            'text-font': ['DIN Offc Pro Medium', 'Arial Unicode MS Bold'],
            'text-size': 12
          }
        });

        // Add a layer for unclustered points
        map.addLayer({
          id: 'unclustered-point',
          type: 'circle',
          source: 'markers',
          filter: ['!', ['has', 'point_count']],
          paint: {
            'circle-color': '#11b4da',
            'circle-radius': 6,
            'circle-stroke-width': 1,
            'circle-stroke-color': '#fff'
          }
        });

        // Inspect a cluster on click
        map.on('click', 'clusters', (e) => {
          const features = map.queryRenderedFeatures(e.point, { layers: ['clusters'] });
          const clusterId = features[0].properties?.cluster_id;
          (map.getSource('markers') as mapboxgl.GeoJSONSource).getClusterExpansionZoom(
            clusterId,
            (err, zoom) => {
              if (err) return;

              map.easeTo({
                center: (features[0].geometry as GeoJSON.Point).coordinates as [number, number],
                zoom: zoom
              });
            }
          );
        });

        // When a click event occurs on a feature in the unclustered-point layer, zoom in
        map.on('click', 'unclustered-point', (e) => {
          const coordinates = (e.features?.[0].geometry as GeoJSON.Point).coordinates as [number, number];
          map.flyTo({
            center: coordinates,
            zoom: 14,
            duration: 2000
          });
        });

        // Change the cursor to a pointer when hovering over a cluster or point
        map.on('mouseenter', 'clusters', () => {
          map.getCanvas().style.cursor = 'pointer';
        });
        map.on('mouseleave', 'clusters', () => {
          map.getCanvas().style.cursor = '';
        });

        map.on('mouseenter', 'unclustered-point', () => {
          map.getCanvas().style.cursor = 'pointer';
        });
        map.on('mouseleave', 'unclustered-point', () => {
          map.getCanvas().style.cursor = '';
        });
      });

            mapRef.current = map;

            return () => {
                map.remove();
            }
        }
    }, [state]);

    useEffect(() => {
      if (mapRef.current) {
        mapRef.current.on('click', handlePointPlacement);
      }
    
      return () => {
        if (mapRef.current) {
          mapRef.current.off('click', handlePointPlacement);
        }
      };
    }, [handlePointPlacement, mapRef]);


    //#region Polygon Func
    const handleEquipmentSelect = (event: React.ChangeEvent<HTMLSelectElement>) => {
      const selected = equipmentTypes.find(eq => eq.id === event.target.value);
      setSelectedEquipment(selected || null);
      if (drawRef.current && selected) {
        drawRef.current.changeMode('draw_polygon', { userCustom: true });
      }
    };

    const handleDrawPolygon = () => {
      if (drawRef.current) {
        drawRef.current.changeMode('draw_polygon', { userCustom: false });
      }
    };
  
      const handleDeletePolygon = () => {
        if (drawRef.current) {
          drawRef.current.trash();
        }
      };

      //#region HTML 
      return (
        <div className="w-full h-full relative">
          <div className="absolute top-0 bottom-0 w-full h-full left-0" ref={mapContainerRef}>
            <div className="absolute top-4 left-4 z-10 flex flex-col gap-2">
            <ControlsDropdown
          mapStyles={mapStyles}
          changeMapStyle={changeMapStyle}
          searchEnabled={searchEnabled}
          drawingEnabled={drawingEnabled}
          equipmentDrawingEnabled={equipmentDrawingEnabled}
          lat={lat}
          lng={lng}
          setLat={setLat}
          setLng={setLng}
          searchLocation={searchLocation}
          drawPolygon={handleDrawPolygon}
          deletePolygon={handleDeletePolygon}
          equipmentTypes={equipmentTypes}
          setSelectedEquipment={setSelectedEquipment}
          confirmBoundary={confirmBoundary}
          confirmEquipment={confirmEquipment}
          isBoundaryConfirmed={isBoundaryConfirmed}
          isEquipmentConfirmed={isEquipmentConfirmed}
          currentBoundary={!!currentBoundary}
          drawnEquipmentLength={drawnEquipment.length}
        />
              {/* Barrier */}
              {(drawingEnabled || equipmentDrawingEnabled) && (
                <DropdownMenu>
                  <DropdownMenuTrigger asChild>
                    <Button variant="secondary" className="w-40">
                      Barrier <ChevronDown className="ml-2 h-4 w-4" />
                    </Button>
                  </DropdownMenuTrigger>
                  <DropdownMenuContent>
                    <DropdownMenuItem onClick={handleDrawPolygon}>
                      <Pencil className="mr-2 h-4 w-4" />
                      Draw Polygon
                    </DropdownMenuItem>
                    <DropdownMenuItem onClick={handleDeletePolygon}>
                      <Trash2 className="mr-2 h-4 w-4" />
                      Delete Polygon
                    </DropdownMenuItem>
                  </DropdownMenuContent>
                </DropdownMenu>
              )}

{/* Draw Equipment */}
{equipmentDrawingEnabled && (
    <DropdownMenu>
        <DropdownMenuTrigger asChild>
            <Button variant="secondary" className="w-40">
                Select Equipment <ChevronDown className="ml-2 h-4 w-4" />
            </Button>
        </DropdownMenuTrigger>
        <DropdownMenuContent>
            {equipmentTypes.map(eq => (
                <DropdownMenuItem key={eq.id} onSelect={() => handleEquipmentSelect({ target: { value: eq.id } } as React.ChangeEvent<HTMLSelectElement>)}>
                    {eq.name}
                </DropdownMenuItem>
            ))}
        </DropdownMenuContent>
    </DropdownMenu>
)}
              
              {selectedEquipment && (
                <div className="bg-white p-2 rounded shadow">
                  <p className="text-sm font-medium">Selected: {selectedEquipment.name}</p>
                </div>
              )}

              {/* Sensor Placement */}
              {sensorEnabled && (

                    <>
                    <Button 
                      variant="secondary" 
                      className="w-40"
                      onClick={() => setPointPlacementMode(!pointPlacementMode)}
                    >
                      {pointPlacementMode ? 'Finish Adding Sensors' : 'Add Sensor'}
                    </Button> 
                    {points.length > 0 && (
                      <div className="bg-white p-2 rounded shadow mt-2">
                        <p className="text-sm font-medium">Sensors added: {points.length}</p>
                      </div>
                    )}
                    </>
              )}
            </div>
            
            {/* Display Equipment  */}
            {drawnEquipment.length > 0 && (
              <div className="absolute bottom-4 right-4 m-2 p-4 bg-white rounded shadow overflow-auto max-h-[50%] max-w-[300px]">
                <h3 className="font-bold mb-2">Drawn Equipment:</h3>
                <ul className="space-y-4">
                  {drawnEquipment.map((item, index) => (
                    <li key={index} className="text-sm">
                      <strong>{item.equipment.name}</strong>
                      <ul className="ml-4">
                        <li>ID: {item.equipment.id}</li>
                        <li>Source Height: {
                          isNaN(item.equipment.sourceHeight)
                            ? 'N/A'
                            : `${item.equipment.sourceHeight} m`
                        }</li>
                        <li>Emission Source: {item.equipment.isEmissionSource ? 'Yes' : 'No'}</li>
                      </ul>
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        </div>
    );
};

export default Map;
