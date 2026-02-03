import React, { useState, useRef, useEffect } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import { authAPI } from '../services/api'
import './Auth.css'

function Login() {
  const navigate = useNavigate()
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)
  const [success, setSuccess] = useState('')
  const [showPassword, setShowPassword] = useState(false)
  const emailRef = useRef(null)

  useEffect(() => {
    if (emailRef.current) emailRef.current.focus()
  }, [])

  const validateEmail = (email) => {
    return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')
    setSuccess('')
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
      const result = await authAPI.login(email, password)
      if (result.access_token) {
        localStorage.setItem('token', result.access_token)
        const userData = {
          id: result.user?.id || email,
          name: result.user?.full_name || email.split('@')[0],
          email: result.user?.email || email,
          role: result.user?.role || 'user',
        }
        localStorage.setItem('user', JSON.stringify(userData))
        setSuccess('Login successful! Redirecting...')
        setTimeout(() => navigate('/dashboard'), 1200)
      }
    } catch (err) {
      setError(err.message || 'Login failed. Please check your credentials and try again.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="auth-container">
      <div className="auth-card">
        <h2>Login to HealthGYM</h2>
        {error && <div className="error-message animate-fade" role="alert" aria-live="assertive">{error}</div>}
        {success && <div className="success-message animate-fade" role="status" aria-live="polite">{success}</div>}
        <form onSubmit={handleSubmit} autoComplete="on" aria-label="Login form">
          <div className="form-group">
            <label htmlFor="login-email">Email</label>
            <input
              id="login-email"
              type="email"
              required
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              disabled={loading}
              ref={emailRef}
              autoFocus
              autoComplete="username"
              placeholder="you@email.com"
              aria-required="true"
              aria-label="Email"
            />
          </div>
          <div className="form-group" style={{ position: 'relative' }}>
            <label htmlFor="login-password">Password</label>
            <input
              id="login-password"
              type={showPassword ? 'text' : 'password'}
              required
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              disabled={loading}
              autoComplete="current-password"
              placeholder="Enter password"
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
            aria-label="Login"
          >
            {loading ? 'Logging in...' : 'Login'}
          </button>
        </form>
        <p className="auth-link">
          Don't have an account? <Link to="/register">Register</Link>
        </p>
      </div>
    </div>
  )
}

export default Login
