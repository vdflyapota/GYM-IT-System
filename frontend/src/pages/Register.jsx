
import React, { useState, useRef, useEffect } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import { authAPI } from '../services/api'
import './Auth.css'

function Register() {
  const navigate = useNavigate()
  const [fullName, setFullName] = useState('')
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')
  const [loading, setLoading] = useState(false)
  const [showPassword, setShowPassword] = useState(false)
  const nameRef = useRef(null)

  useEffect(() => {
    if (nameRef.current) nameRef.current.focus()
  }, [])

  const validateEmail = (email) => {
    return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')
    setSuccess('')
    if (!fullName.trim()) {
      setError('Please enter your full name.')
      return
    }
    if (!validateEmail(email)) {
      setError('Please enter a valid email address.')
      return
    }
    if (password.length < 4) {
      setError('Password must be at least 4 characters.')
      return
    }
    setLoading(true)
    try {
      const result = await authAPI.register(email, password, fullName)
      setSuccess('Registration successful! Awaiting admin approval.')
      setFullName('')
      setEmail('')
      setPassword('')
      setTimeout(() => {
        navigate('/login')
      }, 1800)
    } catch (err) {
      setError(err.message || 'Registration failed. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="auth-container">
      <div className="auth-card">
        <h2>Register for HealthGYM</h2>
        {error && <div className="error-message animate-fade" role="alert" aria-live="assertive">{error}</div>}
        {success && <div className="success-message animate-fade" role="status" aria-live="polite">{success}</div>}
        <form onSubmit={handleSubmit} autoComplete="on" aria-label="Registration form">
          <div className="form-group">
            <label htmlFor="register-name">Full Name</label>
            <input
              id="register-name"
              type="text"
              required
              value={fullName}
              onChange={(e) => setFullName(e.target.value)}
              disabled={loading}
              ref={nameRef}
              autoFocus
              autoComplete="name"
              placeholder="Your full name"
              aria-required="true"
              aria-label="Full Name"
            />
          </div>
          <div className="form-group">
            <label htmlFor="register-email">Email</label>
            <input
              id="register-email"
              type="email"
              required
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              disabled={loading}
              autoComplete="username"
              placeholder="you@email.com"
              aria-required="true"
              aria-label="Email"
            />
          </div>
          <div className="form-group" style={{ position: 'relative' }}>
            <label htmlFor="register-password">Password</label>
            <input
              id="register-password"
              type={showPassword ? 'text' : 'password'}
              required
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              disabled={loading}
              autoComplete="new-password"
              placeholder="Create a password"
              minLength={4}
              aria-required="true"
              aria-label="Password"
            />
            <button
              type="button"
              className="show-password-btn"
              aria-label={showPassword ? 'Hide password' : 'Show password'}
              onClick={() => setShowPassword((v) => !v)}
              tabIndex={0}
              style={{
                position: 'absolute',
                right: 10,
                top: 36,
                background: 'none',
                border: 'none',
                cursor: 'pointer',
                color: '#198754',
                fontSize: '1.1rem',
                padding: 0
              }}
            >
              {showPassword ? '🙈' : '👁️'}
            </button>
          </div>
          <button
            type="submit"
            className="btn btn-primary btn-block"
            disabled={loading}
            aria-busy={loading}
            aria-label="Register"
          >
            {loading ? 'Registering...' : 'Register'}
          </button>
        </form>
        <p className="auth-link">
          Already have an account? <Link to="/login">Login</Link>
        </p>
      </div>
    </div>
  )
}

export default Register
