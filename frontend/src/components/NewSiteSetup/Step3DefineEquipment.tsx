import React from 'react'
import { Card, CardContent } from "@/components/ui/card";
import Map from '../Dashboard/Map';

interface EquipmentType {
  id: string;
  name: string;
  sourceHeight: number;
  isEmissionSource: boolean;
}

interface Step3DefineEquipmentProps {
  boundary: GeoJSON.Feature | null;
  onEquipmentConfirm: (equipment: Array<{ equipment: EquipmentType, polygon: GeoJSON.Feature }>) => void;
}

const Step3DefineEquipment: React.FC<Step3DefineEquipmentProps> = ({ boundary, onEquipmentConfirm }) => {
  return (
    <Card>
      <CardContent>
        <div className="grid grid-cols-3 gap-4 w-full">
          <div className="col-span-3 w-full bg-secondary h-96 flex items-center justify-center">
            <Map 
              drawingEnabled={true}
              searchEnabled={false} 
              equipmentDrawingEnabled={true}
              initialBoundary={boundary}
              onEquipmentConfirm={onEquipmentConfirm}
            />
          </div>
        </div>
      </CardContent>
    </Card>
  )
}

export default Step3DefineEquipment