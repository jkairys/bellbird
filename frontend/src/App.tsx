import { Routes, Route, Link, useLocation } from 'react-router-dom'
import Dashboard from './components/Dashboard'
import FamilyManagement from './pages/FamilyManagement'
import { FamilyProvider } from './contexts/FamilyContext'
import './App.css'

function App() {
  const location = useLocation()

  return (
    <div className="app">
      <nav className="app-nav">
        <div className="nav-brand">Bellweaver</div>
        <div className="nav-links">
          <Link
            to="/"
            className={`nav-link ${location.pathname === '/' ? 'active' : ''}`}
          >
            Dashboard
          </Link>
          <Link
            to="/family"
            className={`nav-link ${location.pathname === '/family' ? 'active' : ''}`}
          >
            Family Management
          </Link>
        </div>
      </nav>

      <main className="app-content">
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route
            path="/family"
            element={
              <FamilyProvider>
                <FamilyManagement />
              </FamilyProvider>
            }
          />
        </Routes>
      </main>
    </div>
  )
}

export default App