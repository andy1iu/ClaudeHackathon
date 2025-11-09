import React, { useState, useEffect } from 'react';
import { patientsApi, appointmentsApi } from '../services/api';
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
  const [nextAppointment, setNextAppointment] = useState(null);
  const [appointmentLoading, setAppointmentLoading] = useState(true);
  const [patientAppointments, setPatientAppointments] = useState({}); // Map of patient_id -> appointments

  useEffect(() => {
    loadPatients();
    loadNextAppointment();
  }, []);

  useEffect(() => {
    // Load appointments for all patients when patients are loaded
    if (patients.length > 0) {
      loadPatientAppointments();
    }
  }, [patients]);

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

  const loadNextAppointment = async () => {
    try {
      setAppointmentLoading(true);
      const appointment = await appointmentsApi.getNextUpcoming();
      setNextAppointment(appointment);
    } catch (err) {
      console.error('Error loading next appointment:', err);
      setNextAppointment(null);
    } finally {
      setAppointmentLoading(false);
    }
  };

  const loadPatientAppointments = async () => {
    try {
      const appointmentsMap = {};
      await Promise.all(
        patients.map(async (patient) => {
          try {
            const appointments = await appointmentsApi.getByPatient(patient.patient_id, { upcoming_only: true });
            if (appointments && appointments.length > 0) {
              appointmentsMap[patient.patient_id] = appointments[0]; // Get the next upcoming
            }
          } catch (err) {
            console.error(`Error loading appointments for ${patient.patient_id}:`, err);
          }
        })
      );
      setPatientAppointments(appointmentsMap);
    } catch (err) {
      console.error('Error loading patient appointments:', err);
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
      case 'appointment':
        const aAppt = getPatientNextAppointment(a.patient_id);
        const bAppt = getPatientNextAppointment(b.patient_id);
        
        // If both have appointments, compare by date/time
        if (aAppt && bAppt) {
          aValue = new Date(aAppt.appointment_date_time).getTime();
          bValue = new Date(bAppt.appointment_date_time).getTime();
        } 
        // If only one has an appointment, it always comes first
        else if (aAppt && !bAppt) {
          return -1; // a comes first
        } 
        else if (!aAppt && bAppt) {
          return 1; // b comes first
        } 
        // If neither has an appointment, they're equal (both at bottom)
        else {
          return 0;
        }
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

  const formatAppointmentTime = (dateString) => {
    if (!dateString) return '';
    const date = new Date(dateString);
    const hours = date.getHours();
    const minutes = date.getMinutes();
    const ampm = hours >= 12 ? 'PM' : 'AM';
    const displayHours = hours % 12 || 12;
    const displayMinutes = minutes.toString().padStart(2, '0');
    return `${displayHours}:${displayMinutes} ${ampm}`;
  };

  const formatAppointmentDate = (dateString) => {
    if (!dateString) return '';
    const date = new Date(dateString);
    const today = new Date();
    const tomorrow = new Date(today);
    tomorrow.setDate(tomorrow.getDate() + 1);
    
    if (date.toDateString() === today.toDateString()) {
      return 'Today';
    } else if (date.toDateString() === tomorrow.toDateString()) {
      return 'Tomorrow';
    } else {
      return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: date.getFullYear() !== today.getFullYear() ? 'numeric' : undefined });
    }
  };

  const getTimeUntilAppointment = (appointmentDateString) => {
    if (!appointmentDateString) return '';
    const now = new Date();
    const appointmentDate = new Date(appointmentDateString);
    const diff = appointmentDate - now;
    
    if (diff < 0) return 'Now';
    
    const minutes = Math.floor(diff / 1000 / 60);
    const hours = Math.floor(minutes / 60);
    const days = Math.floor(hours / 24);
    const remainingHours = hours % 24;
    const remainingMinutes = minutes % 60;
    
    if (days > 0) {
      return `in ${days}d ${remainingHours}h`;
    } else if (hours > 0) {
      return `in ${hours}h ${remainingMinutes}m`;
    }
    return `in ${minutes}m`;
  };

  // Get patient info for the next appointment
  const getNextAppointmentPatient = () => {
    if (!nextAppointment) return null;
    return patients.find(p => p.patient_id === nextAppointment.patient_id);
  };

  const nextAppointmentPatient = getNextAppointmentPatient();

  // Get next appointment for a specific patient
  const getPatientNextAppointment = (patientId) => {
    return patientAppointments[patientId] || null;
  };

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
        {appointmentLoading ? (
          <div className="quick-facts-card">
            <div className="quick-facts-header">
              <div className="quick-facts-label">Loading...</div>
            </div>
          </div>
        ) : nextAppointment && nextAppointmentPatient ? (
          <div className="next-meeting-card">
            <div className="next-meeting-header">
              <div className="next-meeting-label">Next Meeting</div>
            </div>
            
            <div className="next-meeting-body">
              <div className="next-meeting-primary">
                <div className="next-meeting-patient">
                  <h3 className="next-meeting-name">{nextAppointmentPatient.full_name}</h3>
                  <div className="next-meeting-meta">
                    {calculateAge(nextAppointmentPatient.date_of_birth)} years • {nextAppointmentPatient.gender_identity}
                    {nextAppointment.appointment_type && ` • ${nextAppointment.appointment_type.replace('_', ' ')}`}
                  </div>
                </div>
              </div>
              
              <div className="next-meeting-details">
                <div className="next-meeting-detail">
                  <div className="next-meeting-detail-label">Date</div>
                  <div className="next-meeting-detail-value">{formatAppointmentDate(nextAppointment.appointment_date_time)}</div>
                </div>
                <div className="next-meeting-detail">
                  <div className="next-meeting-detail-label">Time</div>
                  <div className="next-meeting-detail-value">{formatAppointmentTime(nextAppointment.appointment_date_time)}</div>
                </div>
                <div className="next-meeting-detail">
                  <div className="next-meeting-detail-label">Starting</div>
                  <div className="next-meeting-detail-value next-meeting-time-until">{getTimeUntilAppointment(nextAppointment.appointment_date_time)}</div>
                </div>
                {nextAppointment.location && (
                  <div className="next-meeting-detail">
                    <div className="next-meeting-detail-label">Location</div>
                    <div className="next-meeting-detail-value">{nextAppointment.location.replace('_', ' ')}</div>
                  </div>
                )}
                <div className="next-meeting-detail">
                  <div className="next-meeting-detail-label">Status</div>
                  <div className={`next-meeting-detail-value next-meeting-status ${nextAppointmentPatient.briefing_status === 'Briefing Ready' ? 'status-ready' : 'status-pending'}`}>
                    {nextAppointmentPatient.briefing_status === 'Briefing Ready' ? 'Ready' : 'Pending'}
                  </div>
                </div>
              </div>
            </div>
            
            <div className="next-meeting-footer">
              <button 
                className="next-meeting-action"
                onClick={() => {
                  if (nextAppointmentPatient.briefing_status === 'Briefing Ready') {
                    handleViewBriefing(nextAppointmentPatient);
                  } else {
                    handleBeginIntake(nextAppointmentPatient);
                  }
                }}
              >
                {nextAppointmentPatient.briefing_status === 'Briefing Ready' ? 'View Briefing' : 'Begin Intake'}
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
            className={`view-mode-toggle ${!compactMode ? 'active' : ''}`}
            onClick={() => setCompactMode(!compactMode)}
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
            <table className={`patients-table ${compactMode ? 'compact' : 'detailed'}`}>
              <thead>
                <tr>
                  <th className="table-checkbox">
                    <input
                      type="checkbox"
                      checked={selectedRows.size === sortedPatients.length && sortedPatients.length > 0}
                      onChange={handleSelectAll}
                      aria-label="Select all patients"
                    />
                  </th>
                  <th className="table-sortable" onClick={() => handleSort('patient_id')}>
                    PATIENT ID
                    {sortConfig.key === 'patient_id' && (
                      <span className="sort-icon">{sortConfig.direction === 'asc' ? '↑' : '↓'}</span>
                    )}
                  </th>
                  <th className="table-sortable" onClick={() => handleSort('full_name')}>
                    FULL NAME
                    {sortConfig.key === 'full_name' && (
                      <span className="sort-icon">{sortConfig.direction === 'asc' ? '↑' : '↓'}</span>
                    )}
                  </th>
                  <th className="table-sortable" onClick={() => handleSort('age')}>
                    AGE / GENDER
                    {sortConfig.key === 'age' && (
                      <span className="sort-icon">{sortConfig.direction === 'asc' ? '↑' : '↓'}</span>
                    )}
                  </th>
                  <th className="table-sortable" onClick={() => handleSort('appointment')}>
                    NEXT APPOINTMENT
                    {sortConfig.key === 'appointment' && (
                      <span className="sort-icon">{sortConfig.direction === 'asc' ? '↑' : '↓'}</span>
                    )}
                  </th>
                  <th className="table-sortable" onClick={() => handleSort('status')}>
                    BRIEFING STATUS
                    {sortConfig.key === 'status' && (
                      <span className="sort-icon">{sortConfig.direction === 'asc' ? '↑' : '↓'}</span>
                    )}
                  </th>
                  <th>ACTIONS</th>
                </tr>
              </thead>
              <tbody>
                {sortedPatients.map((patient) => {
                  const nextAppt = getPatientNextAppointment(patient.patient_id);
                  return (
                    <tr key={patient.patient_id}>
                      <td className="table-checkbox">
                        <input
                          type="checkbox"
                          checked={selectedRows.has(patient.patient_id)}
                          onChange={() => handleRowSelect(patient.patient_id)}
                          onClick={(e) => e.stopPropagation()}
                        />
                      </td>
                      <td className="table-id">{patient.patient_id}</td>
                      <td className="table-name">
                        <div className="table-name-primary">{patient.full_name}</div>
                        {!compactMode && (
                          <div className="table-name-secondary">{patient.race} • {patient.address_zip_code}</div>
                        )}
                      </td>
                      <td className="table-demographics">
                        <div className="table-age">{calculateAge(patient.date_of_birth)} years</div>
                        <div className="table-gender">{patient.gender_identity}</div>
                      </td>
                      <td className="table-appointment">
                        {nextAppt ? (
                          <>
                            <div className="table-date">{formatAppointmentDate(nextAppt.appointment_date_time)}</div>
                            <div className="table-time">{formatAppointmentTime(nextAppt.appointment_date_time)}</div>
                            {!compactMode && nextAppt.location && (
                              <div className="table-location">{nextAppt.location.replace('_', ' ')}</div>
                            )}
                          </>
                        ) : (
                          <div className="table-no-appt">No appointment</div>
                        )}
                      </td>
                      <td className="table-status">
                        <span className={`status-indicator ${patient.briefing_status === 'Briefing Ready' ? 'status-ready' : 'status-pending'}`}>
                          <span className="status-dot"></span>
                          {patient.briefing_status}
                        </span>
                      </td>
                      <td className="table-actions">
                        {patient.briefing_status === 'Pending Intake' ? (
                          <button className="table-btn-primary" onClick={() => handleBeginIntake(patient)}>
                            Begin Intake
                          </button>
                        ) : (
                          <button className="table-btn-secondary" onClick={() => handleViewBriefing(patient)}>
                            View Briefing
                          </button>
                        )}
                        <button className="table-btn-secondary" onClick={() => handleViewMedicalHistory(patient)}>
                          History
                        </button>
                      </td>
                    </tr>
                  );
                })}
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
