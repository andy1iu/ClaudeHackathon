import React from 'react';

const BriefingView = ({ patient, briefing, onClose }) => {
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

  const formatDate = (dateString) => {
    const date = new Date(dateString);
    return date.toLocaleString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <h3>Clinical Briefing</h3>
          <div className="patient-info">
            {patient.full_name} | {calculateAge(patient.date_of_birth)} years old |{' '}
            {patient.gender_identity} | Generated: {formatDate(briefing.created_at)}
          </div>
        </div>

        <div className="briefing-view">
          {/* AI Summary Section */}
          <div className="briefing-section">
            <h4>Clinical Summary</h4>
            <div className="briefing-summary">
              {briefing.ai_summary}
            </div>
          </div>

          {/* Key Insights & Flags Section */}
          <div className="briefing-section">
            <h4>Key Insights & Clinical Flags</h4>
            {briefing.key_insights_flags && briefing.key_insights_flags.length > 0 ? (
              briefing.key_insights_flags.map((insight, index) => (
                <div
                  key={index}
                  className={`insight-card ${insight.type.toLowerCase()}`}
                >
                  <div className="insight-header">
                    <span className={`insight-type ${insight.type.toLowerCase()}`}>
                      {insight.type}
                    </span>
                    <span className="insight-flag">{insight.flag}</span>
                  </div>
                  <div className="insight-reasoning">{insight.reasoning}</div>
                </div>
              ))
            ) : (
              <p>No key insights flagged.</p>
            )}
          </div>

          {/* Reported Symptoms Section */}
          <div className="briefing-section">
            <h4>Reported Symptoms (Structured)</h4>
            {briefing.reported_symptoms_structured &&
            briefing.reported_symptoms_structured.length > 0 ? (
              <ul className="symptom-list">
                {briefing.reported_symptoms_structured.map((symptom, index) => (
                  <li key={index}>
                    <div className="symptom-name">{symptom.symptom}</div>
                    <div className="symptom-details">
                      {symptom.quality && <span>Quality: {symptom.quality} | </span>}
                      {symptom.location && <span>Location: {symptom.location} | </span>}
                      {symptom.timing && <span>Timing: {symptom.timing}</span>}
                    </div>
                  </li>
                ))}
              </ul>
            ) : (
              <p>No structured symptoms recorded.</p>
            )}
          </div>

          {/* Relevant Medical History Section */}
          <div className="briefing-section">
            <h4>Relevant Medical History</h4>
            {briefing.relevant_history_surfaced &&
            briefing.relevant_history_surfaced.length > 0 ? (
              <ul className="history-list">
                {briefing.relevant_history_surfaced.map((item, index) => (
                  <li key={index}>{item}</li>
                ))}
              </ul>
            ) : (
              <p>No relevant history surfaced.</p>
            )}
          </div>
        </div>

        <div className="modal-actions">
          <button className="btn btn-primary" onClick={onClose}>
            Close
          </button>
        </div>
      </div>
    </div>
  );
};

export default BriefingView;
