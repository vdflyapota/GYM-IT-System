import React from 'react'
import { Link } from 'react-router-dom'
import './Home.css'

function Home() {
  return (
    <div className="home-container">
      <header className="home-hero">
        <h1 className="home-title">Welcome to HealthGYM</h1>
        <p className="home-subtitle">
          Track your progress, join tournaments, and dominate the leaderboard.
        </p>
        <div className="home-actions">
          <Link to="/register" className="btn btn-primary btn-large">
            Start Your Journey
          </Link>
          <Link to="/login" className="btn btn-secondary btn-large">
            Member Login
          </Link>
        </div>
      </header>
    </div>
  )
}

export default Home
