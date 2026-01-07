import React from 'react'
import './Header.css'

function Header() {
  const userEmail = localStorage.getItem('user') || 'guest@gym.com'
  const userName = userEmail.split('@')[0]

  return (
    <header className="header">
      <div className="header-content">
        <div className="header-greeting">
          <h2 className="header-title">Dashboard</h2>
          <p className="header-subtitle">
            Welcome back, <span className="header-user-name">{userName}</span>
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
