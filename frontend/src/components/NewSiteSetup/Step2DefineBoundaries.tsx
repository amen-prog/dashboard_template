import React, { useState } from 'react'
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import Map from '../Dashboard/Map';
import axios from 'axios';

interface Step2DefineBoundariesProps {
  onBoundaryChange: (boundary: GeoJSON.Feature | null) => void;
}

const Step2DefineBoundaries: React.FC<Step2DefineBoundariesProps> = ({ onBoundaryChange }) => {
  const [showOffsiteQuestion, setShowOffsiteQuestion] = useState(true);
  const [hasOffsiteEmissions, setHasOffsiteEmissions] = useState<boolean | null>(null);

  const handleOffsiteResponse = async (response: boolean) => {
    setHasOffsiteEmissions(response);
    setShowOffsiteQuestion(false);

    try {
      const result = await axios.post('http://localhost:5000/boundaries', {
        hasOffsiteEmissions: response
      }, {
        headers: {
          'Content-Type': 'application/json'
        }
      });
      console.log('Server response:', result.data);
    } catch (error) {
      console.error('Error sending data to server:', error);
    }
  };

  return (
    <Card>
      <CardContent>
        <div className="grid grid-cols-3 gap-4 w-full">
          {showOffsiteQuestion && (
            <div className="col-span-3 mb-4">
              <p className="mb-2">Are there any offsite emissions that you would like to delineate?</p>
              <div className="flex gap-2">
                <Button onClick={() => handleOffsiteResponse(true)}>Yes</Button>
                <Button onClick={() => handleOffsiteResponse(false)}>No</Button>
              </div>
            </div>
          )}
          {!showOffsiteQuestion && (
            <div className="col-span-3 mb-4">
              <p>
                {hasOffsiteEmissions 
                  ? "Please delineate the offsite emissions on the map."
                  : "No offsite emissions to delineate. You can proceed with defining the main boundary."}
              </p>
            </div>
          )}
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