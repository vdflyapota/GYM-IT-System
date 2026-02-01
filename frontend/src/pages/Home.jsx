import React, { useState, useEffect } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import './Home.css'

function Home() {
  const navigate = useNavigate()

  useEffect(() => {
    // Check if user is logged in
    const token = localStorage.getItem('token')
    if (token) {
      // Redirect to dashboard
      navigate('/dashboard', { replace: true })
    }
  }, [navigate])

  return (
    <div className="home-container">
      <header className="home-hero">
        <h1 className="home-title">Welcome to HealthGYM 💪</h1>
        <p className="home-subtitle">
          Track your progress, join tournaments, and dominate the leaderboard.
        </p>
        <div className="home-actions">
          <Link to="/register" className="btn btn-primary btn-large">
            🚀 Start Your Journey
          </Link>
          <Link to="/login" className="btn btn-secondary btn-large">
            🔑 Member Login
          </Link>
          <Link to="/class-schedule" className="btn btn-outline btn-large">
            📅 View Class Schedule
          </Link>
          <Link to="/hiring" className="btn btn-outline btn-large">
            💼 Join Our Team
          </Link>
        </div>
      </header>
    </div>
  )
}

export default Home