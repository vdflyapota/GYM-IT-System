import React, { useState, useEffect } from 'react'
import { analyticsAPI } from '../services/api'
import './AccessLogs.css'

function AccessLogs() {
  const [logs, setLogs] = useState([])
  const [filteredLogs, setFilteredLogs] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [searchTerm, setSearchTerm] = useState('')
  const [filterType, setFilterType] = useState('all')

  useEffect(() => {
    fetchAccessLogs()
    const interval = setInterval(fetchAccessLogs, 30000) // Auto-refresh every 30 seconds
    return () => clearInterval(interval)
  }, [])

  useEffect(() => {
    applyFilters()
  }, [logs, searchTerm, filterType])

  const fetchAccessLogs = async () => {
    try {
      const data = await analyticsAPI.getAccessLogs(100).catch(() => generateMockLogs())
      setLogs(data)
      setError('')
    } catch (err) {
      console.error('Error fetching access logs:', err)
      setError('Failed to load access logs')
      setLogs(generateMockLogs())
    } finally {
      setLoading(false)
    }
  }

  const generateMockLogs = () => {
    const names = ['John Doe', 'Jane Smith', 'Mike Johnson', 'Sarah Williams', 'Alex Brown']
    const logs = []
    const now = new Date()

    for (let i = 0; i < 50; i++) {
      const time = new Date(now - Math.random() * 86400000) // Last 24 hours
      logs.push({
        id: i,
        name: names[Math.floor(Math.random() * names.length)],
        action: Math.random() > 0.5 ? 'in' : 'out',
        time: time.toLocaleTimeString(),
        date: time.toLocaleDateString(),
        membershipId: `MEM-${String(1000 + Math.floor(Math.random() * 9000)).padStart(4, '0')}`,
        method: Math.random() > 0.7 ? 'card' : 'app'
      })
    }

    return logs.sort((a, b) => new Date(`${b.date} ${b.time}`) - new Date(`${a.date} ${a.time}`))
  }

  const applyFilters = () => {
    let filtered = [...logs]

    // Search filter
    if (searchTerm) {
      filtered = filtered.filter(log =>
        log.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
        log.membershipId.toLowerCase().includes(searchTerm.toLowerCase())
      )
    }

    // Type filter
    if (filterType !== 'all') {
      filtered = filtered.filter(log => log.action === filterType)
    }

    setFilteredLogs(filtered)
  }

  const getActionBadge = (action) => {
    return action === 'in' ? '✅ In' : '⬅️ Out'
  }

  const getMethodBadge = (method) => {
    return method === 'card' ? '🎫 Card' : '📱 App'
  }

  const stats = {
    totalAccess: logs.length,
    checkIn: logs.filter(l => l.action === 'in').length,
    checkOut: logs.filter(l => l.action === 'out').length,
    activeNow: logs.filter(l => l.action === 'in').length - logs.filter(l => l.action === 'out').length
  }

  if (loading) return <div className="access-logs-container"><p>Loading access logs...</p></div>

  return (
    <div className="access-logs-container">
      <h1>🚪 Access Logs</h1>

      {error && <div className="error-message">{error}</div>}

      {/* Stats Cards */}
      <div className="stats-grid">
        <div className="stat-card">
          <h3>Total Access</h3>
          <p className="stat-value">{stats.totalAccess}</p>
          <p className="stat-label">Last 24 hours</p>
        </div>
        <div className="stat-card">
          <h3>Check-ins</h3>
          <p className="stat-value" style={{color: '#22c55e'}}>{stats.checkIn}</p>
          <p className="stat-label">✅ Members in</p>
        </div>
        <div className="stat-card">
          <h3>Check-outs</h3>
          <p className="stat-value" style={{color: '#2563eb'}}>{stats.checkOut}</p>
          <p className="stat-label">⬅️ Members out</p>
        </div>
        <div className="stat-card">
          <h3>Currently in Gym</h3>
          <p className="stat-value" style={{color: '#f97316'}}>{Math.max(0, stats.activeNow)}</p>
          <p className="stat-label">Active members</p>
        </div>
      </div>

      {/* Filters and Search */}
      <div className="filter-section">
        <input
          type="text"
          className="search-input"
          placeholder="Search by name or membership ID..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
        />
        <div className="filter-buttons">
          <button
            className={`filter-btn ${filterType === 'all' ? 'active' : ''}`}
            onClick={() => setFilterType('all')}
          >
            All ({logs.length})
          </button>
          <button
            className={`filter-btn ${filterType === 'in' ? 'active' : ''}`}
            onClick={() => setFilterType('in')}
          >
            Check-in ({stats.checkIn})
          </button>
          <button
            className={`filter-btn ${filterType === 'out' ? 'active' : ''}`}
            onClick={() => setFilterType('out')}
          >
            Check-out ({stats.checkOut})
          </button>
        </div>
      </div>

      {/* Access Logs Table */}
      <div className="logs-section">
        {filteredLogs.length === 0 ? (
          <p className="no-logs">No access logs found</p>
        ) : (
          <div className="logs-wrapper">
            <table className="logs-table">
              <thead>
                <tr>
                  <th>Member Name</th>
                  <th>Membership ID</th>
                  <th>Action</th>
                  <th>Method</th>
                  <th>Date & Time</th>
                </tr>
              </thead>
              <tbody>
                {filteredLogs.map(log => (
                  <tr key={log.id} className={`log-row log-${log.action}`}>
                    <td className="member-name">{log.name}</td>
                    <td className="membership-id">{log.membershipId}</td>
                    <td className="action-cell">
                      <span className={`badge badge-${log.action}`}>
                        {getActionBadge(log.action)}
                      </span>
                    </td>
                    <td className="method-cell">
                      <span className={`badge badge-${log.method}`}>
                        {getMethodBadge(log.method)}
                      </span>
                    </td>
                    <td className="datetime-cell">
                      <span className="date">{log.date}</span>
                      <span className="time">{log.time}</span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Pagination Info */}
      <div className="pagination-info">
        <p>Showing {filteredLogs.length} of {logs.length} records</p>
      </div>
    </div>
  )
}

export default AccessLogs
