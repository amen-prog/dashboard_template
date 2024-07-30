import React, { useState } from 'react'
import { Card, CardContent } from "@/components/ui/card";
import Map from '../Dashboard/Map';

interface Step2DefineBoundariesProps {
  onBoundaryChange: (boundary: GeoJSON.Feature | null) => void;
}

const Step2DefineBoundaries: React.FC<Step2DefineBoundariesProps> = ({ onBoundaryChange }) => {
  return (
    <Card>
      <CardContent>
        <div className="grid grid-cols-3 gap-4 w-full">
          <div className="col-span-3 w-full bg-secondary h-96 flex items-center justify-center">
            <Map 
              drawingEnabled={true} 
              searchEnabled={false} 
              equipmentDrawingEnabled={false}
              onBoundaryChange={onBoundaryChange}
            />
          </div>
        </div>
      </CardContent>
    </Card>
  )
}

export default Step2DefineBoundaries