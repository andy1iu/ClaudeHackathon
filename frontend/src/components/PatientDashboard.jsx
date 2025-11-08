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
      <div className="greeting-header">
        <h1>Hello Doctor Shino!</h1>
      </div>
      <div className="dashboard-header">
        <h2>Patients</h2>
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
        <table className="patients-table">
        <thead>
          <tr>
            <th>Patient ID</th>
            <th>Full Name</th>
            <th>Age / Gender</th>
            <th>Status</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          {patients.map((patient) => (
            <tr key={patient.patient_id}>
              <td>{patient.patient_id}</td>
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
                    <span className="icon-shape icon-ring"></span>
                  )}
                  {patient.briefing_status}
                </span>
              </td>
              <td>
                <div style={{ display: 'flex', gap: '8px', flexWrap: 'wrap' }}>
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
