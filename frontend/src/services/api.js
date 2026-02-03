/**
 * API Service - Handles all HTTP requests to backend microservices
 * Base URL should be the API Gateway
 */

const API_BASE_URL = 'http://localhost:8000/api'

// Helper function to get auth token from localStorage
const getAuthToken = () => {
  return localStorage.getItem('token')
}

// Helper function to make API requests
const apiCall = async (endpoint, options = {}) => {
  const url = `${API_BASE_URL}${endpoint}`
  const headers = {
    'Content-Type': 'application/json',
    ...options.headers,
  }

  // Add auth token if available
  const token = getAuthToken()
  if (token) {
    headers['Authorization'] = `Bearer ${token}`
  }

  try {
    const response = await fetch(url, {
      ...options,
      headers,
    })

    // Handle non-JSON responses
    const contentType = response.headers.get('content-type')
    let data = null
    
    if (contentType && contentType.includes('application/json')) {
      data = await response.json()
    } else {
      data = await response.text()
    }

    if (!response.ok) {
      throw {
        status: response.status,
        message: data?.detail || data?.message || 'Unknown error',
        data,
      }
    }

    return { success: true, data }
  } catch (error) {
    console.error('API Error:', error)
    throw error
  }
}

/**
 * Authentication API
 */
export const authAPI = {
  // Register a new user
  register: async (email, password, fullName) => {
    try {
      const response = await apiCall('/auth/register', {
        method: 'POST',
        body: JSON.stringify({
          email: email.toLowerCase().trim(),
          password,
          full_name: fullName.trim(),
          role: 'member',
        }),
      })
      return response.data
    } catch (error) {
      throw error
    }
  },

  // Login user
  login: async (email, password) => {
    try {
      const response = await apiCall('/auth/login', {
        method: 'POST',
        body: JSON.stringify({
          email: email.toLowerCase().trim(),
          password,
        }),
      })
      
      const result = response.data
      
      // Store token and user info in localStorage
      if (result.access_token) {
        localStorage.setItem('token', result.access_token)
      }
      
      if (result.user) {
        localStorage.setItem('user', JSON.stringify(result.user))
      }
      
      return result
    } catch (error) {
      throw error
    }
  },

  // Logout user
  logout: () => {
    localStorage.removeItem('token')
    localStorage.removeItem('user')
  },

  // Create admin user
  createAdmin: async (email, password, fullName) => {
    try {
      const response = await apiCall('/auth/create_admin', {
        method: 'POST',
        body: JSON.stringify({
          email: email.toLowerCase().trim(),
          password,
          full_name: fullName.trim(),
        }),
      })
      return response.data
    } catch (error) {
      throw error
    }
  },
}

/**
 * Users API
 */
export const usersAPI = {
  // Get current user profile
  getMe: async () => {
    try {
      const response = await apiCall('/users/me', {
        method: 'GET',
      })
      return response.data
    } catch (error) {
      throw error
    }
  },

  // Get all users (admin/trainer only)
  listUsers: async () => {
    try {
      const response = await apiCall('/users/', {
        method: 'GET',
      })
      return response.data
    } catch (error) {
      throw error
    }
  },

  // Get user by ID
  getUserById: async (userId) => {
    try {
      const response = await apiCall(`/users/${userId}`, {
        method: 'GET',
      })
      return response.data
    } catch (error) {
      throw error
    }
  },

  // Update user profile
  updateProfile: async (userId, updates) => {
    try {
      const response = await apiCall(`/users/${userId}`, {
        method: 'PUT',
        body: JSON.stringify(updates),
      })
      return response.data
    } catch (error) {
      throw error
    }
  },
}

/**
 * Tournaments API
 */
export const tournamentsAPI = {
  // Get all tournaments
  listTournaments: async () => {
    try {
      const response = await apiCall('/tournaments/', {
        method: 'GET',
      })
      return response.data
    } catch (error) {
      throw error
    }
  },

  // Get tournament by ID
  getTournament: async (tournamentId) => {
    try {
      const response = await apiCall(`/tournaments/${tournamentId}`, {
        method: 'GET',
      })
      return response.data
    } catch (error) {
      throw error
    }
  },

  // Create tournament (admin only)
  createTournament: async (tournamentData) => {
    try {
      const response = await apiCall('/tournaments/', {
        method: 'POST',
        body: JSON.stringify(tournamentData),
      })
      return response.data
    } catch (error) {
      throw error
    }
  },

  // Join tournament
  joinTournament: async (tournamentId) => {
    try {
      // Get user name from localStorage
      const userStr = localStorage.getItem('user') || '{}'
      const userData = JSON.parse(userStr)
      const participantName = userData.name || userData.email?.split('@')[0] || 'Participant'
      
      const response = await apiCall(`/tournaments/${tournamentId}/participants`, {
        method: 'POST',
        body: JSON.stringify({
          name: participantName,
        }),
      })
      return response.data
    } catch (error) {
      throw error
    }
  },

  // Get leaderboard
  getLeaderboard: async () => {
    try {
      const response = await apiCall('/tournaments/leaderboard', {
        method: 'GET',
      })
      return response.data
    } catch (error) {
      throw error
    }
  },
}

/**
 * Notifications API
 */
export const notificationsAPI = {
  // Get all notifications for current user
  getNotifications: async () => {
    try {
      const response = await apiCall('/notifications/', {
        method: 'GET',
      })
      return response.data
    } catch (error) {
      throw error
    }
  },

  // Mark notification as read
  markAsRead: async (notificationId) => {
    try {
      const response = await apiCall(`/notifications/${notificationId}/read`, {
        method: 'PUT',
      })
      return response.data
    } catch (error) {
      throw error
    }
  },
}

