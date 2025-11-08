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
        <div className="modal-header">
          <div>
            <h2>Comprehensive Medical History & EHR</h2>
            <p className="patient-info">
              {patient.full_name} • {calculateAge(patient.date_of_birth)} years old • {patient.gender_identity} • {patient.race}
            </p>
          </div>
          <button className="close-btn" onClick={onClose} aria-label="Close">
            <span className="icon-shape icon-plus" style={{ transform: 'rotate(45deg)' }}></span>
          </button>
        </div>

        <div className="modal-content">
          {loading ? (
            <div className="loading-state">
              <div className="spinner"></div>
              <p>Loading medical history...</p>
            </div>
          ) : error ? (
            <div className="error-state">
              <p>{error}</p>
              <button className="retry-btn" onClick={loadEHRData}>
                Retry
              </button>
            </div>
          ) : ehrData ? (
            <>
              {/* Patient Demographics */}
              <section className="ehr-section">
                <h3>Patient Demographics</h3>
                <div className="info-grid">
                  <div className="info-item">
                    <span className="label">Patient ID:</span>
                    <span className="value">{patient.patient_id}</span>
                  </div>
                  <div className="info-item">
                    <span className="label">Date of Birth:</span>
                    <span className="value">{patient.date_of_birth}</span>
                  </div>
                  <div className="info-item">
                    <span className="label">Age:</span>
                    <span className="value">{calculateAge(patient.date_of_birth)} years</span>
                  </div>
                  <div className="info-item">
                    <span className="label">Gender:</span>
                    <span className="value">{patient.gender_identity}</span>
                  </div>
                  <div className="info-item">
                    <span className="label">Race/Ethnicity:</span>
                    <span className="value">{patient.race}</span>
                  </div>
                  <div className="info-item">
                    <span className="label">ZIP Code:</span>
                    <span className="value">{patient.address_zip_code}</span>
                  </div>
                </div>
              </section>

              {/* Vital Signs */}
              {ehrData.vital_signs && (
                <section className="ehr-section">
                  <h3>Most Recent Vital Signs</h3>
                  <div className="info-grid">
                    <div className="info-item">
                      <span className="label">Blood Pressure:</span>
                      <span className="value">{ehrData.vital_signs.bp_systolic}/{ehrData.vital_signs.bp_diastolic} mmHg</span>
                    </div>
                    <div className="info-item">
                      <span className="label">Heart Rate:</span>
                      <span className="value">{ehrData.vital_signs.heart_rate} bpm</span>
                    </div>
                    <div className="info-item">
                      <span className="label">Respiratory Rate:</span>
                      <span className="value">{ehrData.vital_signs.respiratory_rate} breaths/min</span>
                    </div>
                    <div className="info-item">
                      <span className="label">Temperature:</span>
                      <span className="value">{ehrData.vital_signs.temperature}°F</span>
                    </div>
                    <div className="info-item">
                      <span className="label">Date Recorded:</span>
                      <span className="value">{ehrData.vital_signs.date}</span>
                    </div>
                  </div>
                </section>
              )}

              {/* Allergies */}
              <section className="ehr-section">
                <h3>Allergies</h3>
                {ehrData.allergies && ehrData.allergies.length > 0 ? (
                  <div className="allergy-list">
                    {ehrData.allergies.map((allergy, index) => (
                      <div key={index} className="allergy-item">
                        <div className="allergy-name">{allergy.allergen}</div>
                        <div className="allergy-details">
                          <span className="allergy-reaction">Reaction: {allergy.reaction}</span>
                          {allergy.severity && allergy.severity !== "None" && (
                            <span className={`allergy-severity severity-${allergy.severity.toLowerCase()}`}>
                              {allergy.severity}
                            </span>
                          )}
                        </div>
                      </div>
                    ))}
                  </div>
                ) : (
                  <p className="empty-state">No known allergies</p>
                )}
              </section>

              {/* Problem List */}
              <section className="ehr-section">
                <h3>Problem List (Active Diagnoses)</h3>
                {ehrData.problem_list && ehrData.problem_list.length > 0 ? (
                  <div className="problem-list">
                    {ehrData.problem_list.map((problem, index) => (
                      <div key={index} className="problem-item">
                        <div className="problem-name">{problem.condition}</div>
                        <div className="problem-code">
                          ICD-10: {problem.icd10}
                          {problem.date_diagnosed && ` • Diagnosed: ${problem.date_diagnosed}`}
                        </div>
                      </div>
                    ))}
                  </div>
                ) : (
                  <p className="empty-state">No active problems on record</p>
                )}
              </section>

              {/* Current Medications */}
              <section className="ehr-section">
                <h3>Current Medications</h3>
                {ehrData.medication_list && ehrData.medication_list.length > 0 ? (
                  <div className="medication-list-enhanced">
                    {ehrData.medication_list.map((medication, index) => (
                      <div key={index} className="medication-item-enhanced">
                        <div className="medication-name">{medication.name}</div>
                        <div className="medication-details">
                          {medication.dosage && <span className="medication-dosage">{medication.dosage}</span>}
                          {medication.frequency && <span className="medication-frequency"> • {medication.frequency}</span>}
                        </div>
                      </div>
                    ))}
                  </div>
                ) : (
                  <p className="empty-state">No current medications</p>
                )}
              </section>

              {/* Surgical History */}
              {ehrData.surgical_history && ehrData.surgical_history.length > 0 && (
                <section className="ehr-section">
                  <h3>Surgical History</h3>
                  <div className="surgical-history-list">
                    {ehrData.surgical_history.map((surgery, index) => (
                      <div key={index} className="surgical-item">
                        <div className="surgical-year">{surgery.year}</div>
                        <div className="surgical-details">
                          <div className="surgical-procedure">{surgery.procedure}</div>
                          {surgery.indication && (
                            <div className="surgical-indication">Indication: {surgery.indication}</div>
                          )}
                        </div>
                      </div>
                    ))}
                  </div>
                </section>
              )}

              {/* Recent Lab Results */}
              <section className="ehr-section">
                <h3>Recent Laboratory Results</h3>
                {ehrData.recent_labs && ehrData.recent_labs.length > 0 ? (
                  <div className="labs-table">
                    <table>
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
                            <td>{lab.test}</td>
                            <td className="lab-value">{lab.value}</td>
                            <td>{lab.unit || '—'}</td>
                            <td>{lab.date}</td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                ) : (
                  <p className="empty-state">No recent lab results</p>
                )}
              </section>

              {/* Social History */}
              {ehrData.social_history && (
                <section className="ehr-section">
                  <h3>Social History</h3>
                  <div className="info-grid">
                    {ehrData.social_history.tobacco && (
                      <div className="info-item">
                        <span className="label">Tobacco Use:</span>
                        <span className="value">{ehrData.social_history.tobacco}</span>
                      </div>
                    )}
                    {ehrData.social_history.alcohol && (
                      <div className="info-item">
                        <span className="label">Alcohol Use:</span>
                        <span className="value">{ehrData.social_history.alcohol}</span>
                      </div>
                    )}
                    {ehrData.social_history.occupation && (
                      <div className="info-item">
                        <span className="label">Occupation:</span>
                        <span className="value">{ehrData.social_history.occupation}</span>
                      </div>
                    )}
                    {ehrData.social_history.living_situation && (
                      <div className="info-item">
                        <span className="label">Living Situation:</span>
                        <span className="value">{ehrData.social_history.living_situation}</span>
                      </div>
                    )}
                  </div>
                </section>
              )}

              {/* Family History */}
              {ehrData.family_history && ehrData.family_history.length > 0 && (
                <section className="ehr-section">
                  <h3>Family History</h3>
                  <div className="family-history-list">
                    {ehrData.family_history.map((member, index) => (
                      <div key={index} className="family-member">
                        <div className="family-relation">{member.relation}</div>
                        <div className="family-details">
                          <div className="family-age">
                            {member.age_at_death ? (
                              <span>Deceased at age {member.age_at_death} ({member.cause_of_death})</span>
                            ) : (
                              <span>Age: {member.age}</span>
                            )}
                          </div>
                          {member.conditions && member.conditions.length > 0 && (
                            <div className="family-conditions">
                              Conditions: {member.conditions.join(', ')}
                            </div>
                          )}
                        </div>
                      </div>
                    ))}
                  </div>
                </section>
              )}
            </>
          ) : (
            <div className="empty-state">
              <p>No medical history available</p>
            </div>
          )}
        </div>

        <div className="modal-footer">
          <button className="close-footer-btn" onClick={onClose}>
            Close
          </button>
        </div>
      </div>
    </div>
  );
}

export default MedicalHistoryModal;
