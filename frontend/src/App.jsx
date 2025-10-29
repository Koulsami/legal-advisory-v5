import { useState, useEffect, useRef } from 'react'
import './App.css'

// Get API URL from environment or use default
const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

function App() {
  const [sessionId, setSessionId] = useState(null)
  const [messages, setMessages] = useState([])
  const [inputMessage, setInputMessage] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [apiStatus, setApiStatus] = useState('checking')
  const messagesEndRef = useRef(null)

  // Check API health on mount
  useEffect(() => {
    checkApiHealth()
  }, [])

  // Scroll to bottom when messages change
  useEffect(() => {
    scrollToBottom()
  }, [messages])

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  const checkApiHealth = async () => {
    try {
      const response = await fetch(`${API_URL}/health`)
      if (response.ok) {
        setApiStatus('connected')
        setError(null)
        // Show welcome message
        setMessages([{
          role: 'system',
          content: 'Welcome to the Legal Advisory System! Enter your case details to calculate costs under Singapore Rules of Court Order 21.'
        }])
      } else {
        setApiStatus('error')
        setError('API is not responding. Please check backend deployment.')
      }
    } catch (err) {
      setApiStatus('error')
      setError(`Cannot connect to API at ${API_URL}. Please update VITE_API_URL.`)
    }
  }

  const createSession = async () => {
    try {
      const response = await fetch(`${API_URL}/sessions`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ user_id: `user_${Date.now()}` })
      })

      if (!response.ok) throw new Error('Failed to create session')

      const data = await response.json()
      setSessionId(data.session_id)
      setMessages([{
        role: 'system',
        content: 'Session created. How can I help you with legal cost calculations today?'
      }])
      setError(null)
    } catch (err) {
      setError('Failed to create session: ' + err.message)
    }
  }

  const sendMessage = async (e) => {
    e.preventDefault()
    if (!inputMessage.trim() || loading) return  // Removed sessionId check for direct calculation

    const userMessage = inputMessage.trim()
    setInputMessage('')
    setLoading(true)
    setError(null)

    // Add user message to chat
    setMessages(prev => [...prev, { role: 'user', content: userMessage }])

    try {
      // Use DIRECT CALCULATION endpoint (like MCP demo)
      const response = await fetch(`${API_URL}/calculate`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          query: userMessage
        })
      })

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}))
        throw new Error(errorData.detail || 'Failed to calculate costs')
      }

      const data = await response.json()

      // Format the calculation result into a nice message
      const formattedMessage = `
**Cost Calculation Result**

💰 **Total Costs:** $${data.total_costs.toLocaleString()}
📊 **Cost Range:** $${data.cost_range_min.toLocaleString()} - $${data.cost_range_max.toLocaleString()}

⚖️ **Court Level:** ${data.court_level}
💵 **Claim Amount:** $${data.claim_amount.toLocaleString()}
📋 **Case Type:** ${data.case_type.replace(/_/g, ' ')}

📜 **Calculation Basis:**
${data.calculation_basis}

🔍 **Calculation Steps:**
${data.calculation_steps.map((step, i) => `${i + 1}. ${step}`).join('\n')}

⚠️ **Assumptions:**
${data.assumptions.map(a => `• ${a}`).join('\n')}

📚 **Rules Applied:**
${data.rules_applied.map(r => `• ${r}`).join('\n')}

✅ **Confidence:** ${data.confidence}
      `.trim()

      // Add assistant response
      setMessages(prev => [...prev, {
        role: 'assistant',
        content: formattedMessage,
        result: {
          calculation: {
            total_costs: data.total_costs,
            cost_range_min: data.cost_range_min,
            cost_range_max: data.cost_range_max,
            citation: data.calculation_basis,
            breakdown: data.calculation_steps
          }
        }
      }])

    } catch (err) {
      setError('Calculation failed: ' + err.message)
      setMessages(prev => [...prev, {
        role: 'error',
        content: `Sorry, I couldn't calculate costs. ${err.message}\n\nPlease make sure your query includes:\n• Court level (High Court, District Court, Magistrates Court)\n• Case type (default judgment, summary judgment, etc.)\n• Claim amount (e.g., $50,000)`
      }])
    } finally {
      setLoading(false)
    }
  }

  const resetSession = () => {
    setSessionId(null)
    setMessages([])
    setError(null)
    createSession()
  }

  return (
    <div className="app">
      <header className="header">
        <div className="header-content">
          <h1>⚖️ Legal Advisory System v5.0</h1>
          <p className="subtitle">Singapore Rules of Court - Cost Calculator</p>
          <div className="status-bar">
            <div className={`status-indicator ${apiStatus}`}>
              <span className="status-dot"></span>
              {apiStatus === 'connected' ? 'Connected' : apiStatus === 'checking' ? 'Checking...' : 'Disconnected'}
            </div>
            {sessionId && (
              <button onClick={resetSession} className="reset-btn">
                New Session
              </button>
            )}
          </div>
        </div>
      </header>

      <main className="main">
        {error && (
          <div className="error-banner">
            <strong>Error:</strong> {error}
            <button onClick={() => setError(null)}>✕</button>
          </div>
        )}

        <div className="chat-container">
          <div className="messages">
            {messages.map((msg, index) => (
              <div key={index} className={`message message-${msg.role}`}>
                {msg.role === 'user' && <div className="message-label">You</div>}
                {msg.role === 'assistant' && <div className="message-label">Legal Advisor</div>}
                {msg.role === 'system' && <div className="message-label">System</div>}

                <div className="message-content">
                  <p>{msg.content}</p>

                  {msg.result && msg.result.calculation && (
                    <div className="calculation-result">
                      <h4>📊 Calculation Result</h4>
                      <div className="result-details">
                        <div className="result-item">
                          <strong>Total Costs:</strong>
                          <span className="cost-amount">
                            ${msg.result.calculation.total_costs?.toLocaleString() || 'N/A'}
                          </span>
                        </div>
                        {msg.result.calculation.citation && (
                          <div className="result-item">
                            <strong>Citation:</strong>
                            <span>{msg.result.calculation.citation}</span>
                          </div>
                        )}
                        {msg.result.calculation.breakdown && (
                          <details className="breakdown-details">
                            <summary>View Breakdown</summary>
                            <pre>{JSON.stringify(msg.result.calculation.breakdown, null, 2)}</pre>
                          </details>
                        )}
                      </div>
                    </div>
                  )}

                  {msg.questions && msg.questions.length > 0 && (
                    <div className="follow-up-questions">
                      <h4>❓ Follow-up Questions:</h4>
                      <ul>
                        {msg.questions.map((q, i) => (
                          <li key={i}>{q}</li>
                        ))}
                      </ul>
                    </div>
                  )}

                  {msg.completeness !== undefined && (
                    <div className="completeness-bar">
                      <div className="completeness-label">
                        Completeness: {Math.round(msg.completeness * 100)}%
                      </div>
                      <div className="progress-bar">
                        <div
                          className="progress-fill"
                          style={{ width: `${msg.completeness * 100}%` }}
                        ></div>
                      </div>
                    </div>
                  )}
                </div>
              </div>
            ))}
            {loading && (
              <div className="message message-assistant">
                <div className="message-label">Legal Advisor</div>
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

          <form onSubmit={sendMessage} className="input-form">
            <input
              type="text"
              value={inputMessage}
              onChange={(e) => setInputMessage(e.target.value)}
              placeholder="Describe your case (e.g., High Court default judgment for $50,000)..."
              disabled={loading}
              className="message-input"
            />
            <button
              type="submit"
              disabled={loading || !inputMessage.trim()}
              className="send-button"
            >
              {loading ? '...' : 'Calculate'}
            </button>
          </form>

          <div className="examples">
            <p><strong>Example queries:</strong></p>
            <ul>
              <li>"I need costs for a High Court default judgment for $50,000"</li>
              <li>"What are the costs for a 3-day contested trial in District Court?"</li>
              <li>"Summary judgment in Magistrates Court for $20,000"</li>
            </ul>
          </div>
        </div>
      </main>

      <footer className="footer">
        <p>Legal Advisory System v5.0 | Powered by Hybrid AI</p>
        <p className="api-url">API: {API_URL}</p>
      </footer>
    </div>
  )
}

export default App
