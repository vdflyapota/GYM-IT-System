import React from 'react'
import { useNavigate } from 'react-router-dom'
import './Auth.css'

function Register() {
  const navigate = useNavigate()

  const handleSubmit = (e) => {
    e.preventDefault()
    // Simulate registration - in real app, call API
    localStorage.setItem('user', 'user@example.com')
    localStorage.setItem('token', 'mock-token')
    navigate('/dashboard')
  }

  return (
    <div className="auth-container">
      <div className="auth-card">
        <h2>Join HealthGYM</h2>
        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label>Full Name</label>
            <input type="text" required />
          </div>
          <div className="form-group">
            <label>Email</label>
            <input type="email" required />
          </div>
          <div className="form-group">
            <label>Password</label>
            <input type="password" required />
          </div>
          <button type="submit" className="btn btn-primary btn-block">
            Register
          </button>
        </form>
      </div>
    </div>
  )
}

export default Register
