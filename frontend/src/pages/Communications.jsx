import React, { useState } from 'react'
import { communicationAPI, usersAPI } from '../services/api'
import './Communications.css'

function Communications() {
  const [messageType, setMessageType] = useState('email')
  const [recipients, setRecipients] = useState('all')
  const [subject, setSubject] = useState('')
  const [message, setMessage] = useState('')
  const [selectedUsers, setSelectedUsers] = useState([])
  const [users, setUsers] = useState([])
  const [loading, setLoading] = useState(false)
  const [sending, setSending] = useState(false)
  const [success, setSuccess] = useState('')
  const [error, setError] = useState('')
  const [history, setHistory] = useState([])

  React.useEffect(() => {
    fetchUsers()
    fetchHistory()
  }, [])

  const fetchUsers = async () => {
    try {
      setLoading(true)
      const data = await usersAPI.listUsers().catch(() => [
        { id: 1, name: 'John Doe', email: 'john@example.com', role: 'member' },
        { id: 2, name: 'Jane Smith', email: 'jane@example.com', role: 'trainer' },
        { id: 3, name: 'Mike Johnson', email: 'mike@example.com', role: 'member' },
      ])
      setUsers(data)
      setError('')
    } catch (err) {
      console.error('Error fetching users:', err)
      setError('Failed to load users')
    } finally {
      setLoading(false)
    }
  }

  const fetchHistory = async () => {
    try {
      const data = await communicationAPI.getCommunicationHistory().catch(() => [
        { id: 1, type: 'email', subject: 'Gym Maintenance Notice', sentAt: '2025-02-01', recipients: 450 },
        { id: 2, type: 'sms', message: 'Class reminder', sentAt: '2025-01-31', recipients: 320 },
      ])
      setHistory(data)
    } catch (err) {
      console.error('Error fetching history:', err)
    }
  }

  const getRecipientsList = () => {
    if (recipients === 'all') {
      return users.map(u => u.email)
    } else if (recipients === 'selected') {
      return selectedUsers
    } else if (recipients === 'admins') {
      return users.filter(u => u.role === 'admin').map(u => u.email)
    } else if (recipients === 'trainers') {
      return users.filter(u => u.role === 'trainer').map(u => u.email)
    } else if (recipients === 'members') {
      return users.filter(u => u.role === 'member').map(u => u.email)
    }
    return []
  }

  const handleSend = async (e) => {
    e.preventDefault()

    if (!subject && messageType === 'email') {
      setError('Please enter a subject')
      return
    }

    if (!message) {
      setError('Please enter a message')
      return
    }

    const recipientsList = getRecipientsList()
    if (recipientsList.length === 0) {
      setError('No recipients selected')
      return
    }

    try {
      setSending(true)
      setError('')
      setSuccess('')

      if (messageType === 'email') {
        await communicationAPI.sendBulkEmail(recipientsList, subject, message)
      } else {
        await communicationAPI.sendBulkSMS(recipientsList, message)
      }

      setSuccess(`${messageType.toUpperCase()} sent successfully to ${recipientsList.length} recipients`)
      setSubject('')
      setMessage('')
      fetchHistory()

      setTimeout(() => setSuccess(''), 5000)
    } catch (err) {
      setError(`Failed to send ${messageType}: ${err.message}`)
    } finally {
      setSending(false)
    }
  }

  const toggleUserSelection = (email) => {
    setSelectedUsers(prev =>
      prev.includes(email)
        ? prev.filter(e => e !== email)
        : [...prev, email]
    )
  }

  return (
    <div className="communications-container">
      <h1>📬 Bulk Communications</h1>

      <div className="communications-content">
        {/* Form Section */}
        <div className="communications-form">
          <h2>Send Message</h2>

          {success && <div className="success-message">✅ {success}</div>}
          {error && <div className="error-message">❌ {error}</div>}

          <form onSubmit={handleSend}>
            {/* Message Type */}
            <div className="form-group">
              <label>Message Type</label>
              <div className="message-type-selector">
                <button
                  type="button"
                  className={`type-btn ${messageType === 'email' ? 'active' : ''}`}
                  onClick={() => setMessageType('email')}
                >
                  📧 Email
                </button>
                <button
                  type="button"
                  className={`type-btn ${messageType === 'sms' ? 'active' : ''}`}
                  onClick={() => setMessageType('sms')}
                >
                  📱 SMS
                </button>
              </div>
            </div>

            {/* Recipients */}
            <div className="form-group">
              <label>Recipients</label>
              <select value={recipients} onChange={(e) => setRecipients(e.target.value)}>
                <option value="all">All Members ({users.length})</option>
                <option value="admins">Admins Only</option>
                <option value="trainers">Trainers Only</option>
                <option value="members">Members Only</option>
                <option value="selected">Select Specific Users</option>
              </select>
            </div>

            {/* User Selection */}
            {recipients === 'selected' && (
              <div className="form-group">
                <label>Select Users</label>
                <div className="users-list">
                  {users.map(user => (
                    <label key={user.id} className="user-checkbox">
                      <input
                        type="checkbox"
                        checked={selectedUsers.includes(user.email)}
                        onChange={() => toggleUserSelection(user.email)}
                      />
                      <span>{user.name} ({user.email})</span>
                    </label>
                  ))}
                </div>
              </div>
            )}

            {/* Subject (Email Only) */}
            {messageType === 'email' && (
              <div className="form-group">
                <label>Subject</label>
                <input
                  type="text"
                  value={subject}
                  onChange={(e) => setSubject(e.target.value)}
                  placeholder="Enter email subject"
                  required
                />
              </div>
            )}

            {/* Message */}
            <div className="form-group">
              <label>Message</label>
              <textarea
                value={message}
                onChange={(e) => setMessage(e.target.value)}
                placeholder={`Enter ${messageType} message...`}
                rows="6"
                required
              ></textarea>
              <p className="char-count">{message.length} characters</p>
            </div>

            {/* Preview */}
            <div className="message-preview">
              <h4>Preview</h4>
              {messageType === 'email' && subject && (
                <p><strong>Subject:</strong> {subject}</p>
              )}
              <p>{message || 'Message preview will appear here'}</p>
            </div>

            {/* Submit */}
            <button
              type="submit"
              className="btn btn-primary btn-lg"
              disabled={sending || loading}
            >
              {sending ? 'Sending...' : `Send ${messageType.toUpperCase()}`}
            </button>
          </form>
        </div>

        {/* History Section */}
        <div className="communications-history">
          <h2>Communication History</h2>
          {history.length === 0 ? (
            <p>No communications sent yet</p>
          ) : (
            <div className="history-list">
              {history.map(item => (
                <div key={item.id} className="history-item">
                  <div className="history-type">
                    {item.type === 'email' ? '📧' : '📱'}
                  </div>
                  <div className="history-content">
                    <h4>{item.subject || item.message}</h4>
                    <p>Recipients: {item.recipients}</p>
                    <p className="history-date">Sent: {item.sentAt}</p>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

export default Communications
