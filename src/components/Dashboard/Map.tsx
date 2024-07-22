// src/App.tsx
import React, { useState, useEffect, useRef, useCallback } from 'react';
import mapboxgl from 'mapbox-gl';
import MapboxDraw from '@mapbox/mapbox-gl-draw';
import '@mapbox/mapbox-gl-draw/dist/mapbox-gl-draw.css';
import * as turf from '@turf/turf';
import '../../mapbox-custom.css';
import { Button } from "@/components/ui/button"
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

interface MapProps {   
    drawingEnabled: boolean;
    searchEnabled: boolean;
    equipmentDrawingEnabled: boolean;
    onBoundaryChange?: (boundary: GeoJSON.Feature | null) => void;
    onEquipmentConfirm?: (equipment: Array<{ equipment: EquipmentType, polygon: GeoJSON.Feature }>) => void;
    initialBoundary?: GeoJSON.Feature | null;
  }

const Map: React.FC<MapProps> = ({
    drawingEnabled, 
    searchEnabled, 
    equipmentDrawingEnabled,
    onBoundaryChange,
    onEquipmentConfirm,
    initialBoundary
}) => {

    const mapInstanceRef = useRef<mapboxgl.Map | null>(null);
    const mapContainerRef = useRef<HTMLDivElement | null>(null);
    const mapRef = useRef<mapboxgl.Map | null>(null);
    const drawRef = useRef<MapboxDraw | null>(null);
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

    const satView = () => {
        setState(!state);
        if (mapRef.current) {
            const newStyle = state ? 'mapbox://styles/mapbox/streets-v11' : 'mapbox://styles/mapbox/satellite-v9';
            mapRef.current.setStyle(newStyle);
        }
    };

    const searchLocation = () => {
        if (mapRef.current) {
            const latitude = parseFloat(lat);
            const longitude = parseFloat(lng);
            if (!isNaN(latitude) && !isNaN(longitude)) {
                mapRef.current.flyTo({
                    center: [longitude, latitude],
                    essential: true,
                    zoom: 17
                });
                setSearchPerformed(true);
            }
        }
    };


    const updateArea = useCallback(() => {
        if (drawRef.current) {
            const data = drawRef.current.getAll();
            const polygon = data.features[0];
  
            if (polygon) {
                const area = turf.area(polygon);
                setPolygonArea(area);
                setCurrentBoundary(polygon);
  
                if (equipmentDrawingEnabled && selectedEquipment) {
                    setDrawnEquipment(prev => [...prev, { equipment: selectedEquipment, polygon }]);
                    drawRef.current.deleteAll();
                }
            } else {
                setPolygonArea(null);
                setCurrentBoundary(null);
            }
        }
      }, [equipmentDrawingEnabled, selectedEquipment]);

      const confirmBoundary = () => {
        if (currentBoundary) {
            setIsBoundaryConfirmed(true);
            if (onBoundaryChange) {
                onBoundaryChange(currentBoundary);
            }
        }
    };

    const confirmEquipment = () => {
        setIsEquipmentConfirmed(true);
        if (onEquipmentConfirm) {
            onEquipmentConfirm(drawnEquipment);
        }
    };



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

            map.on('load', () => {
                if (drawingEnabled || equipmentDrawingEnabled) {
                    const draw = new MapboxDraw({
                        displayControlsDefault: false,
                        controls: {
                            polygon: false,
                            trash: false
                        }
                    });

                    map.addControl(draw);
                    drawRef.current = draw;

                    if (initialBoundary) {
                        draw.add(initialBoundary);
                        updateArea();
                    }

                    map.on('draw.create', updateArea);
                    map.on('draw.update', updateArea);
                    map.on('draw.delete', updateArea);
                }

                // Add a source for the points
                map.addSource('points', {
                    type: 'geojson',
                    data: {
                        type: 'FeatureCollection',
                        features: [
                            {
                                type: 'Feature',
                                geometry: {
                                    type: 'Point',
                                    coordinates: [-102.099118, 31.972980]
                                },
                                properties: {}
                            },
                            {
                              type: 'Feature',
                              geometry: {
                                  type: 'Point',
                                  coordinates: [-102.099118, 31.5]
                              },
                              properties: {}
                          },
                            // Add more points here
                        ]
                    },
                    cluster: true,
                    clusterMaxZoom: 14, // Max zoom to cluster points on
                    clusterRadius: 50 // Radius of each cluster when clustering points (defaults to 50)
                });

                // Add a layer for the clusters
                map.addLayer({
                    id: 'clusters',
                    type: 'circle',
                    source: 'points',
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
                    source: 'points',
                    filter: ['has', 'point_count'],
                    layout: {
                        'text-field': '{point_count_abbreviated}',
                        'text-font': ['DIN Offc Pro Medium', 'Arial Unicode MS Bold'],
                        'text-size': 12
                    }
                });

                // Add a layer for the unclustered points
                map.addLayer({
                    id: 'unclustered-point',
                    type: 'circle',
                    source: 'points',
                    filter: ['!', ['has', 'point_count']],
                    paint: {
                        'circle-color': '#11b4da',
                        'circle-radius': 6,
                        'circle-stroke-width': 1,
                        'circle-stroke-color': '#fff'
                    }
                });
            });

            mapRef.current = map;

            return () => {
                map.remove();
            }
        }
    }, [state, drawingEnabled, equipmentDrawingEnabled, initialBoundary, updateArea]);


    const handleEquipmentSelect = (event: React.ChangeEvent<HTMLSelectElement>) => {
      const selected = equipmentTypes.find(eq => eq.id === event.target.value);
      setSelectedEquipment(selected || null);
    };

    const handleDrawPolygon = () => {
        if (drawRef.current) {
          drawRef.current.changeMode('draw_polygon');
        }
      };
  
      const handleDeletePolygon = () => {
        if (drawRef.current) {
          drawRef.current.trash();
        }
      };

      return (
        <div className="w-full h-full relative">
          <div className="absolute top-0 bottom-0 w-full h-full left-0" ref={mapContainerRef}>
            <div className="absolute top-4 left-4 z-10 flex flex-col gap-2">
              <DropdownMenu>
                <DropdownMenuTrigger asChild>
                  <Button variant="secondary" className="w-40">
                    Actions <ChevronDown className="ml-2 h-4 w-4" />
                  </Button>
                </DropdownMenuTrigger>
                <DropdownMenuContent>
                  <DropdownMenuItem onClick={satView}>
                    Change view
                  </DropdownMenuItem>
                  {searchEnabled && (
                    <DropdownMenuItem onClick={searchLocation}>
                      Search Location
                    </DropdownMenuItem>
                  )}
                </DropdownMenuContent>
              </DropdownMenu>

              {(drawingEnabled || equipmentDrawingEnabled) && (
                <DropdownMenu>
                  <DropdownMenuTrigger asChild>
                    <Button variant="secondary" className="w-40">
                      Drawing Tools <ChevronDown className="ml-2 h-4 w-4" />
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

              {equipmentDrawingEnabled && (
                <DropdownMenu>
                  <DropdownMenuTrigger asChild>
                    <Button variant="secondary" className="w-40">
                      Select Equipment <ChevronDown className="ml-2 h-4 w-4" />
                    </Button>
                  </DropdownMenuTrigger>
                  <DropdownMenuContent>
                    {equipmentTypes.map(eq => (
                      <DropdownMenuItem key={eq.id} onSelect={() => setSelectedEquipment(eq)}>
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

              {drawingEnabled && !isBoundaryConfirmed && currentBoundary && (
                <Button onClick={confirmBoundary} className="w-40">
                  <Check className="mr-2 h-4 w-4" /> Confirm Boundary
                </Button>
              )}

              {equipmentDrawingEnabled && drawnEquipment.length > 0 && !isEquipmentConfirmed && (
                <Button onClick={confirmEquipment} className="w-40">
                  <Check className="mr-2 h-4 w-4" /> Confirm Equipment
                </Button>
              )}
            </div>
    
            {polygonArea !== null && (
              <div className="absolute bottom-4 left-4 m-2 p-2 bg-white rounded shadow">
                <p className="text-sm font-medium">Area: {polygonArea.toFixed(2)} m²</p>
              </div>
            )}

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
                        <li>Area: {turf.area(item.polygon).toFixed(2)} m²</li>
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
