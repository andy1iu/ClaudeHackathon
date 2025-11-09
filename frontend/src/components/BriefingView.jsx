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

  const getInsightIcon = (type) => {
    switch(type.toLowerCase()) {
      case 'risk':
        return <span className="icon-shape" style={{ width: '12px', height: '12px', border: '2px solid currentColor', borderRadius: '2px', transform: 'rotate(45deg)' }}></span>;
      case 'alert':
        return <span className="icon-shape icon-diamond" style={{ width: '12px', height: '12px' }}></span>;
      case 'opportunity':
        return <span className="icon-shape icon-circle" style={{ width: '12px', height: '12px' }}></span>;
      case 'medication side effect':
      case 'condition progression':
      case 'treatment efficacy':
        return <span className="icon-shape" style={{ width: '12px', height: '12px', border: '2px solid currentColor', borderRadius: '50%' }}></span>;
      default:
        return <span className="icon-shape icon-square" style={{ width: '12px', height: '12px' }}></span>;
    }
  };

  const getSeverityBadge = (severity) => {
    if (!severity) return null;
    const colors = {
      'Low': '#10b981',
      'Medium': '#f59e0b',
      'High': '#ef4444'
    };
    return (
      <span style={{
        backgroundColor: colors[severity] || '#6b7280',
        color: 'white',
        padding: '2px 8px',
        borderRadius: '4px',
        fontSize: '11px',
        fontWeight: '600',
        marginLeft: '8px'
      }}>
        {severity}
      </span>
    );
  };

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <div>
            <h3>Clinical Briefing</h3>
            <div className="patient-info">
              {patient.full_name} | {calculateAge(patient.date_of_birth)} years old |{' '}
              {patient.gender_identity} | Generated: {formatDate(briefing.created_at)}
            </div>
          </div>
          <button className="btn btn-secondary" onClick={onClose} style={{ padding: '6px' }}>
            <span className="icon-shape icon-plus" style={{ transform: 'rotate(45deg)' }}></span>
          </button>
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
                  className={`insight-card ${insight.type.toLowerCase().replace(/\s+/g, '-')}`}
                >
                  <div className="insight-header">
                    <span className={`insight-type ${insight.type.toLowerCase().replace(/\s+/g, '-')}`}>
                      {getInsightIcon(insight.type)}
                      {insight.type}
                      {getSeverityBadge(insight.severity)}
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

          {/* Health Equity & Context Section */}
          {briefing.equity_and_context_flags && briefing.equity_and_context_flags.length > 0 && (
            <div className="briefing-section equity-section">
              <h4 style={{ color: '#8b5cf6' }}>
                <span className="icon-shape" style={{ 
                  display: 'inline-block', 
                  marginRight: '8px', 
                  verticalAlign: 'middle',
                  width: '12px',
                  height: '12px',
                  backgroundColor: '#8b5cf6',
                  borderRadius: '50%'
                }}></span>
                Health Equity & Patient Context
              </h4>
              {briefing.equity_and_context_flags.map((flag, index) => (
                <div
                  key={index}
                  className="insight-card equity-flag"
                  style={{ borderLeftColor: '#8b5cf6' }}
                >
                  <div className="insight-header">
                    <span className="insight-type" style={{ color: '#8b5cf6' }}>
                      {flag.type}
                    </span>
                    <span className="insight-flag">{flag.flag}</span>
                  </div>
                  <div className="insight-reasoning">{flag.reasoning}</div>
                  {flag.recommendation && (
                    <div className="equity-recommendation" style={{
                      marginTop: '12px',
                      padding: '16px',
                      backgroundColor: '#f3e8ff',
                      borderRadius: '8px',
                      fontSize: '14px',
                      lineHeight: '1.6'
                    }}>
                      <strong style={{ color: '#7c3aed', fontSize: '15px', display: 'block', marginBottom: '8px' }}>
                        💡 Actionable Recommendation
                      </strong>
                      {typeof flag.recommendation === 'string' ? (
                        <div style={{ 
                          whiteSpace: 'pre-wrap',
                          color: '#4c1d95'
                        }}>
                          {flag.recommendation}
                        </div>
                      ) : (
                        <div style={{ color: '#4c1d95' }}>
                          {Object.entries(flag.recommendation).map(([key, value], idx) => {
                            // Clean up the key for display
                            const displayKey = key.replace(/^\(\d+\)\s*/, '').replace(/_/g, ' ');
                            
                            // Handle different value types
                            if (typeof value === 'string') {
                              return (
                                <div key={idx} style={{ marginBottom: '12px' }}>
                                  <strong style={{ display: 'block', marginBottom: '4px', color: '#7c3aed' }}>
                                    {displayKey}:
                                  </strong>
                                  <div style={{ whiteSpace: 'pre-wrap' }}>{value}</div>
                                </div>
                              );
                            } else if (Array.isArray(value)) {
                              return (
                                <div key={idx} style={{ marginBottom: '12px' }}>
                                  <strong style={{ display: 'block', marginBottom: '4px', color: '#7c3aed' }}>
                                    {displayKey}:
                                  </strong>
                                  <ul style={{ marginLeft: '20px', marginTop: '4px' }}>
                                    {value.map((item, itemIdx) => (
                                      <li key={itemIdx} style={{ marginBottom: '4px' }}>{item}</li>
                                    ))}
                                  </ul>
                                </div>
                              );
                            } else if (typeof value === 'object' && value !== null) {
                              return (
                                <div key={idx} style={{ marginBottom: '12px' }}>
                                  <strong style={{ display: 'block', marginBottom: '4px', color: '#7c3aed' }}>
                                    {displayKey}:
                                  </strong>
                                  <div style={{ marginLeft: '12px' }}>
                                    {Object.entries(value).map(([subKey, subValue], subIdx) => (
                                      <div key={subIdx} style={{ marginBottom: '8px' }}>
                                        <strong style={{ color: '#7c3aed', fontSize: '13px' }}>{subKey}:</strong>
                                        {Array.isArray(subValue) ? (
                                          <ul style={{ marginLeft: '20px', marginTop: '4px' }}>
                                            {subValue.map((item, itemIdx) => (
                                              <li key={itemIdx} style={{ marginBottom: '2px' }}>{item}</li>
                                            ))}
                                          </ul>
                                        ) : (
                                          <div style={{ marginLeft: '12px' }}>{String(subValue)}</div>
                                        )}
                                      </div>
                                    ))}
                                  </div>
                                </div>
                              );
                            }
                            return null;
                          })}
                        </div>
                      )}
                    </div>
                  )}
                </div>
              ))}
            </div>
          )}

          {/* Reported Symptoms Section */}
          <div className="briefing-section">
            <h4>
              <span className="icon-shape icon-circle" style={{ display: 'inline-block', marginRight: '8px', verticalAlign: 'middle' }}></span>
              Reported Symptoms (Structured)
            </h4>
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
            <h4>
              <span className="icon-shape icon-square" style={{ display: 'inline-block', marginRight: '8px', verticalAlign: 'middle' }}></span>
              Relevant Medical History
            </h4>
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
