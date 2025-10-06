// src/components/AIChatPanel.js
import React, { useState, useRef, useEffect } from 'react';
import { Send, Bot, User, BookOpen, CheckCircle, AlertCircle } from 'lucide-react';
import { sendChatMessage } from '../services/api';

const AIChatPanel = ({ missionPlan }) => {
  const [messages, setMessages] = useState([
    {
      id: 1,
      type: 'bot',
      content: 'Hello! I\'m your NASA-enhanced Planetary Defense AI Assistant. I have access to real NASA documentation and can provide detailed answers about asteroid deflection, impact predictions, and mission strategies. What would you like to know?',
      timestamp: new Date(),
      confidence: 'high'
    }
  ]);
  const [inputMessage, setInputMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSendMessage = async () => {
    if (!inputMessage.trim()) return;

    const userMessage = {
      id: messages.length + 1,
      type: 'user',
      content: inputMessage,
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMessage]);
    const currentMessage = inputMessage;
    setInputMessage('');
    setIsLoading(true);

    try {
      // Call RAG API with mission context
      const response = await sendChatMessage(currentMessage, missionPlan);

      const botMessage = {
        id: messages.length + 2,
        type: 'bot',
        content: response.answer,
        timestamp: new Date(),
        confidence: response.confidence,
        sources: response.sources || [],
        missionContext: response.mission_context
      };

      setMessages(prev => [...prev, botMessage]);
    } catch (error) {
      console.error('Chat error:', error);
      const errorMessage = {
        id: messages.length + 2,
        type: 'bot',
        content: 'I apologize, but I encountered an error. Please ensure the backend is running on port 5000 and try again.',
        timestamp: new Date(),
        confidence: 'low',
        isError: true
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const generateAIResponse = (question, missionPlan) => {
    const questionLower = question.toLowerCase();
    
    // Mission-related questions
    if (questionLower.includes('mission') || questionLower.includes('recommend') || questionLower.includes('strategy')) {
      if (missionPlan?.mission_recommendation) {
        const rec = missionPlan.mission_recommendation;
        const asteroid = missionPlan.asteroid_info;
        return `**Mission Recommendation Analysis:**\n\nBased on my assessment of **${asteroid.name}**, I recommend:\n\n🚀 **Architecture:** ${rec.source}\n💥 **Interceptor:** ${rec.interceptor_type}\n📊 **Confidence:** ${rec.confidence_score}%\n\n**Key Factors:**\n• Asteroid Mass: ${asteroid.mass_kg.toExponential(2)} kg\n• Lead Time: ${missionPlan.mission_parameters.lti_days} days\n• Required ΔV: ${missionPlan.mission_parameters.required_dv_ms.toFixed(6)} m/s\n\n${rec.rationale}`;
      }
      return 'I need mission analysis data to provide specific recommendations. Please analyze an asteroid first using the mission controls.';
    }

    // Impact-related questions
    if (questionLower.includes('impact') || questionLower.includes('consequence') || questionLower.includes('damage')) {
      if (missionPlan?.ai_predicted_consequences) {
        const cons = missionPlan.ai_predicted_consequences;
        return `**Impact Consequence Assessment:**\n\n💥 **Energy Release:** ${cons.impact_energy_megatons.toLocaleString()} megatons of TNT\n💰 **Economic Impact:** $${(cons.economic_damage_usd / 1e12).toFixed(1)} trillion\n👥 **Casualties:** ${cons.predicted_casualties.toLocaleString()}\n🏔️ **Seismic Effects:** Magnitude ${cons.predicted_seismic_magnitude}\n💨 **Blast Radius:** ${cons.blast_radius_km} km\n🕳️ **Crater Size:** ${cons.crater_diameter_km} km diameter\n\nThis represents a **global catastrophic event** requiring immediate deflection efforts.`;
      }
      return 'I need impact consequence data to provide specific predictions. Please analyze an asteroid first.';
    }

    // Physics and deflection questions
    if (questionLower.includes('deflection') || questionLower.includes('delta-v') || questionLower.includes('physics')) {
      return `**Orbital Deflection Physics:**\n\n🎯 **Key Principle:** Small velocity changes (ΔV) applied early create large position changes later due to orbital mechanics.\n\n⚡ **Typical ΔV Requirements:**\n• 0.0001-0.001 m/s: Years of lead time\n• 0.001-0.01 m/s: Moderate timeline  \n• 0.01+ m/s: Short timeline, challenging\n\n🛰️ **Deflection Methods:**\n• **Kinetic Impactors:** Direct collision (DART mission)\n• **Gravity Tractors:** Station-keeping for momentum transfer\n• **Nuclear Disruption:** For very large asteroids\n\nThe key is **early detection** and **sufficient lead time**.`;
    }

    // Technology questions
    if (questionLower.includes('nuclear') || questionLower.includes('kinetic') || questionLower.includes('technology')) {
      return `**Deflection Technology Overview:**\n\n💥 **Kinetic Impactors (Preferred):**\n• NASA\'s DART mission demonstrated effectiveness\n• Low nuclear proliferation concerns\n• Well-understood technology\n• Best for asteroids < 500m diameter\n\n☢️ **Nuclear Disruption:**\n• Considered for large asteroids (> 500m)\n• Short timeline scenarios\n• Complex international coordination needed\n• Multiple delivery options available\n\n🛰️ **Gravity Tractors:**\n• No physical contact required\n• Very precise but slow acting\n• Requires advanced station-keeping\n• Good for final trajectory adjustments`;
    }

    // NASA and mission context
    if (questionLower.includes('nasa') || questionLower.includes('dart') || questionLower.includes('space')) {
      return `**NASA Planetary Defense Context:**\n\n🎯 **Current NASA Missions:**\n• **DART:** Successful kinetic impactor test (2022)\n• **NEO Surveyor:** Upcoming infrared telescope\n• **Planetary Defense Coordination Office:** Active monitoring\n\n🌍 **International Cooperation:**\n• UN Office for Outer Space Affairs guidelines\n• International Asteroid Warning Network\n• Space Mission Planning Advisory Group\n\n🔭 **Detection Capabilities:**\n• Ground-based telescopes worldwide\n• Space-based infrared detection\n• Automated threat assessment systems\n\nNASA leads global efforts in planetary defense coordination and technology development.`;
    }

    // General help
    if (questionLower.includes('help') || questionLower.includes('what can you do')) {
      return `**How I Can Help:**\n\n🔍 **Threat Analysis:** Explain impact consequences and risk assessments\n🚀 **Mission Planning:** Discuss deflection strategies and technologies\n📊 **Data Interpretation:** Help understand orbital mechanics and parameters\n🌍 **Planetary Defense:** Provide context about NASA and international efforts\n\n**Try asking me about:**\n• "Explain the mission recommendation for this asteroid"\n• "What would happen if this asteroid impacted Earth?"\n• "How does orbital deflection physics work?"\n• "What technologies are available for asteroid deflection?"\n• "Tell me about NASA\'s planetary defense efforts"`;
    }

    // Default response
    return `I understand you're interested in planetary defense topics. I can help you with:\n\n🎯 **Mission Analysis** - Explain AI recommendations and strategies\n💥 **Impact Assessment** - Detail potential consequences and risks\n🚀 **Deflection Physics** - Explain orbital mechanics and ΔV requirements\n🌍 **NASA Context** - Discuss current efforts and technologies\n\nCould you be more specific about what you'd like to know? For example, ask about "mission strategies," "impact predictions," or "deflection physics."`;
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  const quickQuestions = [
    "What is a Near-Earth Object?",
    "Tell me about the DART mission",
    "What is the Torino Scale?",
    "How is impact energy calculated?"
  ];

  const handleQuickQuestion = (question) => {
    setInputMessage(question);
  };

  return (
    <div className="ai-chat-panel">
      <div className="panel-header">
        <h2>💬 AI Defense Assistant</h2>
        <div className="panel-subtitle">
          Ask me about planetary defense strategies
        </div>
      </div>

      <div className="quick-questions">
        {quickQuestions.map((question, index) => (
          <button
            key={index}
            onClick={() => handleQuickQuestion(question)}
            className="quick-question-btn"
          >
            {question}
          </button>
        ))}
      </div>

      <div className="chat-messages">
        {messages.map((message) => (
          <div key={message.id} className={`message ${message.type} ${message.isError ? 'error' : ''}`}>
            <div className="message-avatar">
              {message.type === 'bot' ? <Bot size={18} /> : <User size={18} />}
            </div>
            <div className="message-content">
              <div className="message-text">{message.content}</div>

              {/* Show confidence indicator for bot messages */}
              {message.type === 'bot' && message.confidence && (
                <div className={`confidence-indicator ${message.confidence}`}>
                  {message.confidence === 'high' ? <CheckCircle size={12} /> : <AlertCircle size={12} />}
                  <span>{message.confidence} confidence</span>
                </div>
              )}

              {/* Show sources if available */}
              {message.sources && message.sources.length > 0 && (
                <div className="sources-list">
                  <div className="sources-header">
                    <BookOpen size={14} />
                    <span>Sources ({message.sources.length}):</span>
                  </div>
                  {message.sources.map((source, idx) => (
                    <div key={idx} className="source-item">
                      <strong>{source.title}</strong>
                      <div className="source-snippet">{source.snippet}</div>
                    </div>
                  ))}
                </div>
              )}

              {/* Show mission context if available */}
              {message.missionContext && (
                <div className="mission-context">
                  📊 {message.missionContext}
                </div>
              )}

              <div className="message-time">
                {message.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
              </div>
            </div>
          </div>
        ))}
        {isLoading && (
          <div className="message bot">
            <div className="message-avatar">
              <Bot size={18} />
            </div>
            <div className="message-content">
              <div className="typing-indicator">
                <span></span>
                <span></span>
                <span></span>
              </div>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      <div className="chat-input">
        <textarea
          value={inputMessage}
          onChange={(e) => setInputMessage(e.target.value)}
          onKeyPress={handleKeyPress}
          placeholder="Ask about mission strategies, impact predictions, or deflection physics..."
          rows="2"
        />
        <button 
          onClick={handleSendMessage} 
          disabled={!inputMessage.trim() || isLoading}
          className="send-button"
        >
          <Send size={16} />
        </button>
      </div>
    </div>
  );
};

export default AIChatPanel;