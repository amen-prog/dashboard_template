import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"

const StatisticsTab: React.FC = () => {
  return (
    <div className="space-y-4 mt-8">
      <h2 className="text-2xl font-bold">Statistics</h2>
      <Card>
        <CardHeader>
          <CardTitle>Statistical Analysis</CardTitle>
        </CardHeader>
        <CardContent>
          <p>Detailed statistical analysis and charts will go here</p>
        </CardContent>
      </Card>
    </div>
  );
};

export default StatisticsTab;