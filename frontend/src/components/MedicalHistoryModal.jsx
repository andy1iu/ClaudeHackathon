import { useState, useEffect } from 'react';
import { patientsApi } from '../services/api';
import './MedicalHistoryModal.css';

function MedicalHistoryModal({ patient, onClose }) {
  const [ehrData, setEhrData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    loadEHRData();
  }, []);

  const loadEHRData = async () => {
    try {
      setLoading(true);
      const data = await patientsApi.getEHR(patient.patient_id);
      setEhrData(data);
      setError(null);
    } catch (err) {
      console.error('Failed to load EHR data:', err);
      setError('Failed to load medical history. Please try again.');
    } finally {
      setLoading(false);
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
      <div className="medical-history-modal" onClick={(e) => e.stopPropagation()}>
        {/* Header */}
        <div className="mh-header">
          <div className="mh-header-content">
            <h2 className="mh-title">{patient.full_name}</h2>
            <div className="mh-patient-info">
              <span className="mh-patient-meta">
                {calculateAge(patient.date_of_birth)} • {patient.gender_identity} • {patient.race}
              </span>
            </div>
          </div>
          <button className="mh-close-btn" onClick={onClose} aria-label="Close">
            <svg width="14" height="14" viewBox="0 0 14 14" fill="none" stroke="currentColor" strokeWidth="1.5">
              <path d="M10 3L3 10M3 3l7 7" />
            </svg>
          </button>
        </div>

        {/* Content */}
        <div className="mh-content">
          {loading ? (
            <div className="mh-loading">
              <div className="mh-spinner"></div>
              <p>Loading medical history...</p>
            </div>
          ) : error ? (
            <div className="mh-error">
              <p>{error}</p>
              <button className="mh-retry-btn" onClick={loadEHRData}>
                Retry
              </button>
            </div>
          ) : ehrData ? (
            <div className="mh-sections">
              {/* Demographics */}
              <section className="mh-section">
                <h3 className="mh-section-title">Demographics</h3>
                <div className="mh-demo-grid">
                  <div className="mh-demo-item">
                    <span className="mh-demo-label">Patient ID</span>
                    <span className="mh-demo-value">{patient.patient_id}</span>
                  </div>
                  <div className="mh-demo-item">
                    <span className="mh-demo-label">Date of Birth</span>
                    <span className="mh-demo-value">{patient.date_of_birth}</span>
                  </div>
                  <div className="mh-demo-item">
                    <span className="mh-demo-label">Age</span>
                    <span className="mh-demo-value">{calculateAge(patient.date_of_birth)} years</span>
                  </div>
                  <div className="mh-demo-item">
                    <span className="mh-demo-label">Gender</span>
                    <span className="mh-demo-value">{patient.gender_identity}</span>
                  </div>
                  <div className="mh-demo-item">
                    <span className="mh-demo-label">Race/Ethnicity</span>
                    <span className="mh-demo-value">{patient.race}</span>
                  </div>
                  <div className="mh-demo-item">
                    <span className="mh-demo-label">ZIP Code</span>
                    <span className="mh-demo-value">{patient.address_zip_code}</span>
                  </div>
                </div>
              </section>

              {/* Vital Signs */}
              {ehrData.vital_signs && (
                <section className="mh-section">
                  <div className="mh-section-header">
                    <h3 className="mh-section-title">Vital Signs</h3>
                    <span className="mh-section-date">{ehrData.vital_signs.date}</span>
                  </div>
                  <div className="mh-vitals-grid">
                    <div className="mh-vital-item">
                      <span className="mh-vital-label">Blood Pressure</span>
                      <div className="mh-vital-value">
                        <span className="mh-vital-number">{ehrData.vital_signs.bp_systolic}</span>
                        <span className="mh-vital-sep">/</span>
                        <span className="mh-vital-number">{ehrData.vital_signs.bp_diastolic}</span>
                        <span className="mh-vital-unit"> mmHg</span>
                      </div>
                    </div>
                    <div className="mh-vital-item">
                      <span className="mh-vital-label">Heart Rate</span>
                      <div className="mh-vital-value">
                        <span className="mh-vital-number">{ehrData.vital_signs.heart_rate}</span>
                        <span className="mh-vital-unit"> bpm</span>
                      </div>
                    </div>
                    <div className="mh-vital-item">
                      <span className="mh-vital-label">Respiratory Rate</span>
                      <div className="mh-vital-value">
                        <span className="mh-vital-number">{ehrData.vital_signs.respiratory_rate}</span>
                        <span className="mh-vital-unit"> breaths/min</span>
                      </div>
                    </div>
                    <div className="mh-vital-item">
                      <span className="mh-vital-label">Temperature</span>
                      <div className="mh-vital-value">
                        <span className="mh-vital-number">{ehrData.vital_signs.temperature}</span>
                        <span className="mh-vital-unit"> °F</span>
                      </div>
                    </div>
                  </div>
                </section>
              )}

              {/* Allergies */}
              <section className="mh-section">
                <h3 className="mh-section-title">Allergies</h3>
                {ehrData.allergies && ehrData.allergies.length > 0 ? (
                  <div className="mh-list">
                    {ehrData.allergies.map((allergy, index) => (
                      <div key={index} className="mh-list-item">
                        <div className="mh-list-main">
                          <span className="mh-list-name">{allergy.allergen}</span>
                          {allergy.severity && allergy.severity !== "None" && (
                            <span className={`mh-badge mh-badge-${allergy.severity.toLowerCase()}`}>
                              {allergy.severity}
                            </span>
                          )}
                        </div>
                        <div className="mh-list-detail">
                          <span className="mh-list-detail-label">Reaction:</span>
                          <span>{allergy.reaction}</span>
                        </div>
                      </div>
                    ))}
                  </div>
                ) : (
                  <div className="mh-empty">No known allergies</div>
                )}
              </section>

              {/* Problem List */}
              <section className="mh-section">
                <h3 className="mh-section-title">Active Diagnoses</h3>
                {ehrData.problem_list && ehrData.problem_list.length > 0 ? (
                  <div className="mh-list">
                    {ehrData.problem_list.map((problem, index) => (
                      <div key={index} className="mh-list-item">
                        <div className="mh-list-main">
                          <span className="mh-list-name">{problem.condition}</span>
                          <span className="mh-list-meta">ICD-10: {problem.icd10}</span>
                        </div>
                        {problem.date_diagnosed && (
                          <div className="mh-list-detail">Diagnosed: {problem.date_diagnosed}</div>
                        )}
                      </div>
                    ))}
                  </div>
                ) : (
                  <div className="mh-empty">No active problems on record</div>
                )}
              </section>

              {/* Medications */}
              <section className="mh-section">
                <h3 className="mh-section-title">Current Medications</h3>
                {ehrData.medication_list && ehrData.medication_list.length > 0 ? (
                  <div className="mh-list">
                    {ehrData.medication_list.map((medication, index) => (
                      <div key={index} className="mh-list-item">
                        <div className="mh-list-main">
                          <span className="mh-list-name">{medication.name}</span>
                        </div>
                        <div className="mh-list-detail">
                          {medication.dosage && <span>{medication.dosage}</span>}
                          {medication.dosage && medication.frequency && <span className="mh-sep"> • </span>}
                          {medication.frequency && <span>{medication.frequency}</span>}
                        </div>
                      </div>
                    ))}
                  </div>
                ) : (
                  <div className="mh-empty">No current medications</div>
                )}
              </section>

              {/* Surgical History */}
              {ehrData.surgical_history && ehrData.surgical_history.length > 0 && (
                <section className="mh-section">
                  <h3 className="mh-section-title">Surgical History</h3>
                  <div className="mh-list">
                    {ehrData.surgical_history.map((surgery, index) => (
                      <div key={index} className="mh-list-item">
                        <div className="mh-list-main">
                          <span className="mh-list-name">{surgery.procedure}</span>
                          <span className="mh-list-meta">{surgery.year}</span>
                        </div>
                        {surgery.indication && (
                          <div className="mh-list-detail">Indication: {surgery.indication}</div>
                        )}
                      </div>
                    ))}
                  </div>
                </section>
              )}

              {/* Lab Results */}
              <section className="mh-section">
                <h3 className="mh-section-title">Recent Laboratory Results</h3>
                {ehrData.recent_labs && ehrData.recent_labs.length > 0 ? (
                  <div className="mh-table-wrapper">
                    <table className="mh-table">
                      <thead>
                        <tr>
                          <th>Test</th>
                          <th>Value</th>
                          <th>Unit</th>
                          <th>Date</th>
                        </tr>
                      </thead>
                      <tbody>
                        {ehrData.recent_labs.map((lab, index) => (
                          <tr key={index}>
                            <td className="mh-table-cell">{lab.test}</td>
                            <td className="mh-table-cell mh-table-value">{lab.value}</td>
                            <td className="mh-table-cell mh-table-meta">{lab.unit || '—'}</td>
                            <td className="mh-table-cell mh-table-meta">{lab.date}</td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                ) : (
                  <div className="mh-empty">No recent lab results</div>
                )}
              </section>

              {/* Social History */}
              {ehrData.social_history && (
                <section className="mh-section">
                  <h3 className="mh-section-title">Social History</h3>
                  <div className="mh-demo-grid">
                    {ehrData.social_history.tobacco && (
                      <div className="mh-demo-item">
                        <span className="mh-demo-label">Tobacco Use</span>
                        <span className="mh-demo-value">{ehrData.social_history.tobacco}</span>
                      </div>
                    )}
                    {ehrData.social_history.alcohol && (
                      <div className="mh-demo-item">
                        <span className="mh-demo-label">Alcohol Use</span>
                        <span className="mh-demo-value">{ehrData.social_history.alcohol}</span>
                      </div>
                    )}
                    {ehrData.social_history.occupation && (
                      <div className="mh-demo-item">
                        <span className="mh-demo-label">Occupation</span>
                        <span className="mh-demo-value">{ehrData.social_history.occupation}</span>
                      </div>
                    )}
                    {ehrData.social_history.living_situation && (
                      <div className="mh-demo-item">
                        <span className="mh-demo-label">Living Situation</span>
                        <span className="mh-demo-value">{ehrData.social_history.living_situation}</span>
                      </div>
                    )}
                  </div>
                </section>
              )}

              {/* Family History */}
              {ehrData.family_history && ehrData.family_history.length > 0 && (
                <section className="mh-section">
                  <h3 className="mh-section-title">Family History</h3>
                  <div className="mh-list">
                    {ehrData.family_history.map((member, index) => (
                      <div key={index} className="mh-list-item">
                        <div className="mh-list-main">
                          <span className="mh-list-name">{member.relation}</span>
                          <span className="mh-list-meta">
                            {member.age_at_death 
                              ? `Deceased at age ${member.age_at_death} (${member.cause_of_death})`
                              : `Age: ${member.age}`
                            }
                          </span>
                        </div>
                        {member.conditions && member.conditions.length > 0 && (
                          <div className="mh-list-detail">Conditions: {member.conditions.join(', ')}</div>
                        )}
                      </div>
                    ))}
                  </div>
                </section>
              )}
            </div>
          ) : (
            <div className="mh-empty mh-empty-large">No medical history available</div>
          )}
        </div>
      </div>
    </div>
  );
}

export default MedicalHistoryModal;
