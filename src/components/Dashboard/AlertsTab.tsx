import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"

const AlertsTab: React.FC = () => {
  return (
    <Card>
      <CardHeader>
        <CardTitle>Alerts</CardTitle>
      </CardHeader>
      <CardContent>
        <p>Alerts content will go here</p>
      </CardContent>
    </Card>
  );
};

export default AlertsTab;