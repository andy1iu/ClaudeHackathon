import React, { useState, useEffect } from 'react';
import { patientsApi } from '../services/api';
import NarrativeModal from './NarrativeModal';
import IntakeChatModal from './IntakeChatModal';
import BriefingView from './BriefingView';
import MedicalHistoryModal from './MedicalHistoryModal';

const PatientDashboard = () => {
  const [patients, setPatients] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [selectedPatient, setSelectedPatient] = useState(null);
  const [showNarrativeModal, setShowNarrativeModal] = useState(false);
  const [showChatModal, setShowChatModal] = useState(false);
  const [showBriefingModal, setShowBriefingModal] = useState(false);
  const [showMedicalHistoryModal, setShowMedicalHistoryModal] = useState(false);
  const [briefing, setBriefing] = useState(null);
  const [selectedRows, setSelectedRows] = useState(new Set());
  const [sortConfig, setSortConfig] = useState({ key: null, direction: 'asc' });
  const [compactMode, setCompactMode] = useState(true);

  useEffect(() => {
    loadPatients();
  }, []);

  const loadPatients = async () => {
    try {
      setLoading(true);
      const data = await patientsApi.getAll();
      setPatients(data);
      setError(null);
    } catch (err) {
      setError('Failed to load patients. Please ensure the backend server is running.');
      console.error('Error loading patients:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleBeginIntake = (patient) => {
    setSelectedPatient(patient);
    setShowChatModal(true);
  };

  const handleSimulateIntake = (patient) => {
    setSelectedPatient(patient);
    setShowNarrativeModal(true);
  };

  const handleViewBriefing = async (patient) => {
    try {
      setLoading(true);
      const briefingData = await patientsApi.getBriefing(patient.patient_id);
      setBriefing(briefingData);
      setSelectedPatient(patient);
      setShowBriefingModal(true);
    } catch (err) {
      setError('Failed to load briefing.');
      console.error('Error loading briefing:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleChatComplete = (briefingId) => {
    // Refresh the patient list to update statuses
    loadPatients();
  };

  const handleBriefingGenerated = () => {
    // Refresh the patient list to update statuses
    loadPatients();
    setShowNarrativeModal(false);
  };

  const handleViewMedicalHistory = (patient) => {
    setSelectedPatient(patient);
    setShowMedicalHistoryModal(true);
  };

  const handleRowSelect = (patientId) => {
    setSelectedRows(prev => {
      const newSet = new Set(prev);
      if (newSet.has(patientId)) {
        newSet.delete(patientId);
      } else {
        newSet.add(patientId);
      }
      return newSet;
    });
  };

  const calculateAge = (dateOfBirth) => {
    const today = new Date();
    const birthDate = new Date(dateOfBirth);
    let age = today.getFullYear() - birthDate.getFullYear();
    const monthDiff = today.getMonth() - birthDate.getMonth();
    if (monthDiff < 0 || (monthDiff === 0 && today.getDate() < birthDate.getDate())) {
      age--;
    }
    return age;
  };

  const handleSort = (key) => {
    setSortConfig(prev => {
      if (prev.key === key) {
        return { key, direction: prev.direction === 'asc' ? 'desc' : 'asc' };
      }
      return { key, direction: 'asc' };
    });
  };

  const sortedPatients = [...patients].sort((a, b) => {
    if (!sortConfig.key) return 0;
    
    let aValue, bValue;
    
    switch (sortConfig.key) {
      case 'patient_id':
        aValue = a.patient_id;
        bValue = b.patient_id;
        break;
      case 'full_name':
        aValue = a.full_name;
        bValue = b.full_name;
        break;
      case 'age':
        aValue = calculateAge(a.date_of_birth);
        bValue = calculateAge(b.date_of_birth);
        break;
      case 'status':
        aValue = a.briefing_status;
        bValue = b.briefing_status;
        break;
      default:
        return 0;
    }
    
    if (aValue < bValue) return sortConfig.direction === 'asc' ? -1 : 1;
    if (aValue > bValue) return sortConfig.direction === 'asc' ? 1 : -1;
    return 0;
  });

  const handleSelectAll = () => {
    if (selectedRows.size === sortedPatients.length) {
      setSelectedRows(new Set());
    } else {
      setSelectedRows(new Set(sortedPatients.map(p => p.patient_id)));
    }
  };

  // Generate appointment times for patients (simulated)
  const generateAppointmentTime = (index) => {
    const now = new Date();
    const baseTime = new Date(now);
    baseTime.setHours(9, 0, 0, 0); // Start at 9 AM
    baseTime.setMinutes(baseTime.getMinutes() + (index * 30)); // 30-minute slots
    return baseTime;
  };

  // Get the next upcoming appointment
  const getNextAppointment = () => {
    if (patients.length === 0) return null;
    
    const now = new Date();
    const patientsWithTimes = patients.map((patient, index) => ({
      ...patient,
      appointmentTime: generateAppointmentTime(index)
    }));

    // Find the next appointment (first one after current time)
    const upcomingAppointments = patientsWithTimes.filter(p => p.appointmentTime > now);
    
    if (upcomingAppointments.length > 0) {
      return upcomingAppointments[0];
    }
    
    // If no upcoming appointments, return the first one (or last one of the day)
    return patientsWithTimes[0];
  };

  const formatAppointmentTime = (date) => {
    if (!date) return '';
    const hours = date.getHours();
    const minutes = date.getMinutes();
    const ampm = hours >= 12 ? 'PM' : 'AM';
    const displayHours = hours % 12 || 12;
    const displayMinutes = minutes.toString().padStart(2, '0');
    return `${displayHours}:${displayMinutes} ${ampm}`;
  };

  const getTimeUntilAppointment = (appointmentTime) => {
    if (!appointmentTime) return '';
    const now = new Date();
    const diff = appointmentTime - now;
    
    if (diff < 0) return 'Now';
    
    const minutes = Math.floor(diff / 1000 / 60);
    const hours = Math.floor(minutes / 60);
    const remainingMinutes = minutes % 60;
    
    if (hours > 0) {
      return `in ${hours}h ${remainingMinutes}m`;
    }
    return `in ${minutes}m`;
  };

  const nextAppointment = getNextAppointment();

  if (loading && patients.length === 0) {
    return (
      <div className="dashboard-container">
        <div className="loading-spinner">
          <div className="spinner"></div>
          <p>Loading patients...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="dashboard-container">
      <div className="greeting-section">
        <div className="greeting-content">
          <h1>Hello Doctor Shino!</h1>
          <p className="greeting-subtitle">Review patient information and prepare for your next appointments</p>
        </div>
      </div>

      <div className="next-meeting-section">
        {nextAppointment ? (
          <div className="next-meeting-card">
            <div className="next-meeting-header">
              <div className="next-meeting-label">Next Meeting</div>
            </div>
            
            <div className="next-meeting-body">
              <div className="next-meeting-primary">
                <div className="next-meeting-patient">
                  <h3 className="next-meeting-name">{nextAppointment.full_name}</h3>
                  <div className="next-meeting-meta">
                    {calculateAge(nextAppointment.date_of_birth)} years • {nextAppointment.gender_identity}
                  </div>
                </div>
              </div>
              
              <div className="next-meeting-details">
                <div className="next-meeting-detail">
                  <div className="next-meeting-detail-label">Time</div>
                  <div className="next-meeting-detail-value">{formatAppointmentTime(nextAppointment.appointmentTime)}</div>
                </div>
                <div className="next-meeting-detail">
                  <div className="next-meeting-detail-label">Starting</div>
                  <div className="next-meeting-detail-value next-meeting-time-until">{getTimeUntilAppointment(nextAppointment.appointmentTime)}</div>
                </div>
                <div className="next-meeting-detail">
                  <div className="next-meeting-detail-label">Status</div>
                  <div className={`next-meeting-detail-value next-meeting-status ${nextAppointment.briefing_status === 'Briefing Ready' ? 'status-ready' : 'status-pending'}`}>
                    {nextAppointment.briefing_status === 'Briefing Ready' ? 'Ready' : 'Pending'}
                  </div>
                </div>
              </div>
            </div>
            
            <div className="next-meeting-footer">
              <button 
                className="next-meeting-action"
                onClick={() => {
                  if (nextAppointment.briefing_status === 'Briefing Ready') {
                    handleViewBriefing(nextAppointment);
                  } else {
                    handleBeginIntake(nextAppointment);
                  }
                }}
              >
                {nextAppointment.briefing_status === 'Briefing Ready' ? 'View Briefing' : 'Begin Intake'}
                <svg width="14" height="14" viewBox="0 0 14 14" fill="none" xmlns="http://www.w3.org/2000/svg">
                  <path d="M5.25 10.5L8.75 7L5.25 3.5" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/>
                </svg>
              </button>
            </div>
          </div>
        ) : (
          <div className="quick-facts-card">
            <div className="quick-facts-header">
              <div className="quick-facts-label">Quick Facts</div>
            </div>
            <div className="quick-facts-grid">
              <div className="quick-fact">
                <div className="quick-fact-label">Today's Patients</div>
                <div className="quick-fact-value">{patients.length}</div>
              </div>
              <div className="quick-fact">
                <div className="quick-fact-label">Pending Intake</div>
                <div className="quick-fact-value">{patients.filter(p => p.briefing_status === 'Pending Intake').length}</div>
              </div>
            </div>
          </div>
        )}
      </div>
      <div className="dashboard-header">
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', width: '100%' }}>
          <h2>Patients</h2>
          <button
            className="compact-mode-toggle"
            onClick={() => setCompactMode(!compactMode)}
            style={{
              padding: '6px 12px',
              background: 'transparent',
              border: '0.5px solid rgba(0, 0, 0, 0.1)',
              borderRadius: '6px',
              fontSize: '12px',
              color: 'var(--color-text-secondary)',
              cursor: 'pointer',
              transition: 'all 0.15s ease'
            }}
          >
            {compactMode ? 'Detailed' : 'Compact'}
          </button>
        </div>
      </div>

      {error && (
        <div className="error-message">
          {error}
        </div>
      )}

      {patients.length === 0 && !loading ? (
        <div className="loading-spinner">
          <div style={{ 
            width: '48px', 
            height: '48px', 
            borderRadius: '50%', 
            border: '3px solid var(--color-border)',
            marginBottom: '16px' 
          }}></div>
          <p style={{ color: 'var(--color-text-secondary)' }}>No patients scheduled for today</p>
        </div>
      ) : (
        <>
          {selectedRows.size > 0 && (
            <div className="bulk-actions-bar">
              <span>{selectedRows.size} selected</span>
              <div style={{ display: 'flex', gap: '8px' }}>
                <button className="btn btn-secondary" onClick={() => setSelectedRows(new Set())}>
                  Clear
                </button>
              </div>
            </div>
          )}
          <div className="table-container">
            <table className={`patients-table ${compactMode ? 'compact-mode' : ''}`}>
              <thead>
                <tr>
                  <th className="sticky-column">
                    <input
                      type="checkbox"
                      checked={selectedRows.size === sortedPatients.length && sortedPatients.length > 0}
                      onChange={handleSelectAll}
                      style={{ cursor: 'pointer' }}
                    />
                  </th>
                  <th className="sticky-column sortable" onClick={() => handleSort('patient_id')}>
                    Patient ID
                    {sortConfig.key === 'patient_id' && (
                      <span className="sort-indicator">{sortConfig.direction === 'asc' ? '↑' : '↓'}</span>
                    )}
                  </th>
                  <th className="sortable" onClick={() => handleSort('full_name')}>
                    Full Name
                    {sortConfig.key === 'full_name' && (
                      <span className="sort-indicator">{sortConfig.direction === 'asc' ? '↑' : '↓'}</span>
                    )}
                  </th>
                  <th className="sortable" onClick={() => handleSort('age')}>
                    Age / Gender
                    {sortConfig.key === 'age' && (
                      <span className="sort-indicator">{sortConfig.direction === 'asc' ? '↑' : '↓'}</span>
                    )}
                  </th>
                  <th className="sortable" onClick={() => handleSort('status')}>
                    Status
                    {sortConfig.key === 'status' && (
                      <span className="sort-indicator">{sortConfig.direction === 'asc' ? '↑' : '↓'}</span>
                    )}
                  </th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {sortedPatients.map((patient) => (
                  <tr 
                    key={patient.patient_id}
                    className={`${selectedRows.has(patient.patient_id) ? 'row-selected' : ''} ${
                      patient.briefing_status === 'Briefing Ready' ? 'row-status-ready' : 'row-status-pending'
                    }`}
                  >
                    <td className="sticky-column">
                      <input
                        type="checkbox"
                        checked={selectedRows.has(patient.patient_id)}
                        onChange={() => handleRowSelect(patient.patient_id)}
                        onClick={(e) => e.stopPropagation()}
                        style={{ cursor: 'pointer' }}
                      />
                    </td>
                    <td className="sticky-column">{patient.patient_id}</td>
                    <td>{patient.full_name}</td>
                    <td>
                      {calculateAge(patient.date_of_birth)} years / {patient.gender_identity}
                    </td>
                    <td>
                      <span
                        className={`status-badge ${
                          patient.briefing_status === 'Briefing Ready'
                            ? 'status-ready'
                            : 'status-pending'
                        }`}
                      >
                        {patient.briefing_status === 'Briefing Ready' ? (
                          <span className="icon-shape icon-circle"></span>
                        ) : (
                          <span className="status-dot"></span>
                        )}
                        {patient.briefing_status}
                      </span>
                    </td>
                    <td>
                      <div style={{ display: 'flex', gap: 'var(--spacing-2)', flexWrap: 'wrap', alignItems: 'center' }}>
                        {patient.briefing_status === 'Pending Intake' ? (
                          <button
                            className="btn btn-primary"
                            onClick={() => handleBeginIntake(patient)}
                          >
                            Begin Patient Intake
                          </button>
                        ) : (
                          <button
                            className="btn btn-secondary"
                            onClick={() => handleViewBriefing(patient)}
                          >
                            View Clinical Briefing
                          </button>
                        )}
                        <button
                          className="btn btn-secondary"
                          onClick={() => handleViewMedicalHistory(patient)}
                        >
                          Medical History
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </>
      )}

      {showChatModal && selectedPatient && (
        <IntakeChatModal
          patient={selectedPatient}
          onClose={() => setShowChatModal(false)}
          onComplete={handleChatComplete}
        />
      )}

      {showNarrativeModal && selectedPatient && (
        <NarrativeModal
          patient={selectedPatient}
          onClose={() => setShowNarrativeModal(false)}
          onBriefingGenerated={handleBriefingGenerated}
        />
      )}

      {showBriefingModal && selectedPatient && briefing && (
        <BriefingView
          patient={selectedPatient}
          briefing={briefing}
          onClose={() => setShowBriefingModal(false)}
        />
      )}

      {showMedicalHistoryModal && selectedPatient && (
        <MedicalHistoryModal
          patient={selectedPatient}
          onClose={() => setShowMedicalHistoryModal(false)}
        />
      )}
    </div>
  );
};

export default PatientDashboard;
