import React, { useState, useEffect } from 'react'
import { membershipAPI, classesAPI } from '../services/api'
import './MembershipPortal.css'

function MembershipPortal() {
  const [membership, setMembership] = useState(null)
  const [bookings, setBookings] = useState([])
  const [classes, setClasses] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [activeTab, setActiveTab] = useState('overview')
  const [showFreezeModal, setShowFreezeModal] = useState(false)
  const [freezeReason, setFreezeReason] = useState('')
  const [freezeDuration, setFreezeDuration] = useState('1')

  useEffect(() => {
    fetchMembershipData()
  }, [])

  const fetchMembershipData = async () => {
    try {
      setLoading(true)
      const [membershipData, bookingsData, classesData] = await Promise.all([
        membershipAPI.getMembershipDetails().catch(() => ({
          plan: 'Premium',
          status: 'Active',
          nextBillingDate: '2025-03-02',
          joinedDate: '2024-01-15',
          monthlyPrice: 49.99
        })),
        membershipAPI.getMyBookings().catch(() => [
          { id: 1, className: 'Yoga', time: '10:00 AM', date: '2025-02-05', trainer: 'Sarah' },
          { id: 2, className: 'HIIT', time: '6:00 PM', date: '2025-02-06', trainer: 'Mike' }
        ]),
        classesAPI.getSchedule().catch(() => [
          { id: 1, name: 'Yoga', time: '10:00 AM', trainer: 'Sarah', capacity: 20, booked: 15 },
          { id: 2, name: 'HIIT', time: '6:00 PM', trainer: 'Mike', capacity: 15, booked: 14 }
        ])
      ])
      
      setMembership(membershipData)
      setBookings(bookingsData)
      setClasses(classesData)
      setError('')
    } catch (err) {
      console.error('Error fetching membership data:', err)
      setError('Failed to load membership data')
    } finally {
      setLoading(false)
    }
  }

  const handleFreezeMembership = async () => {
    try {
      await membershipAPI.freezeMembership(freezeReason, freezeDuration)
      alert('Membership frozen successfully')
      setShowFreezeModal(false)
      setFreezeReason('')
      fetchMembershipData()
    } catch (err) {
      alert('Failed to freeze membership: ' + err.message)
    }
  }

  const handleUpgradeMembership = async (newPlan) => {
    try {
      await membershipAPI.upgradeMembership(newPlan)
      alert('Membership upgraded successfully')
      fetchMembershipData()
    } catch (err) {
      alert('Failed to upgrade membership: ' + err.message)
    }
  }

  const handleBookClass = async (classId) => {
    try {
      await membershipAPI.bookClass(classId)
      alert('Class booked successfully')
      fetchMembershipData()
    } catch (err) {
      alert('Failed to book class: ' + err.message)
    }
  }

  const handleCancelBooking = async (bookingId) => {
    try {
      await membershipAPI.cancelBooking(bookingId)
      alert('Booking cancelled')
      fetchMembershipData()
    } catch (err) {
      alert('Failed to cancel booking: ' + err.message)
    }
  }

  if (loading) return <div className="membership-container"><p>Loading...</p></div>

  return (
    <div className="membership-container">
      <h1>💳 Membership Management</h1>

      <div className="membership-tabs">
        <button 
          className={`tab-btn ${activeTab === 'overview' ? 'active' : ''}`}
          onClick={() => setActiveTab('overview')}
        >
          Overview
        </button>
        <button 
          className={`tab-btn ${activeTab === 'booking' ? 'active' : ''}`}
          onClick={() => setActiveTab('booking')}
        >
          Book Classes
        </button>
        <button 
          className={`tab-btn ${activeTab === 'bookings' ? 'active' : ''}`}
          onClick={() => setActiveTab('bookings')}
        >
          My Bookings
        </button>
      </div>

      {error && <div className="error-message">{error}</div>}

      {activeTab === 'overview' && membership && (
        <div className="membership-overview">
          <div className="membership-card">
            <h2>{membership.plan} Plan</h2>
            <p><strong>Status:</strong> {membership.status}</p>
            <p><strong>Monthly Price:</strong> ${membership.monthlyPrice}</p>
            <p><strong>Member Since:</strong> {membership.joinedDate}</p>
            <p><strong>Next Billing:</strong> {membership.nextBillingDate}</p>

            <div className="membership-actions">
              <button 
                className="btn btn-primary"
                onClick={() => handleUpgradeMembership('Premium Plus')}
              >
                Upgrade Plan
              </button>
              <button 
                className="btn btn-secondary"
                onClick={() => setShowFreezeModal(true)}
              >
                Freeze Membership
              </button>
            </div>
          </div>

          {showFreezeModal && (
            <div className="modal-overlay">
              <div className="modal">
                <h3>Freeze Membership</h3>
                <p>Pause your membership for vacation or injury recovery</p>
                
                <div className="form-group">
                  <label>Reason:</label>
                  <select value={freezeReason} onChange={(e) => setFreezeReason(e.target.value)}>
                    <option value="">Select reason</option>
                    <option value="vacation">Vacation</option>
                    <option value="injury">Injury Recovery</option>
                    <option value="work">Work/Travel</option>
                    <option value="other">Other</option>
                  </select>
                </div>

                <div className="form-group">
                  <label>Duration (months):</label>
                  <input 
                    type="number" 
                    min="1" 
                    max="12" 
                    value={freezeDuration}
                    onChange={(e) => setFreezeDuration(e.target.value)}
                  />
                </div>

                <div className="modal-actions">
                  <button 
                    className="btn btn-primary"
                    onClick={handleFreezeMembership}
                  >
                    Confirm Freeze
                  </button>
                  <button 
                    className="btn btn-secondary"
                    onClick={() => setShowFreezeModal(false)}
                  >
                    Cancel
                  </button>
                </div>
              </div>
            </div>
          )}

          <div className="plans-comparison">
            <h3>Upgrade Your Plan</h3>
            <div className="plans-grid">
              {['Standard', 'Premium', 'Elite'].map((plan) => (
                <div key={plan} className="plan-card">
                  <h4>{plan}</h4>
                  <p className="price">${plan === 'Standard' ? '29' : plan === 'Premium' ? '49' : '79'}/mo</p>
                  <ul className="features">
                    <li>✓ Unlimited Classes</li>
                    {plan !== 'Standard' && <li>✓ Personal Training</li>}
                    {plan === 'Elite' && <li>✓ Nutrition Coaching</li>}
                  </ul>
                  <button 
                    className="btn btn-primary"
                    onClick={() => handleUpgradeMembership(plan)}
                  >
                    Select Plan
                  </button>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {activeTab === 'booking' && (
        <div className="class-booking">
          <h3>Available Classes</h3>
          <div className="classes-grid">
            {classes.map((gym_class) => (
              <div key={gym_class.id} className="class-card">
                <h4>{gym_class.name}</h4>
                <p><strong>Time:</strong> {gym_class.time}</p>
                <p><strong>Trainer:</strong> {gym_class.trainer}</p>
                <p><strong>Available:</strong> {gym_class.capacity - gym_class.booked}/{gym_class.capacity}</p>
                <button 
                  className="btn btn-primary"
                  onClick={() => handleBookClass(gym_class.id)}
                  disabled={gym_class.booked >= gym_class.capacity}
                >
                  {gym_class.booked >= gym_class.capacity ? 'Full' : 'Book Class'}
                </button>
              </div>
            ))}
          </div>
        </div>
      )}

      {activeTab === 'bookings' && (
        <div className="my-bookings">
          <h3>My Class Bookings</h3>
          {bookings.length === 0 ? (
            <p>No bookings yet</p>
          ) : (
            <table className="bookings-table">
              <thead>
                <tr>
                  <th>Class</th>
                  <th>Date</th>
                  <th>Time</th>
                  <th>Trainer</th>
                  <th>Action</th>
                </tr>
              </thead>
              <tbody>
                {bookings.map((booking) => (
                  <tr key={booking.id}>
                    <td>{booking.className}</td>
                    <td>{booking.date}</td>
                    <td>{booking.time}</td>
                    <td>{booking.trainer}</td>
                    <td>
                      <button 
                        className="btn-small btn-danger"
                        onClick={() => handleCancelBooking(booking.id)}
                      >
                        Cancel
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>
      )}
    </div>
  )
}

export default MembershipPortal
