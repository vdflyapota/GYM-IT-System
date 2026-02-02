import React, { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { usersAPI, tournamentsAPI } from '../services/api'
import './Dashboard.css'

function Dashboard() {
  const [stats, setStats] = useState({
    rank: '#12',
    points: 1250,
    tournaments: 2
  })
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

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

  useEffect(() => {
    fetchDashboardData()
  }, [])

  const fetchDashboardData = async () => {
    try {
      setLoading(true)
      
      // Try to fetch user data and tournaments
      const userProfile = await usersAPI.getMe();
      const tournaments = await tournamentsAPI.listTournaments();
      
      setStats({
        rank: '#12', // This would need a dedicated endpoint
        points: userProfile?.points || 1250,
        tournaments: tournaments?.length || 2
      })
      setError('')
    } catch (err) {
      console.error('Failed to fetch dashboard data:', err)
      // Keep default mock data as fallback
      setError('')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="dashboard-container">
      <div className="dashboard-stats">
        <div className="stat-card">
          <div className="stat-icon">🏅</div>
          <div className="stat-content">
            <h6 className="stat-label">Your Rank</h6>
            <h3 className="stat-value">{stats.rank}</h3>
          </div>
        </div>
        <div className="stat-card">
          <div className="stat-icon">⭐</div>
          <div className="stat-content">
            <h6 className="stat-label">Points Earned</h6>
            <h3 className="stat-value">{stats.points.toLocaleString()}</h3>
          </div>
        </div>
        <div className="stat-card">
          <div className="stat-icon">🏆</div>
          <div className="stat-content">
            <h6 className="stat-label">Active Tournaments</h6>
            <h3 className="stat-value">{stats.tournaments}</h3>
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
