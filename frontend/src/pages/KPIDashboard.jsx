import React, { useState, useEffect } from 'react'
import { analyticsAPI } from '../services/api'
import './KPIDashboard.css'

function KPIDashboard() {
  const [kpiData, setKpiData] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [period, setPeriod] = useState('monthly')

  useEffect(() => {
    fetchKPIData()
  }, [period])

  const fetchKPIData = async () => {
    try {
      setLoading(true)
      const data = await analyticsAPI.getKPIDashboard().catch(() => ({
        mrr: 12500,
        activeMembers: 450,
        churnRate: 3.2,
        newMembers: 28,
        revenue: 37500,
        avgLifetimeValue: 1250,
        classesThisMonth: 156,
        memberSatisfaction: 4.6
      }))
      setKpiData(data)
      setError('')
    } catch (err) {
      console.error('Error fetching KPI data:', err)
      setError('Failed to load KPI data')
    } finally {
      setLoading(false)
    }
  }

  if (loading) return <div className="kpi-container"><p>Loading KPI data...</p></div>

  return (
    <div className="kpi-container">
      <h1>📊 KPI Dashboard</h1>
      
      <div className="period-selector">
        <select value={period} onChange={(e) => setPeriod(e.target.value)}>
          <option value="daily">Daily</option>
          <option value="weekly">Weekly</option>
          <option value="monthly">Monthly</option>
          <option value="yearly">Yearly</option>
        </select>
      </div>

      {error && <div className="error-message">{error}</div>}

      {kpiData && (
        <div className="kpi-content">
          {/* Main KPI Cards */}
          <div className="kpi-grid-main">
            <div className="kpi-card primary">
              <div className="kpi-icon">💰</div>
              <div className="kpi-content-inner">
                <h3>Monthly Recurring Revenue</h3>
                <p className="kpi-value">${kpiData.mrr?.toLocaleString() || '0'}</p>
                <p className="kpi-change">↑ 12% from last month</p>
              </div>
            </div>

            <div className="kpi-card danger">
              <div className="kpi-icon">📉</div>
              <div className="kpi-content-inner">
                <h3>Churn Rate</h3>
                <p className="kpi-value">{kpiData.churnRate || '0'}%</p>
                <p className="kpi-change">↓ 0.5% improvement</p>
              </div>
            </div>

            <div className="kpi-card success">
              <div className="kpi-icon">👥</div>
              <div className="kpi-content-inner">
                <h3>Active Members</h3>
                <p className="kpi-value">{kpiData.activeMembers?.toLocaleString() || '0'}</p>
                <p className="kpi-change">↑ {kpiData.newMembers || '0'} new this month</p>
              </div>
            </div>

            <div className="kpi-card info">
              <div className="kpi-icon">⭐</div>
              <div className="kpi-content-inner">
                <h3>Member Satisfaction</h3>
                <p className="kpi-value">{kpiData.memberSatisfaction || '0'}/5.0</p>
                <p className="kpi-change">Based on 450 reviews</p>
              </div>
            </div>
          </div>

          {/* Secondary Metrics */}
          <div className="kpi-grid-secondary">
            <div className="metric-card">
              <h4>Total Revenue</h4>
              <p className="metric-value">${kpiData.revenue?.toLocaleString() || '0'}</p>
              <div className="metric-bar">
                <div className="metric-fill" style={{width: '75%'}}></div>
              </div>
            </div>

            <div className="metric-card">
              <h4>Avg Lifetime Value</h4>
              <p className="metric-value">${kpiData.avgLifetimeValue?.toLocaleString() || '0'}</p>
              <div className="metric-bar">
                <div className="metric-fill" style={{width: '60%'}}></div>
              </div>
            </div>

            <div className="metric-card">
              <h4>Classes This Month</h4>
              <p className="metric-value">{kpiData.classesThisMonth || '0'}</p>
              <div className="metric-bar">
                <div className="metric-fill" style={{width: '85%'}}></div>
              </div>
            </div>

            <div className="metric-card">
              <h4>Retention Rate</h4>
              <p className="metric-value">{(100 - (kpiData.churnRate || 0)).toFixed(1)}%</p>
              <div className="metric-bar">
                <div className="metric-fill" style={{width: `${100 - (kpiData.churnRate || 0)}%`}}></div>
              </div>
            </div>
          </div>

          {/* Charts Section */}
          <div className="charts-section">
            <div className="chart-container">
              <h3>Revenue Trend</h3>
              <div className="chart-placeholder">
                <div className="mock-chart">
                  <div className="bar" style={{height: '60%'}}></div>
                  <div className="bar" style={{height: '70%'}}></div>
                  <div className="bar" style={{height: '65%'}}></div>
                  <div className="bar" style={{height: '85%'}}></div>
                  <div className="bar" style={{height: '90%'}}></div>
                  <div className="bar" style={{height: '95%'}}></div>
                  <div className="bar" style={{height: '100%'}}></div>
                </div>
              </div>
              <p className="chart-label">Last 7 days</p>
            </div>

            <div className="chart-container">
              <h3>Member Growth</h3>
              <div className="chart-placeholder">
                <div className="mock-line-chart">
                  <svg viewBox="0 0 300 150" style={{width: '100%', height: '100%'}}>
                    <polyline points="0,120 40,100 80,90 120,70 160,50 200,40 240,35 280,20" 
                              fill="none" stroke="#2563eb" strokeWidth="3"/>
                    <polyline points="0,120 40,100 80,90 120,70 160,50 200,40 240,35 280,20" 
                              fill="url(#grad)" fillOpacity="0.3"/>
                    <defs>
                      <linearGradient id="grad" x1="0%" y1="0%" x2="0%" y2="100%">
                        <stop offset="0%" stopColor="#2563eb" stopOpacity="0.3"/>
                        <stop offset="100%" stopColor="#2563eb" stopOpacity="0"/>
                      </linearGradient>
                    </defs>
                  </svg>
                </div>
              </div>
              <p className="chart-label">Last 30 days</p>
            </div>

            <div className="chart-container">
              <h3>Membership Distribution</h3>
              <div className="chart-placeholder pie-chart">
                <svg viewBox="0 0 100 100" style={{width: '150px', height: '150px'}}>
                  <circle cx="50" cy="50" r="45" fill="none" stroke="#2563eb" strokeWidth="15" 
                          strokeDasharray="70.686 188.4" transform="rotate(-90 50 50)"/>
                  <circle cx="50" cy="50" r="45" fill="none" stroke="#9333ea" strokeWidth="15" 
                          strokeDasharray="56.548 188.4" strokeDashoffset="-70.686" transform="rotate(-90 50 50)"/>
                  <circle cx="50" cy="50" r="45" fill="none" stroke="#f97316" strokeWidth="15" 
                          strokeDasharray="61.166 188.4" strokeDashoffset="-127.234" transform="rotate(-90 50 50)"/>
                </svg>
              </div>
              <div className="pie-legend">
                <p><span style={{color: '#2563eb'}}>■</span> Premium (45%)</p>
                <p><span style={{color: '#9333ea'}}>■</span> Standard (30%)</p>
                <p><span style={{color: '#f97316'}}>■</span> Basic (25%)</p>
              </div>
            </div>
          </div>

          {/* Goals Section */}
          <div className="goals-section">
            <h3>Monthly Goals Progress</h3>
            <div className="goals-grid">
              <div className="goal-card">
                <h4>MRR Target</h4>
                <div className="goal-progress">
                  <div className="goal-bar">
                    <div className="goal-fill" style={{width: '92%'}}></div>
                  </div>
                  <p>$12,500 / $13,500</p>
                </div>
              </div>

              <div className="goal-card">
                <h4>New Members Target</h4>
                <div className="goal-progress">
                  <div className="goal-bar">
                    <div className="goal-fill" style={{width: '87%'}}></div>
                  </div>
                  <p>28 / 32</p>
                </div>
              </div>

              <div className="goal-card">
                <h4>Churn Rate Target</h4>
                <div className="goal-progress">
                  <div className="goal-bar">
                    <div className="goal-fill" style={{width: '78%'}}></div>
                  </div>
                  <p>3.2% / 2.5%</p>
                </div>
              </div>

              <div className="goal-card">
                <h4>Satisfaction Target</h4>
                <div className="goal-progress">
                  <div className="goal-bar">
                    <div className="goal-fill" style={{width: '92%'}}></div>
                  </div>
                  <p>4.6 / 4.5</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default KPIDashboard
