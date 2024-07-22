import React from 'react';
import { Link as ScrollLink, Element } from 'react-scroll';
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import Map from '../Dashboard/Map'

const Dashboard: React.FC = () => {
  return (
    <div className="container mx-auto p-4">
      <nav className="mb-8">
        <ul className="flex space-x-4">
          <li>
            <ScrollLink to="operations" smooth={true} duration={500}>
              <Button variant="ghost">Operations</Button>
            </ScrollLink>
          </li>
          <li>
            <ScrollLink to="statistics" smooth={true} duration={500}>
              <Button variant="ghost">Statistics</Button>
            </ScrollLink>
          </li>
          <li>
            <ScrollLink to="alarms" smooth={true} duration={500}>
              <Button variant="ghost">Alarms</Button>
            </ScrollLink>
          </li>
        </ul>
      </nav>

      <Element name="operations" className="mb-16">
        <Card>
          <CardHeader>
            <CardTitle>Operations</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-3 gap-4">
              <div className="col-span-2 bg-secondary h-96 flex items-center justify-center">
               <Map drawingEnabled={false} searchEnabled={true} equipmentDrawingEnabled={false}/>
              </div>
              <div className="space-y-4">
                <Card>
                  <CardHeader>
                    <CardTitle>Methane Stats</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <p>Total Emissions: 1000 kg</p>
                    <p>Peak Concentration: 5 ppm</p>
                  </CardContent>
                </Card>
                <Card>
                  <CardHeader>
                    <CardTitle>Map Legend</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <ul>
                      <li>Red: High Concentration</li>
                      <li>Yellow: Medium Concentration</li>
                      <li>Green: Low Concentration</li>
                    </ul>
                  </CardContent>
                </Card>
              </div>
            </div>
          </CardContent>
        </Card>
      </Element>

      <Element name="statistics" className="mb-16">
        <Card>
          <CardHeader>
            <CardTitle>Statistics</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-2 gap-4">
              <Card>
                <CardHeader>
                  <CardTitle>Daily Emissions</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="h-64 bg-secondary flex items-center justify-center">
                    Chart Placeholder
                  </div>
                </CardContent>
              </Card>
              <Card>
                <CardHeader>
                  <CardTitle>Monthly Trends</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="h-64 bg-secondary flex items-center justify-center">
                    Chart Placeholder
                  </div>
                </CardContent>
              </Card>
            </div>
          </CardContent>
        </Card>
      </Element>

      <Element name="alarms" className="mb-16">
        <Card>
          <CardHeader>
            <CardTitle>Alarms</CardTitle>
          </CardHeader>
          <CardContent>
            <ul className="space-y-2">
              <li className="flex justify-between items-center bg-red-100 p-2 rounded">
                <span>High Methane Concentration Detected</span>
                <span className="text-sm text-gray-500">2 hours ago</span>
              </li>
              <li className="flex justify-between items-center bg-yellow-100 p-2 rounded">
                <span>Equipment Malfunction Warning</span>
                <span className="text-sm text-gray-500">1 day ago</span>
              </li>
              <li className="flex justify-between items-center bg-green-100 p-2 rounded">
                <span>Scheduled Maintenance Reminder</span>
                <span className="text-sm text-gray-500">3 days ago</span>
              </li>
            </ul>
          </CardContent>
        </Card>
      </Element>
    </div>
  );
};

export default Dashboard;