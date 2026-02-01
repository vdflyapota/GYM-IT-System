import React, { useState, useEffect } from 'react'
import './Header.css'

function Header() {
  const [user, setUser] = useState({ name: 'User', role: 'user' })

  useEffect(() => {
    const userData = JSON.parse(localStorage.getItem('user') || '{}')
    setUser({
      name: userData.name || userData.username || 'User',
      role: userData.role || 'user'
    })
  }, [])

  return (
    <header className="header">
      <div className="header-content">
        <div className="header-greeting">
          <h2 className="header-title">Dashboard</h2>
          <p className="header-subtitle">
            Welcome back, <span className="header-user-name">{user.name}</span>
            <span className="header-role-badge" style={{
              background: user.role === 'admin' ? '#ff6b6b' : user.role === 'trainer' ? '#4facfe' : '#667eea'
            }}>
              {user.role.toUpperCase()}
            </span>
          </p>
        </div>
        <div className="header-actions">
          <button className="header-notification-btn" title="Notifications">
            <span className="header-notification-icon">🔔</span>
            <span className="header-notification-badge">3</span>
          </button>
        </div>
      </div>
    </header>
  )
}

export default Header
