import React from 'react'
import { useNavigate } from 'react-router-dom'
import './Auth.css'

function Login() {
  const navigate = useNavigate()

  const handleSubmit = (e) => {
    e.preventDefault()
    // Simulate login - in real app, call API
    localStorage.setItem('user', 'user@example.com')
    localStorage.setItem('token', 'mock-token')
    navigate('/dashboard')
  }

  return (
    <div className="auth-container">
      <div className="auth-card">
        <h2>Login</h2>
        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label>Email</label>
            <input type="email" required />
          </div>
          <div className="form-group">
            <label>Password</label>
            <input type="password" required />
          </div>
          <button type="submit" className="btn btn-primary btn-block">
            Login
          </button>
        </form>
      </div>
    </div>
  )
}

export default Login
