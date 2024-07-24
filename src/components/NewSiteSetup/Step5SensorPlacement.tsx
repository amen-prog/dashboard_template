import React from 'react'
import { Card, CardContent } from "@/components/ui/card";
import Map from '../Dashboard/Map';

const Step5SensorPlacement: React.FC = () => {
  return (
    <Card>
      <CardContent>
        <div className="grid grid-cols-3 gap-4 w-full">
          <div className="col-span-3 w-full bg-secondary h-96 flex items-center justify-center">
            <Map 
              drawingEnabled={true} 
              searchEnabled={false} 
              equipmentDrawingEnabled={false}
            />
          </div>
        </div>
      </CardContent>
    </Card>
  )
}

export default Step5SensorPlacement