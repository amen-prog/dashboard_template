import React from 'react'
import Dashboard from '@/components/pages/Dashboard'
import { ThemeProvider } from '@/components/dark-mode/theme-provider'


const App: React.FC = () => {
  return (
    <ThemeProvider defaultTheme="dark" storageKey="vite-ui-theme">
      <Dashboard />
    </ThemeProvider>
  )
}

export default App