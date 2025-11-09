import React from 'react';
import PatientDashboard from './components/PatientDashboard';
import './App.css';

function App() {
  return (
    <div className="app">
      <div className="app-header">
        <div className="header-brand">
          <div className="brand-logo">
            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none">
              <path d="M5 12h3.5l1-3 1 2h2.5l1-2 1 3h3.5" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round" fill="none"/>
            </svg>
          </div>
          <div className="brand-text">
            <h1>shino.ai</h1>
            <span className="brand-subtitle">Clinical Intake Platform</span>
          </div>
        </div>
        <nav className="header-nav">
          <button className="header-btn header-btn-active">
            <span className="btn-icon">
              <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <line x1="6" y1="20" x2="6" y2="10"/>
                <line x1="12" y1="20" x2="12" y2="4"/>
                <line x1="18" y1="20" x2="18" y2="14"/>
              </svg>
            </span>
            <span>Dashboard</span>
          </button>
          <button className="header-btn">
            <span className="btn-icon">
              <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <rect x="3" y="4" width="18" height="18" rx="2"/>
                <line x1="16" y1="2" x2="16" y2="6"/>
                <line x1="8" y1="2" x2="8" y2="6"/>
                <line x1="3" y1="10" x2="21" y2="10"/>
              </svg>
            </span>
            <span>Schedule</span>
          </button>
          <button className="header-btn">
            <span className="btn-icon">
              <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <polyline points="3 17 9 11 13 15 21 7"/>
              </svg>
            </span>
            <span>Analytics</span>
          </button>
        </nav>
        <div className="header-actions">
          <button className="header-btn-secondary">
            <span className="btn-icon">
              <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <path d="M6 8a6 6 0 0 1 12 0c0 7 3 9 3 9H3s3-2 3-9"/>
                <path d="M13.73 21a2 2 0 0 1-3.46 0"/>
              </svg>
            </span>
          </button>
          <button className="header-btn-primary">
            <svg xmlns="http://www.w3.org/2000/svg" width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <line x1="12" y1="5" x2="12" y2="19"/>
              <line x1="5" y1="12" x2="19" y2="12"/>
            </svg>
            <span>New Patient</span>
          </button>
        </div>
      </div>
      <PatientDashboard />
    </div>
  );
}

export default App;
