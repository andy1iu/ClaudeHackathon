import { useState, useEffect, useRef } from 'react';
import { chatApi } from '../services/api';
import './IntakeChatModal.css';

function IntakeChatModal({ patient, onClose, onComplete }) {
  const [messages, setMessages] = useState([]);
  const [userInput, setUserInput] = useState('');
  const [conversationId, setConversationId] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [isInitializing, setIsInitializing] = useState(true);
  const [showThoughtProcess, setShowThoughtProcess] = useState(false);
  const [thinkingSteps, setThinkingSteps] = useState([]);
  const [displayedThinkingSteps, setDisplayedThinkingSteps] = useState([]);
  const [error, setError] = useState(null);
  const messagesEndRef = useRef(null);
  const thinkingAnimationRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  useEffect(() => {
    initializeChat();
  }, []);

  // Progressive thinking display when expanded
  useEffect(() => {
    if (showThoughtProcess && thinkingSteps.length > 0 && displayedThinkingSteps.length === 0) {
      // Clear any existing animation
      if (thinkingAnimationRef.current) {
        clearTimeout(thinkingAnimationRef.current);
      }

      // Start progressive display
      let currentIndex = 0;
      const displayNextLine = () => {
        if (currentIndex < thinkingSteps.length) {
          setDisplayedThinkingSteps(prev => [...prev, thinkingSteps[currentIndex]]);
          currentIndex++;
          thinkingAnimationRef.current = setTimeout(displayNextLine, 300); // 300ms delay between lines
        }
      };
      displayNextLine();
    } else if (!showThoughtProcess) {
      // Reset displayed steps when collapsed
      setDisplayedThinkingSteps([]);
      if (thinkingAnimationRef.current) {
        clearTimeout(thinkingAnimationRef.current);
      }
    }

    return () => {
      if (thinkingAnimationRef.current) {
        clearTimeout(thinkingAnimationRef.current);
      }
    };
  }, [showThoughtProcess, thinkingSteps]);

  const initializeChat = async () => {
    try {
      setIsInitializing(true);
      const response = await chatApi.startChat(patient.patient_id);
      setConversationId(response.conversation_id);
      setMessages([response.initial_message]);
      setError(null);
    } catch (err) {
      console.error('Failed to start chat:', err);
      setError('Failed to start conversation. Please try again.');
    } finally {
      setIsInitializing(false);
    }
  };

  const handleSendMessage = async (e) => {
    e.preventDefault();

    if (!userInput.trim() || isLoading || !conversationId) {
      return;
    }

    const userMessage = {
      role: 'user',
      content: userInput.trim()
    };

    // Add user message to UI immediately
    setMessages(prev => [...prev, userMessage]);
    setUserInput('');
    setIsLoading(true);

    try {
      const response = await chatApi.continueChat(conversationId, userMessage.content);

      // Store thinking steps for later display
      if (response.thinking && response.thinking.length > 0) {
        // Split thinking into lines for progressive display
        const allThinkingText = response.thinking.join('\n\n');
        const lines = allThinkingText.split('\n').filter(line => line.trim());

        // Store all lines (will be displayed progressively when user clicks)
        setThinkingSteps(lines);
      } else {
        setThinkingSteps([]);
      }

      // Add AI response to messages after thinking completes
      setMessages(prev => [...prev, response.ai_message]);

      // Check if conversation is complete
      if (response.is_complete) {
        // Show "Generating briefing..." message
        setMessages(prev => [...prev, {
          role: 'ai',
          content: 'Thank you! I\'m now generating your clinical briefing. This will take a moment...',
          isProcessing: true
        }]);

        // Wait a moment, then close
        setTimeout(() => {
          onComplete(response.briefing_id);
          onClose();
        }, 2000);
      }

      setError(null);
    } catch (err) {
      console.error('Failed to send message:', err);
      console.error('Error details:', err.response?.data);
      
      // Show more detailed error message
      const errorMessage = err.response?.data?.detail || err.message || 'Failed to send message. Please try again.';
      setError(errorMessage);
      
      // Remove the user message from UI since it failed
      setMessages(prev => prev.slice(0, -1));
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage(e);
    }
  };

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="chat-modal" onClick={(e) => e.stopPropagation()}>
        <div className="chat-header">
          <div>
            <h2>Patient Intake Chat</h2>
            <p className="patient-name">{patient.full_name}</p>
          </div>
          <button className="close-btn" onClick={onClose} aria-label="Close">
            <span className="icon-shape icon-plus" style={{ transform: 'rotate(45deg)' }}></span>
          </button>
        </div>

        <div className="chat-messages">
          {isInitializing ? (
            <div className="loading-state">
              <div className="spinner"></div>
              <p>Initializing conversation...</p>
            </div>
          ) : (
            <>
              {messages.map((message, index) => (
                <div
                  key={index}
                  className={`message ${message.role === 'user' ? 'user-message' : 'ai-message'}`}
                >
                  <div className={`message-content ${message.isProcessing ? 'processing-message' : ''}`}>
                    {message.isProcessing ? (
                      <div className="processing-indicator">
                        <div className="processing-spinner"></div>
                        <span>{message.content}</span>
                      </div>
                    ) : (
                      message.content
                    )}
                  </div>
                </div>
              ))}
              {isLoading && (
                <div className="message ai-message">
                  <div
                    className="message-content thinking-indicator clickable"
                    onClick={() => setShowThoughtProcess(!showThoughtProcess)}
                    title="Click to view thought process"
                  >
                    <div className="thinking-spinner"></div>
                    <span>Thinking...</span>
                    <span className="expand-icon">{showThoughtProcess ? '▼' : '▶'}</span>
                  </div>
                  {showThoughtProcess && displayedThinkingSteps.length > 0 && (
                    <div className="thought-process">
                      {displayedThinkingSteps.map((step, idx) => (
                        <div key={idx} className="thought-step dynamic">
                          {step}
                        </div>
                      ))}
                    </div>
                  )}
                  {showThoughtProcess && thinkingSteps.length > 0 && displayedThinkingSteps.length === 0 && (
                    <div className="thought-process">
                      <div className="thought-step">
                        Loading thought process...
                      </div>
                    </div>
                  )}
                </div>
              )}
              <div ref={messagesEndRef} />
            </>
          )}
        </div>

        {error && (
          <div className="error-message">
            {error}
          </div>
        )}

        <form className="chat-input-form" onSubmit={handleSendMessage}>
          <textarea
            value={userInput}
            onChange={(e) => setUserInput(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Type your message here..."
            disabled={isLoading || isInitializing}
            rows="3"
          />
          <button
            type="submit"
            disabled={!userInput.trim() || isLoading || isInitializing}
            className="send-btn"
          >
            {isLoading ? 'Sending...' : 'Send'}
          </button>
        </form>
      </div>
    </div>
  );
}

export default IntakeChatModal;
