import React, { lazy, Suspense } from 'react'
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import Layout from './components/Layout/Layout'
import Home from './pages/Home'
import LoadingSpinner from './components/UI/LoadingSpinner'
import ErrorBoundary from './components/ErrorBoundary'

// Lazy load pages for performance (Phase 3 requirement)
const Dashboard = lazy(() => import('./pages/Dashboard'))
const Leaderboard = lazy(() => import('./pages/Leaderboard'))
const Tournaments = lazy(() => import('./pages/Tournaments'))
const Login = lazy(() => import('./pages/Login'))
const Register = lazy(() => import('./pages/Register'))
const AdminReports = lazy(() => import('./pages/AdminReports'))
const ClassSchedule = lazy(() => import('./pages/ClassSchedule'))
const Hiring = lazy(() => import('./pages/Hiring'))
const MembershipPortal = lazy(() => import('./pages/MembershipPortal'))
const KPIDashboard = lazy(() => import('./pages/KPIDashboard'))
const Communications = lazy(() => import('./pages/Communications'))
const AccessLogs = lazy(() => import('./pages/AccessLogs'))

function App() {
  return (
    <ErrorBoundary>
      <Router>
        <Suspense fallback={<LoadingSpinner />}>
          <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/login" element={<Login />} />
            <Route path="/register" element={<Register />} />
            <Route path="/class-schedule" element={<ClassSchedule />} />
            <Route path="/hiring" element={<Hiring />} />
            <Route element={<Layout />}>
              <Route path="/dashboard" element={<Dashboard />} />
              <Route path="/leaderboard" element={<Leaderboard />} />
              <Route path="/tournaments" element={<Tournaments />} />
              <Route path="/membership" element={<MembershipPortal />} />
              <Route path="/admin/reports" element={<AdminReports />} />
              <Route path="/admin/kpi" element={<KPIDashboard />} />
              <Route path="/admin/communications" element={<Communications />} />
              <Route path="/admin/access-logs" element={<AccessLogs />} />
            </Route>
          </Routes>
        </Suspense>
      </Router>
    </ErrorBoundary>
  )
}

export default App
