import React, { useState, useEffect } from 'react';
import { patientsApi } from '../services/api';

const NarrativeModal = ({ patient, onClose, onBriefingGenerated }) => {
  const [narratives, setNarratives] = useState([]);
  const [selectedNarrative, setSelectedNarrative] = useState(null);
  const [loading, setLoading] = useState(true);
  const [processing, setProcessing] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    loadNarratives();
  }, [patient]);

  const loadNarratives = async () => {
    try {
      setLoading(true);
      const data = await patientsApi.getNarratives(patient.patient_id);
      setNarratives(data);
      if (data.length > 0) {
        setSelectedNarrative(data[0]);
      }
      setError(null);
    } catch (err) {
      setError('Failed to load narratives.');
      console.error('Error loading narratives:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleNarrativeChange = (e) => {
    const narrativeId = e.target.value;
    const narrative = narratives.find((n) => n.narrative_id === narrativeId);
    setSelectedNarrative(narrative);
  };

  const handleGenerateBriefing = async () => {
    if (!selectedNarrative) return;

    try {
      setProcessing(true);
      setError(null);
      await patientsApi.synthesizeBriefing(
        patient.patient_id,
        selectedNarrative.narrative_text
      );
      onBriefingGenerated();
    } catch (err) {
      setError('Failed to generate briefing. Please check your API key and try again.');
      console.error('Error generating briefing:', err);
    } finally {
      setProcessing(false);
    }
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

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <h3>Patient Intake Simulation</h3>
          <div className="patient-info">
            {patient.full_name} | {calculateAge(patient.date_of_birth)} years old |{' '}
            {patient.gender_identity}
          </div>
        </div>

        {error && (
          <div className="error-message">
            {error}
          </div>
        )}

        {loading ? (
          <div className="loading-spinner">
            <div className="spinner"></div>
            <p>Loading narratives...</p>
          </div>
        ) : processing ? (
          <div className="loading-spinner">
            <div className="spinner"></div>
            <p>Generating clinical briefing with AI...</p>
            <p style={{ fontSize: '14px', color: '#6c757d', marginTop: '8px' }}>
              This may take a few seconds...
            </p>
          </div>
        ) : (
          <>
            <div className="narrative-selector">
              <label htmlFor="narrative-select">
                Select Patient Narrative:
              </label>
              <select
                id="narrative-select"
                value={selectedNarrative?.narrative_id || ''}
                onChange={handleNarrativeChange}
              >
                {narratives.map((narrative) => (
                  <option key={narrative.narrative_id} value={narrative.narrative_id}>
                    {narrative.narrative_title}
                  </option>
                ))}
              </select>

              {selectedNarrative && (
                <div className="narrative-preview">
                  <h4>Patient's Words:</h4>
                  <p>{selectedNarrative.narrative_text}</p>
                </div>
              )}
            </div>

            <div className="modal-actions">
              <button className="btn btn-secondary" onClick={onClose}>
                Cancel
              </button>
              <button
                className="btn btn-primary"
                onClick={handleGenerateBriefing}
                disabled={!selectedNarrative}
              >
                Generate Clinical Briefing
              </button>
            </div>
          </>
        )}
      </div>
    </div>
  );
};

export default NarrativeModal;