/**
 * Classes/Schedule API
 */
export const classesAPI = {
  // Get all classes
  listClasses: async () => {
    try {
      const response = await apiCall('/classes/', {
        method: 'GET',
      })
      return response.data
    } catch (error) {
      throw error
    }
  },

  // Get class schedule
  getSchedule: async () => {
    try {
      const response = await apiCall('/classes/schedule', {
        method: 'GET',
      })
      return response.data
    } catch (error) {
      throw error
    }
  },

  // Register for a class
  registerForClass: async (classId) => {
    try {
      const response = await apiCall(`/classes/${classId}/register`, {
        method: 'POST',
      })
      return response.data
    } catch (error) {
      throw error
    }
  },
}

// Applications API
export const applicationsAPI = {
  // Submit job application
  submitApplication: async (formData) => {
    try {
      const response = await apiCall('/applications/submit', {
        method: 'POST',
        body: JSON.stringify(formData),
      })
      return response.data
    } catch (error) {
      throw error
    }
  },

  // List applications (admin only)
  listApplications: async () => {
    try {
      const response = await apiCall('/applications/', {
        method: 'GET',
      })
      return response.data
    } catch (error) {
      throw error
    }
  },

  // Get single application
  getApplication: async (appId) => {
    try {
      const response = await apiCall(`/applications/${appId}`, {
        method: 'GET',
      })
      return response.data
    } catch (error) {
      throw error
    }
  },

  // Update application status
  updateApplicationStatus: async (appId, status) => {
    try {
      const response = await apiCall(`/applications/${appId}`, {
        method: 'PUT',
        body: JSON.stringify({ status }),
      })
      return response.data
    } catch (error) {
      throw error
    }
  },
}

// Membership API
export const membershipAPI = {
  // Get user membership details
  getMembershipDetails: async () => {
    try {
      const response = await apiCall('/membership/details', {
        method: 'GET',
      })
      return response.data
    } catch (error) {
      throw error
    }
  },

  // Freeze membership
  freezeMembership: async (reason, duration) => {
    try {
      const response = await apiCall('/membership/freeze', {
        method: 'POST',
        body: JSON.stringify({ reason, duration }),
      })
      return response.data
    } catch (error) {
      throw error
    }
  },

  // Upgrade membership plan
  upgradeMembership: async (newPlan) => {
    try {
      const response = await apiCall('/membership/upgrade', {
        method: 'POST',
        body: JSON.stringify({ plan: newPlan }),
      })
      return response.data
    } catch (error) {
      throw error
    }
  },

  // Book a class
  bookClass: async (classId) => {
    try {
      const response = await apiCall(`/membership/bookings/${classId}`, {
        method: 'POST',
      })
      return response.data
    } catch (error) {
      throw error
    }
  },

  // Get user bookings
  getMyBookings: async () => {
    try {
      const response = await apiCall('/membership/bookings', {
        method: 'GET',
      })
      return response.data
    } catch (error) {
      throw error
    }
  },

  // Cancel booking
  cancelBooking: async (bookingId) => {
    try {
      const response = await apiCall(`/membership/bookings/${bookingId}`, {
        method: 'DELETE',
      })
      return response.data
    } catch (error) {
      throw error
    }
  },
}

// Admin Analytics API
export const analyticsAPI = {
  // Get KPI dashboard data
  getKPIDashboard: async () => {
    try {
      const response = await apiCall('/analytics/kpi', {
        method: 'GET',
      })
      return response.data
    } catch (error) {
      throw error
    }
  },

  // Get access logs
  getAccessLogs: async (limit = 100) => {
    try {
      const response = await apiCall(`/analytics/access-logs?limit=${limit}`, {
        method: 'GET',
      })
      return response.data
    } catch (error) {
      throw error
    }
  },

  // Get user statistics
  getUserStatistics: async () => {
    try {
      const response = await apiCall('/analytics/users', {
        method: 'GET',
      })
      return response.data
    } catch (error) {
      throw error
    }
  },

  // Get revenue analytics
  getRevenue: async (period = 'monthly') => {
    try {
      const response = await apiCall(`/analytics/revenue?period=${period}`, {
        method: 'GET',
      })
      return response.data
    } catch (error) {
      throw error
    }
  },
}

// Communication API
export const communicationAPI = {
  // Send bulk email
  sendBulkEmail: async (recipients, subject, message) => {
    try {
      const response = await apiCall('/communications/email/bulk', {
        method: 'POST',
        body: JSON.stringify({ recipients, subject, message }),
      })
      return response.data
    } catch (error) {
      throw error
    }
  },

  // Send bulk SMS
  sendBulkSMS: async (recipients, message) => {
    try {
      const response = await apiCall('/communications/sms/bulk', {
        method: 'POST',
        body: JSON.stringify({ recipients, message }),
      })
      return response.data
    } catch (error) {
      throw error
    }
  },

  // Get communication history
  getCommunicationHistory: async () => {
    try {
      const response = await apiCall('/communications/history', {
        method: 'GET',
      })
      return response.data
    } catch (error) {
      throw error
    }
  },
}

export default {
  authAPI,
  usersAPI,
  tournamentsAPI,
  notificationsAPI,
  classesAPI,
  applicationsAPI,
  membershipAPI,
  analyticsAPI,
  communicationAPI,
}
