// src/App.tsx
import React, { useState, useEffect, useRef, useCallback } from 'react';
import mapboxgl from 'mapbox-gl';
import MapboxDraw from '@mapbox/mapbox-gl-draw';
import '@mapbox/mapbox-gl-draw/dist/mapbox-gl-draw.css';
import * as turf from '@turf/turf';
import axios from 'axios';
import FormData from 'form-data';
import '../../mapbox-custom.css';
import { Button } from "@/components/ui/button";

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

}

const Map: React.FC<MapProps> = ({drawingEnabled, searchEnabled, equipmentDrawingEnabled}) => {
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


    const [isUploading, setIsUploading] = useState(false);
    const [uploadError, setUploadError] = useState<string | null>(null);

    const updateArea = useCallback(() => {
      if (drawRef.current) {
          const data = drawRef.current.getAll();
          const polygon = data.features[0];

          if (polygon) {
              const area = turf.area(polygon);
              setPolygonArea(area);

              if (equipmentDrawingEnabled && selectedEquipment) {
                  setDrawnEquipment(prev => [...prev, { equipment: selectedEquipment, polygon }]);
                  drawRef.current.deleteAll();
              }
          }
      }
  }, [equipmentDrawingEnabled, selectedEquipment]);

    useEffect(() => {
        if (mapContainerRef.current) {
            const map = new mapboxgl.Map({
                container: mapContainerRef.current,
                style: state ? 'mapbox://styles/mapbox/streets-v11' : 'mapbox://styles/mapbox/satellite-v9',
                center: [-102.6, 32],
                zoom: 9,
            });

            map.on('load', function () {
              if (drawingEnabled || equipmentDrawingEnabled){

                const draw = new MapboxDraw({
                    displayControlsDefault: false,
                    controls: {
                        polygon: true,
                        trash: true
                    }
                });

                map.addControl(draw as unknown as mapboxgl.IControl);
                drawRef.current = draw;

                map.on('draw.create', updateArea);
                    map.on('draw.update', updateArea);
                    map.on('draw.delete', () => {
                        setPolygonArea(null);
                        if (equipmentDrawingEnabled) {
                            setDrawnEquipment(prev => prev.slice(0, -1));
                        }
                    });
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
              if (mapRef.current) {
                mapRef.current.off('draw.create', updateArea);
                mapRef.current.off('draw.update', updateArea);
                mapRef.current.off('draw.delete');
                mapRef.current.remove();
            }
            }
        }
    }, [state, drawingEnabled, equipmentDrawingEnabled, selectedEquipment]);

    const handleEquipmentSelect = (event: React.ChangeEvent<HTMLSelectElement>) => {
      const selected = equipmentTypes.find(eq => eq.id === event.target.value);
      setSelectedEquipment(selected || null);
    };

    return <div className="w-full h-full relative">
        <div className="absolute top-0 bottom-0 w-[100%] h-[100%] left-0" ref={mapContainerRef}>
            <Button className='absolute top-0 w-[90px] h-[50px] left-0 m-5' onClick={satView}>
                Change view
            </Button>
            {searchEnabled && (
          <div className='flex flex-col absolute top-20'>
            <input
              type="text"
              value={lat}
              onChange={(e) => setLat(e.target.value)}
              placeholder='Enter Latitude'
              className='w-[150px] m-5'
            />
            <input
              type="text"
              value={lng}
              onChange={(e) => setLng(e.target.value)}
              placeholder='Enter Longitude'
              className='w-[150px] m-5'
            />
            <Button onClick={searchLocation} className='w-[150px] m-5'>Search</Button>
          </div>
        )}
        {searchPerformed && !searchEnabled && (
          <div className='absolute top-20 left-0 m-5 p-5 bg-white'>
            <p>Last searched location: {lat}, {lng}</p>
          </div>
        )}

{equipmentDrawingEnabled && (
                    <div className='absolute top-20 right-0 m-5 p-5 bg-white'>
                        <select onChange={handleEquipmentSelect} value={selectedEquipment?.id || ''}>
                            <option value="">Select Equipment</option>
                            {equipmentTypes.map(eq => (
                                <option key={eq.id} value={eq.id}>{eq.name}</option>
                            ))}
                        </select>
                        {selectedEquipment && (
                            <p>Selected: {selectedEquipment.name}</p>
                        )}
                    </div>
                )}
                {drawnEquipment.length > 0 && (
                    <div className='absolute bottom-0 right-0 m-5 p-5 bg-white overflow-auto max-h-[50%]'>
                        <h3>Drawn Equipment:</h3>
                        <ul>
                            {drawnEquipment.map((item, index) => (
                                <li key={index} className="mb-4">
                                    <strong>{item.equipment.name}</strong>
                                    <ul>
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
                {polygonArea !== null && (
                    <div className='absolute bottom-0 left-0 m-5 p-5 bg-white'>
                        <p>Polygon Area: {polygonArea.toFixed(2)} square meters</p>
                    </div>
                )}
        </div>
    </div>;
};

export default Map;
