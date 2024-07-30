import { BrowserRouter as Router, Route, Routes } from 'react-router-dom';
import Dashboard from '@/components/pages/Dashboard'
import { ThemeProvider } from '@/components/dark-mode/theme-provider'
import NewSiteSetup from '@/components/pages/NewSiteSetup';
import Header from '@/components/Layout/Header';

function App() {
  return (
<ThemeProvider defaultTheme="system" storageKey="vite-ui-theme">
<Router>
  <div className="min-h-screen bg-background text-foreground">
    <Header />
    <main className="container mx-auto p-4">
      <Routes>
        <Route path="/" element={<Dashboard />} />
        <Route path="/new-site" element={<NewSiteSetup />} />
        {/* Add other routes as needed */}
      </Routes>
    </main>
  </div>
</Router>
</ThemeProvider>
)
}

export default App

