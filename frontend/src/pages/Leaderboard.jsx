import React, { useState, useEffect } from 'react'
import { tournamentsAPI } from '../services/api'
import './Leaderboard.css'

function Leaderboard() {
  const [leaderboard, setLeaderboard] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [lastUpdated, setLastUpdated] = useState(null)

  const fetchLeaderboard = async () => {
    try {
      setError(null)
      const data = await tournamentsAPI.getLeaderboard()
      setLeaderboard(data || [])
      setLastUpdated(new Date())
    } catch (err) {
      setError('Failed to load leaderboard. Please try again.')
      console.error('Leaderboard fetch error:', err)
      // Use mock data if API fails
      setLeaderboard([
        { rank: 1, name: 'John Athlete', points: 2500, tournaments: 5 },
        { rank: 2, name: 'Sarah Fit', points: 2350, tournaments: 4 },
        { rank: 3, name: 'Mike Strong', points: 2100, tournaments: 5 },
        { rank: 4, name: 'Lisa Power', points: 1950, tournaments: 3 },
        { rank: 5, name: 'Tom Active', points: 1800, tournaments: 4 },
      ])
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchLeaderboard()
    
    // Auto-refresh every 5 seconds for live updates
    const interval = setInterval(fetchLeaderboard, 5000)
    
    return () => clearInterval(interval)
  }, [])

  const getRankBadge = (rank) => {
    if (rank === 1) return '🥇'
    if (rank === 2) return '🥈'
    if (rank === 3) return '🥉'
    return null
  }

  const getRankClass = (rank) => {
    if (rank === 1) return 'rank-gold'
    if (rank === 2) return 'rank-silver'
    if (rank === 3) return 'rank-bronze'
    return ''
  }

  if (loading && leaderboard.length === 0) {
    return (
      <div className="leaderboard-container">
        <div className="loading-state">
          <div className="loading-spinner"></div>
          <p>Loading leaderboard...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="leaderboard-container">
      <div className="leaderboard-header">
        <div>
          <h1 className="leaderboard-title">🥇 Live Leaderboard</h1>
          <p className="leaderboard-subtitle">
            Real-time rankings based on challenge scores
            {lastUpdated && (
              <span className="last-updated">
                {' • Last updated: '}
                {lastUpdated.toLocaleTimeString()}
              </span>
            )}
          </p>
        </div>
        <button 
          className="btn btn-primary refresh-btn"
          onClick={fetchLeaderboard}
          disabled={loading}
        >
          {loading ? '🔄' : '↻'} Refresh
        </button>
      </div>

      {error && (
        <div className="alert alert-error">
          {error}
        </div>
      )}

      <div className="leaderboard-table-container">
        <table className="leaderboard-table">
          <thead>
            <tr>
              <th className="rank-col">Rank</th>
              <th className="name-col">Athlete Name</th>
              <th className="score-col">Total Score</th>
            </tr>
          </thead>
          <tbody>
            {leaderboard.length === 0 ? (
              <tr>
                <td colSpan="3" className="empty-state">
                  No scores yet. Be the first to compete!
                </td>
              </tr>
            ) : (
              leaderboard.map((entry, index) => {
                const rank = index + 1
                const badge = getRankBadge(rank)
                const rankClass = getRankClass(rank)
                
                return (
                  <tr key={entry.user_name} className={rankClass}>
                    <td className="rank-cell">
                      <span className="rank-number">{rank}</span>
                      {badge && <span className="rank-badge">{badge}</span>}
                    </td>
                    <td className="name-cell">
                      <strong>{entry.user_name}</strong>
                    </td>
                    <td className="score-cell">
                      <span className="score-value">
                        {entry.total_score?.toFixed(1) || 0} pts
                      </span>
                    </td>
                  </tr>
                )
              })
            )}
          </tbody>
        </table>
      </div>
    </div>
  )
}

export default Leaderboard
