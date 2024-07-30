// useMapState.ts
import { useState, useCallback } from 'react';
import * as turf from '@turf/turf';

interface EquipmentType {
  id: string;
  name: string;
  sourceHeight: number;
  isEmissionSource: boolean;
}

interface PolygonData {
  area: number;
  coordinates: number[][];
  equipment?: EquipmentType;
}

export function useMapState() {
  const [boundary, setBoundary] = useState<GeoJSON.Feature | null>(null);
  const [equipment, setEquipment] = useState<Array<{ equipment: EquipmentType, polygon: GeoJSON.Feature }>>([]);

  const updateBoundary = useCallback((feature: GeoJSON.Feature<GeoJSON.Polygon>) => {
    setBoundary(feature);
  }, []);

  const addEquipment = useCallback((equipmentItem: EquipmentType, polygon: GeoJSON.Feature<GeoJSON.Polygon>) => {
    setEquipment(prev => [...prev, { equipment: equipmentItem, polygon }]);
  }, []);

  const clearAll = useCallback(() => {
    setBoundary(null);
    setEquipment([]);
  }, []);

  return {
    boundary,
    equipment,
    updateBoundary,
    addEquipment,
    clearAll,
  };
}