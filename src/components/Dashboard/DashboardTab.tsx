import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import OperationsTab from './OperationsTab';
import StatisticsTab from './StatisticsTab';
import AlertsTab from './AlertsTab';

const DashboardTabs = () => {
  return (
    <Tabs defaultValue="operations" className="w-full">
      <TabsList>
        <TabsTrigger value="operations">Operations</TabsTrigger>
        <TabsTrigger value="statistics">Statistics</TabsTrigger>
        <TabsTrigger value="alerts">Alerts</TabsTrigger>
      </TabsList>
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