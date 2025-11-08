import { useState, useEffect, useRef } from 'react';
import { chatApi } from '../services/api';
import './IntakeChatModal.css';

function IntakeChatModal({ patient, onClose, onComplete }) {
  const [messages, setMessages] = useState([]);
  const [userInput, setUserInput] = useState('');
  const [conversationId, setConversationId] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [isInitializing, setIsInitializing] = useState(true);
  const [error, setError] = useState(null);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  useEffect(() => {
    initializeChat();
  }, []);

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

      // Add AI response to messages
      setMessages(prev => [...prev, response.ai_message]);

      // Check if conversation is complete
      if (response.is_complete) {
        // Wait a moment for user to read final message, then close
        setTimeout(() => {
          onComplete(response.briefing_id);
          onClose();
        }, 2000);
      }

      setError(null);
    } catch (err) {
      console.error('Failed to send message:', err);
      setError('Failed to send message. Please try again.');
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
            ×
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
                  <div className="message-content">
                    {message.content}
                  </div>
                </div>
              ))}
              {isLoading && (
                <div className="message ai-message">
                  <div className="message-content typing-indicator">
                    <span></span>
                    <span></span>
                    <span></span>
                  </div>
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
