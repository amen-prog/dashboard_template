import React from 'react';
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import OperationsTab from './OperationsTab';
import StatisticsTab from './StatisticsTab';
import AlertsTab from './AlertsTab';
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

const data = [
  { name: 'Jan', value: 400 },
  { name: 'Feb', value: 300 },
  { name: 'Mar', value: 600 },
  { name: 'Apr', value: 800 },
  { name: 'May', value: 500 },
];

const DashboardOverview = () => {
  return (
    <div className="grid grid-cols-2 gap-4">
      <Card>
        <CardHeader>
          <CardTitle>Overview Chart</CardTitle>
        </CardHeader>
        <CardContent>
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={data}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="name" />
              <YAxis />
              <Tooltip />
              <Legend />
              <Line type="monotone" dataKey="value" stroke="#8884d8" activeDot={{ r: 8 }} />
            </LineChart>
          </ResponsiveContainer>
        </CardContent>
      </Card>
      <Card>
        <CardHeader>
          <CardTitle>Key Metrics</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 gap-4">
            <div className="text-center">
              <h3 className="text-2xl font-bold">95%</h3>
              <p className="text-sm text-muted-foreground">Uptime</p>
            </div>
            <div className="text-center">
              <h3 className="text-2xl font-bold">1.2M</h3>
              <p className="text-sm text-muted-foreground">Active Users</p>
            </div>
            <div className="text-center">
              <h3 className="text-2xl font-bold">$3.4M</h3>
              <p className="text-sm text-muted-foreground">Revenue</p>
            </div>
            <div className="text-center">
              <h3 className="text-2xl font-bold">24.5k</h3>
              <p className="text-sm text-muted-foreground">New Signups</p>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

const DashboardTabs = () => {
  return (
    <Tabs defaultValue="dashboard" className="w-full">
      <TabsList>
        <TabsTrigger value="dashboard">Dashboard</TabsTrigger>
        <TabsTrigger value="operations">Operations</TabsTrigger>
        <TabsTrigger value="statistics">Statistics</TabsTrigger>
        <TabsTrigger value="alerts">Alerts</TabsTrigger>
      </TabsList>
      <TabsContent value="dashboard">
        <DashboardOverview />
      </TabsContent>
      <TabsContent value="operations">
        <OperationsTab />
      </TabsContent>
      <TabsContent value="statistics">
        <StatisticsTab />
      </TabsContent>
      <TabsContent value="alerts">
        <AlertsTab />
      </TabsContent>
    </Tabs>
  );
};

export default DashboardTabs;