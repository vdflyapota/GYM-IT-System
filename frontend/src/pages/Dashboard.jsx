import React from 'react'
import { Link } from 'react-router-dom'
import './Dashboard.css'

function Dashboard() {
  // Safely get user data
  const getUserData = () => {
    try {
      const userStr = localStorage.getItem('user') || '{}'
      const userData = JSON.parse(userStr)
      return userData
    } catch (e) {
      // If parsing fails, user was stored as plain string (email)
      return { email: localStorage.getItem('user'), name: 'Guest' }
    }
  }
  const user = getUserData()
  const userName = user.name || user.email?.split('@')[0] || 'Guest'

  return (
    <div className="dashboard-container">
      <div className="dashboard-stats">
        <div className="stat-card">
          <div className="stat-icon">🏅</div>
          <div className="stat-content">
            <h6 className="stat-label">Your Rank</h6>
            <h3 className="stat-value">#12</h3>
          </div>
        </div>
        <div className="stat-card">
          <div className="stat-icon">⭐</div>
          <div className="stat-content">
            <h6 className="stat-label">Points Earned</h6>
            <h3 className="stat-value">1,250</h3>
          </div>
        </div>
        <div className="stat-card">
          <div className="stat-icon">🏆</div>
          <div className="stat-content">
            <h6 className="stat-label">Active Tournaments</h6>
            <h3 className="stat-value">2</h3>
          </div>
        </div>
      </div>

      <div className="dashboard-actions">
        <Link to="/leaderboard" className="action-card">
          <span className="action-icon">📊</span>
          <div className="action-content">
            <h4>View Leaderboard</h4>
            <p>See where you rank among all athletes</p>
          </div>
          <span className="action-arrow">→</span>
        </Link>
        <Link to="/tournaments" className="action-card">
          <span className="action-icon">🏆</span>
          <div className="action-content">
            <h4>Join Tournament</h4>
            <p>Compete in upcoming tournaments</p>
          </div>
          <span className="action-arrow">→</span>
        </Link>
      </div>
    </div>
  )
}

export default Dashboard
