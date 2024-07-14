import React from 'react';
import Header from '@/components/Layout/Header';
import DashboardTabs from '@/components/Dashboard/DashboardTab';

const Dashboard: React.FC = () => {
  return (
    <div className="min-h-screen bg-background text-foreground">
      <Header />
      <main className="p-4 w-full">
        <DashboardTabs />
      </main>
    </div>
  );
};

export default Dashboard;