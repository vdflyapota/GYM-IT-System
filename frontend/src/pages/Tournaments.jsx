import React, { useState, useEffect } from 'react'
import { tournamentsAPI } from '../services/api'
import './Tournaments.css'

function Tournaments() {
  const [tournaments, setTournaments] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    fetchTournaments()
  }, [])

  const fetchTournaments = async () => {
    try {
      setLoading(true)
      const data = await tournamentsAPI.listTournaments()
      // Extract tournaments array from response
      const tournamentsArray = data.tournaments || data || []
      setTournaments(tournamentsArray)
      setError('')
    } catch (err) {
      setError(err.message || 'Failed to load tournaments')
      console.error('Error fetching tournaments:', err)
      // Use mock data if API fails
      setTournaments([
        {
          id: 1,
          name: 'Summer Fitness Challenge',
          status: 'active',
          participants: 45,
          startDate: '2025-06-01',
          endDate: '2025-08-31',
        },
        {
          id: 2,
          name: 'Weight Loss Competition',
          status: 'active',
          participants: 32,
          startDate: '2025-07-15',
          endDate: '2025-09-30',
        },
      ])
    } finally {
      setLoading(false)
    }
  }

  const handleJoinTournament = async (tournamentId) => {
    try {
      await tournamentsAPI.joinTournament(tournamentId)
      alert('Successfully joined tournament!')
      fetchTournaments()
    } catch (err) {
      alert('Failed to join tournament: ' + err.message)
    }
  }

  if (loading) return <div className="tournaments-container"><p>Loading tournaments...</p></div>

  return (
    <div className="tournaments-container">
      <h1>🏆 Tournaments</h1>
      
      {error && <div className="error-message">{error}</div>}

      {tournaments.length === 0 ? (
        <p>No tournaments available at the moment.</p>
      ) : (
        <div className="tournaments-grid">
          {tournaments.map(tournament => (
            <div key={tournament.id} className="tournament-card">
              <h3>{tournament.name}</h3>
              <p className="status"><strong>Status:</strong> {tournament.status || 'Active'}</p>
              <p><strong>Participants:</strong> {tournament.participant_count || tournament.participants || 0}</p>
              <p><strong>Max Participants:</strong> {tournament.max_participants || 'Unlimited'}</p>
              <p><strong>Period:</strong> {tournament.start_date || tournament.startDate} to {tournament.end_date || tournament.endDate}</p>
              <button 
                className="btn btn-primary"
                onClick={() => handleJoinTournament(tournament.id)}
              >
                Join Tournament
              </button>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}

export default Tournaments
