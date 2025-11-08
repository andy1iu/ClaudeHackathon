import React from 'react';
import PatientDashboard from './components/PatientDashboard';
import './App.css';

function App() {
  return (
    <div className="app">
      <div className="app-header">
        <h1>Amani Clinical Intake - Virtual Clinic Demo</h1>
        <p>
          Experience game-changing pre-appointment insights by synthesizing patient narratives
          with historical data
        </p>
      </div>
      <PatientDashboard />
    </div>
  );
}

export default App;
