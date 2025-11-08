import React from 'react';
import PatientDashboard from './components/PatientDashboard';
import './App.css';

function App() {
  return (
    <div className="app">
      <div className="app-header">
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px', cursor: 'pointer' }}>
          <div style={{ 
            width: '20px', 
            height: '20px', 
            borderRadius: '4px',
            background: 'linear-gradient(135deg, #0070f3 0%, #00a8ff 100%)',
            boxShadow: '0 2px 8px rgba(0, 112, 243, 0.2), 0 0 0 3px rgba(0, 112, 243, 0.08)',
            transition: 'all 0.2s ease'
          }}></div>
          <h1>Amani</h1>
        </div>
      </div>
      <PatientDashboard />
    </div>
  );
}

export default App;
