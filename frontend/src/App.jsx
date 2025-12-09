import { useState } from 'react'
import Dashboard from './components/Dashboard'
import FamilyManagement from './pages/FamilyManagement'
import { FamilyProvider } from './contexts/FamilyContext' // Import FamilyProvider
import './App.css'

function App() {
  const [currentPage, setCurrentPage] = useState('dashboard')

  return (
    <div className="app">
      <nav className="app-nav">
        <div className="nav-brand">Bellweaver</div>
        <div className="nav-links">
          <button
            className={`nav-link ${currentPage === 'dashboard' ? 'active' : ''}`}
            onClick={() => setCurrentPage('dashboard')}
          >
            Dashboard
          </button>
          <button
            className={`nav-link ${currentPage === 'family' ? 'active' : ''}`}
            onClick={() => setCurrentPage('family')}
          >
            Family Management
          </button>
        </div>
      </nav>

      <main className="app-content">
        {currentPage === 'dashboard' && <Dashboard />}
        {currentPage === 'family' && (
          <FamilyProvider> {/* Wrap with FamilyProvider */}
            <FamilyManagement />
          </FamilyProvider>
        )}
      </main>
    </div>
  )
}

export default App