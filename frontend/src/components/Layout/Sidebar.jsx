import React, { useState, useEffect } from 'react'
import { Link, useLocation } from 'react-router-dom'
import './Sidebar.css'

function Sidebar() {
  const location = useLocation()
  const [userRole, setUserRole] = useState('user')
  const [userName, setUserName] = useState('User')

  // Helper function to safely parse user data
  const getUserData = () => {
    try {
      const userStr = localStorage.getItem('user')
      if (!userStr) return { name: 'User', role: 'user' }
      
      // Try to parse as JSON
      const user = JSON.parse(userStr)
      return user
    } catch (e) {
      // If parsing fails, user was stored as plain string (email)
      const userStr = localStorage.getItem('user')
      return { name: 'User', role: 'user', email: userStr }
    }
  }

  useEffect(() => {
    // Get user data safely
    const user = getUserData()
    setUserRole(user.role || 'user')
    setUserName(user.name || user.email?.split('@')[0] || 'User')
  }, [])

  // Define menu items based on user role
  const getMenuItems = () => {
    const baseItems = [
      { path: '/dashboard', icon: '🏠', label: 'Dashboard', roles: ['user', 'trainer', 'admin'] },
      { path: '/class-schedule', icon: '📅', label: 'Class Schedule', roles: ['user', 'trainer', 'admin'] },
      { path: '/tournaments', icon: '🏆', label: 'Tournaments', roles: ['user', 'trainer', 'admin'] },
      { path: '/leaderboard', icon: '📊', label: 'Leaderboard', roles: ['user', 'trainer', 'admin'] },
      { path: '/membership', icon: '💳', label: 'Membership', roles: ['user', 'trainer', 'admin'] },
      { path: '/hiring', icon: '💼', label: 'Hiring', roles: ['user', 'trainer'] }, // Visible to non-admins
    ]

    // Admin-only items
    if (userRole === 'admin') {
      baseItems.push(
        { path: '/admin/reports', icon: '📈', label: 'User Reports', roles: ['admin'] },
        { path: '/admin/kpi', icon: '💹', label: 'KPI Dashboard', roles: ['admin'] },
        { path: '/admin/communications', icon: '📬', label: 'Communications', roles: ['admin'] },
        { path: '/admin/access-logs', icon: '🚪', label: 'Access Logs', roles: ['admin'] },
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
          <p className="user-name">{userName}</p>
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
