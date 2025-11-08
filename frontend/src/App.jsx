import React from 'react';
import PatientDashboard from './components/PatientDashboard';
import './App.css';

function App() {
  return (
    <div className="app">
      <div className="app-header">
        <div className="header-brand">
          <div className="brand-logo"></div>
          <h1>shino.ai</h1>
        </div>
        <div className="header-actions">
          <button className="header-btn header-btn-active">Dashboard</button>
          <button className="header-btn">Schedule</button>
          <button className="header-btn">Analytics</button>
          <button className="header-btn header-btn-primary">+ New Patient</button>
        </div>
      </div>
      <PatientDashboard />
    </div>
  );
}

export default App;
