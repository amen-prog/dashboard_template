// src/components/Step4WindData.tsx

import React, { useState } from 'react';
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import Map from '../Dashboard/Map';
import WindRose from '../Layout/WindRose';
import { getWindData, ProcessedWindData } from '../../api/windyApi';

const Step4WindData: React.FC = () => {
  const [lat, setLat] = useState('');
  const [lng, setLng] = useState('');
  const [windData, setWindData] = useState<ProcessedWindData[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchWindData = () => {
    setLoading(true);
    setError(null);
    getWindData(parseFloat(lat), parseFloat(lng), (data, error) => {
      setLoading(false);
      if (error) {
        setError('Failed to fetch wind data. Please try again.');
        console.error('Error fetching wind data:', error);
      } else if (data) {
        setWindData(data);
      }
    });
  };

  return (
    <Card className="w-full">
      <CardContent className="space-y-4">
        <div className="w-full h-96">
          <Map drawingEnabled={true} searchEnabled={true} equipmentDrawingEnabled={true} sensorEnabled={true}/>
        </div>
        <div className="flex justify-end space-x-4">
          <Input
            type="text"
            value={lat}
            onChange={(e) => setLat(e.target.value)}
            placeholder="Enter Latitude"
            className="w-40"
          />
          <Input
            type="text"
            value={lng}
            onChange={(e) => setLng(e.target.value)}
            placeholder="Enter Longitude"
            className="w-40"
          />
          <Button onClick={fetchWindData} disabled={loading}>
            {loading ? 'Loading...' : 'Fetch Wind Data'}
          </Button>
        </div>
        {error && <p className="text-red-500 text-right">{error}</p>}
        {windData.length > 0 && (
          <div className="w-full h-96">
            <WindRose windData={windData} />
          </div>
        )}
      </CardContent>
    </Card>
  );
};

export default Step4WindData;