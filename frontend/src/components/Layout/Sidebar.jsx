import React, { useState, useEffect } from 'react'
import { Link, useLocation } from 'react-router-dom'
import './Sidebar.css'

function Sidebar() {
  const location = useLocation()
  const [userRole, setUserRole] = useState('user')

  useEffect(() => {
    // Get user role from localStorage or auth context
    const user = JSON.parse(localStorage.getItem('user') || '{}')
    setUserRole(user.role || 'user')
  }, [])

  // Define menu items based on user role
  const getMenuItems = () => {
    const baseItems = [
      { path: '/dashboard', icon: '🏠', label: 'Dashboard', roles: ['user', 'trainer', 'admin'] },
      { path: '/class-schedule', icon: '📅', label: 'Class Schedule', roles: ['user', 'trainer', 'admin'] },
      { path: '/tournaments', icon: '🏆', label: 'Tournaments', roles: ['user', 'trainer', 'admin'] },
      { path: '/leaderboard', icon: '📊', label: 'Leaderboard', roles: ['user', 'trainer', 'admin'] },
      { path: '/hiring', icon: '💼', label: 'Hiring', roles: ['user', 'trainer'] }, // Visible to non-admins
    ]

    // Admin-only items
    if (userRole === 'admin') {
      baseItems.push(
        { path: '/admin/reports', icon: '📈', label: 'User Reports', roles: ['admin'] },
      )
    }

    // Filter items based on current user role
    return baseItems.filter(item => item.roles.includes(userRole))
  }

  const menuItems = getMenuItems()

  return (
    <aside className="sidebar">
      <div className="sidebar-header">
        <div className="sidebar-logo">
          <span className="sidebar-logo-icon">💪</span>
          <h5 className="sidebar-logo-text">HealthGYM</h5>
        </div>
      </div>

      {/* User Info */}
      <div className="sidebar-user-info">
        <div className="user-badge">{userRole === 'admin' ? '👑' : userRole === 'trainer' ? '🏋️' : '👤'}</div>
        <div className="user-details">
          <p className="user-name">{JSON.parse(localStorage.getItem('user') || '{}').name || 'User'}</p>
          <p className="user-role" style={{
            color: userRole === 'admin' ? '#ff6b6b' : userRole === 'trainer' ? '#4facfe' : '#667eea'
          }}>
            {userRole.toUpperCase()}
          </p>
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

        <hr className="sidebar-divider" />

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
