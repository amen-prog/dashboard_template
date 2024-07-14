import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"

const OperationsTab: React.FC = () => {
  return (
    <div className="space-y-4">
      <h2 className="text-2xl font-bold">Operations</h2>
      <div className="grid grid-cols-3 gap-4">
        <div className="col-span-2 bg-secondary h-96">Map Placeholder</div>
        <div className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Methane Stats</CardTitle>
            </CardHeader>
            <CardContent>Summary cards for methane stats</CardContent>
          </Card>
          <Card>
            <CardHeader>
              <CardTitle>Map Legend</CardTitle>
            </CardHeader>
            <CardContent>Detailed legend of the map</CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
};

export default OperationsTab;