import React from 'react'
import { Link, useLocation } from 'react-router-dom'
import './Sidebar.css'

function Sidebar() {
  const location = useLocation()

  const menuItems = [
    { path: '/dashboard', icon: '🏠', label: 'Overview' },
    { path: '/tournaments', icon: '🏆', label: 'Tournaments' },
    { path: '/leaderboard', icon: '📊', label: 'Leaderboard' },
  ]

  return (
    <aside className="sidebar">
      <div className="sidebar-header">
        <div className="sidebar-logo">
          <span className="sidebar-logo-icon">💪</span>
          <h5 className="sidebar-logo-text">HealthGYM</h5>
        </div>
      </div>
      <nav className="sidebar-nav">
        {menuItems.map((item) => (
          <Link
            key={item.path}
            to={item.path}
            className={`sidebar-link ${location.pathname === item.path ? 'active' : ''}`}
          >
            <span className="sidebar-link-icon">{item.icon}</span>
            <span className="sidebar-link-label">{item.label}</span>
          </Link>
        ))}
        <button className="sidebar-link sidebar-link-logout" onClick={() => {
          localStorage.removeItem('user')
          localStorage.removeItem('token')
          window.location.href = '/login'
        }}>
          <span className="sidebar-link-icon">🚪</span>
          <span className="sidebar-link-label">Logout</span>
        </button>
      </nav>
    </aside>
  )
}

export default Sidebar
