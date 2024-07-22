import React, { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import Map from '../Dashboard/Map';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

const emissionsData = [
  { name: 'Jan', value: 4000 },
  { name: 'Feb', value: 3000 },
  { name: 'Mar', value: 2000 },
  { name: 'Apr', value: 2780 },
  { name: 'May', value: 1890 },
  { name: 'Jun', value: 2390 },
];

const trendsData = [
  { name: 'Week 1', value: 2400 },
  { name: 'Week 2', value: 1398 },
  { name: 'Week 3', value: 9800 },
  { name: 'Week 4', value: 3908 },
];

const Dashboard: React.FC = () => {
  const [activeChart, setActiveChart] = useState<'emissions' | 'trends'>('emissions');

  return (
    <div className="container mx-auto p-4">
      <div className="grid grid-cols-3 gap-4 mb-8">
        <Card className="col-span-1">
          <CardHeader>
            <CardTitle>Methane Stats</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex justify-between">
              <div>
                <p className="text-sm text-muted-foreground">Total Emissions</p>
                <p className="text-2xl font-bold">1000 kg</p>
              </div>
              <div>
                <p className="text-sm text-muted-foreground">Peak Concentration</p>
                <p className="text-2xl font-bold">5 ppm</p>
              </div>
            </div>
          </CardContent>
        </Card>
        <Card className="col-span-1">
          <CardHeader>
            <CardTitle>Map Legend</CardTitle>
          </CardHeader>
          <CardContent>
            <ul className="flex justify-between">
              <li className="flex items-center">
                <span className="w-3 h-3 bg-red-500 mr-2 rounded-full"></span>
                <span>High</span>
              </li>
              <li className="flex items-center">
                <span className="w-3 h-3 bg-yellow-500 mr-2 rounded-full"></span>
                <span>Medium</span>
              </li>
              <li className="flex items-center">
                <span className="w-3 h-3 bg-green-500 mr-2 rounded-full"></span>
                <span>Low</span>
              </li>
            </ul>
          </CardContent>
        </Card>
        <Card className="col-span-1">
          <CardHeader>
            <CardTitle>Alarms</CardTitle>
          </CardHeader>
          <CardContent>
            <ul className="space-y-2">
              <li className="flex items-center">
                <span className="w-3 h-3 bg-red-500 mr-2 rounded-full"></span>
                <span className="text-sm">High Methane Concentration</span>
              </li>
              <li className="flex items-center">
                <span className="w-3 h-3 bg-yellow-500 mr-2 rounded-full"></span>
                <span className="text-sm">Equipment Malfunction</span>
              </li>
            </ul>
          </CardContent>
        </Card>
      </div>

      <div className="grid grid-cols-2 gap-4">
        <Card className="col-span-1">
          <CardContent className="p-0">
            <Map drawingEnabled={false} searchEnabled={true} equipmentDrawingEnabled={false}/>
          </CardContent>
        </Card>
        <div className="col-span-1 space-y-4">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between">
              <CardTitle>Statistics</CardTitle>
              <div>
                <Button 
                  variant={activeChart === 'emissions' ? 'default' : 'outline'}
                  onClick={() => setActiveChart('emissions')}
                  className="mr-2"
                >
                  Emissions
                </Button>
                <Button 
                  variant={activeChart === 'trends' ? 'default' : 'outline'}
                  onClick={() => setActiveChart('trends')}
                >
                  Trends
                </Button>
              </div>
            </CardHeader>
            <CardContent>
              <ResponsiveContainer width="100%" height={300}>
                {activeChart === 'emissions' ? (
                  <LineChart data={emissionsData}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="name" />
                    <YAxis />
                    <Tooltip />
                    <Legend />
                    <Line type="monotone" dataKey="value" stroke="#8884d8" activeDot={{ r: 8 }} />
                  </LineChart>
                ) : (
                  <LineChart data={trendsData}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="name" />
                    <YAxis />
                    <Tooltip />
                    <Legend />
                    <Line type="monotone" dataKey="value" stroke="#82ca9d" activeDot={{ r: 8 }} />
                  </LineChart>
                )}
              </ResponsiveContainer>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;