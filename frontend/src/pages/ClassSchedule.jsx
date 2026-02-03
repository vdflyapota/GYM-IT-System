import { useState, useEffect } from 'react';
import { classesAPI } from '../services/api';
import './ClassSchedule.css';

export default function ClassSchedule() {
  const [schedule, setSchedule] = useState([]);
  const [filteredSchedule, setFilteredSchedule] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [selectedClass, setSelectedClass] = useState(null);
  const [isLoggedIn] = useState(!!localStorage.getItem('token'));

  const [filters, setFilters] = useState({
    classType: 'all',
    trainer: 'all',
    day: 'all'
  });

  const classTypes = [
    { id: 'yoga', name: '🧘 Yoga', color: '#667eea' },
    { id: 'hiit', name: '⚡ HIIT', color: '#f093fb' },
    { id: 'pilates', name: '💪 Pilates', color: '#4facfe' },
    { id: 'zumba', name: '💃 Zumba', color: '#fa709a' },
    { id: 'boxing', name: '🥊 Boxing', color: '#ff6b6b' },
    { id: 'crossfit', name: '🏋️ CrossFit', color: '#ffa502' }
  ];

  const daysOfWeek = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'];

  useEffect(() => {
    fetchSchedule();
  }, []);

  useEffect(() => {
    applyFilters();
  }, [schedule, filters]);

  const fetchSchedule = async () => {
    try {
      setLoading(true);
      const data = await classesAPI.getSchedule();
      if (data && Array.isArray(data)) {
        setSchedule(data);
        setError('');
      } else {
        // Use mock data if API fails
        setSchedule(generateMockSchedule());
      }
    } catch (err) {
      console.error('Failed to fetch schedule:', err);
      // Use mock data as fallback
      setSchedule(generateMockSchedule());
      setError('Using local schedule data');
    } finally {
      setLoading(false);
    }
  };

  const generateMockSchedule = () => {
    const trainers = ['John Smith', 'Sarah Johnson', 'Mike Davis', 'Emma Wilson', 'Alex Kumar'];
    const schedule = [];

    for (let day = 0; day < 7; day++) {
      const dayName = daysOfWeek[day];
      const classCount = Math.floor(Math.random() * 3) + 3; // 3-5 classes per day

      for (let i = 0; i < classCount; i++) {
        const classType = classTypes[Math.floor(Math.random() * classTypes.length)];
        const hour = 6 + Math.floor(Math.random() * 14); // 6 AM to 8 PM
        const trainer = trainers[Math.floor(Math.random() * trainers.length)];

        schedule.push({
          id: `${day}-${i}`,
          day: dayName,
          dayIndex: day,
          classType: classType.id,
          className: classType.name,
          time: `${hour.toString().padStart(2, '0')}:${Math.random() > 0.5 ? '00' : '30'}`,
          trainer: trainer,
          duration: 45 + Math.floor(Math.random() * 30), // 45-75 minutes
          capacity: 20,
          enrolled: Math.floor(Math.random() * 18),
          location: ['Studio A', 'Studio B', 'Gym Floor'][Math.floor(Math.random() * 3)],
          level: ['Beginner', 'Intermediate', 'Advanced'][Math.floor(Math.random() * 3)]
        });
      }
    }

    return schedule.sort((a, b) => {
      if (a.dayIndex !== b.dayIndex) return a.dayIndex - b.dayIndex;
      return a.time.localeCompare(b.time);
    });
  };

  const applyFilters = () => {
    let filtered = schedule;

    if (filters.classType !== 'all') {
      filtered = filtered.filter(s => s.classType === filters.classType);
    }

    if (filters.trainer !== 'all') {
      filtered = filtered.filter(s => s.trainer === filters.trainer);
    }

    if (filters.day !== 'all') {
      filtered = filtered.filter(s => s.day === filters.day);
    }

    setFilteredSchedule(filtered);
  };

  const getUniqueTrainers = () => {
    return [...new Set(schedule.map(s => s.trainer))].sort();
  };

  const handleFilterChange = (filterName, value) => {
    setFilters(prev => ({
      ...prev,
      [filterName]: value
    }));
  };

  const handleClassClick = (classItem) => {
    setSelectedClass(selectedClass?.id === classItem.id ? null : classItem);
  };

  const resetFilters = () => {
    setFilters({
      classType: 'all',
      trainer: 'all',
      day: 'all'
    });
  };

  return (
    <div className="class-schedule">
      <div className="schedule-header">
        <h1>📅 Class Schedule</h1>
        <p>Find the perfect class for you. No login required!</p>
      </div>

      {error && <div className="error-message">{error}</div>}

      {/* Filter Section */}
      <div className="filters-section">
        <div className="filter-group">
          <label htmlFor="class-type">Class Type:</label>
          <select
            id="class-type"
            value={filters.classType}
            onChange={(e) => handleFilterChange('classType', e.target.value)}
            className="filter-select"
          >
            <option value="all">All Classes</option>
            {classTypes.map(ct => (
              <option key={ct.id} value={ct.id}>{ct.name}</option>
            ))}
          </select>
        </div>

        <div className="filter-group">
          <label htmlFor="trainer">Trainer:</label>
          <select
            id="trainer"
            value={filters.trainer}
            onChange={(e) => handleFilterChange('trainer', e.target.value)}
            className="filter-select"
          >
            <option value="all">All Trainers</option>
            {getUniqueTrainers().map(trainer => (
              <option key={trainer} value={trainer}>{trainer}</option>
            ))}
          </select>
        </div>

        <div className="filter-group">
          <label htmlFor="day">Day:</label>
          <select
            id="day"
            value={filters.day}
            onChange={(e) => handleFilterChange('day', e.target.value)}
            className="filter-select"
          >
            <option value="all">All Days</option>
            {daysOfWeek.map(day => (
              <option key={day} value={day}>{day}</option>
            ))}
          </select>
        </div>

        <button className="btn-reset" onClick={resetFilters}>Clear Filters</button>
      </div>

      {/* Results Info */}
      <div className="results-info">
        <span>Showing {filteredSchedule.length} classes</span>
      </div>

      {/* Schedule View */}
      {loading ? (
        <div className="loading">Loading schedule...</div>
      ) : filteredSchedule.length === 0 ? (
        <div className="no-data">
          <p>No classes found matching your filters.</p>
          <button className="btn-reset" onClick={resetFilters}>Clear filters and try again</button>
        </div>
      ) : (
        <div className="schedule-container">
          {daysOfWeek.map(day => {
            const dayClasses = filteredSchedule.filter(s => s.day === day);
            return dayClasses.length > 0 && (
              <div key={day} className="day-section">
                <h2 className="day-header">{day}</h2>
                <div className="classes-grid">
                  {dayClasses.map(classItem => (
                    <div
                      key={classItem.id}
                      className={`class-card ${selectedClass?.id === classItem.id ? 'selected' : ''}`}
                      onClick={() => handleClassClick(classItem)}
                    >
                      <div className="class-card-header">
                        <span className="class-type-badge" style={{backgroundColor: classTypes.find(ct => ct.id === classItem.classType)?.color}}>
                          {classItem.className}
                        </span>
                        <span className="class-time">{classItem.time}</span>
                      </div>

                      <div className="class-card-body">
                        <p className="trainer"><strong>👨‍🏫 {classItem.trainer}</strong></p>
                        <p className="meta">⏱️ {classItem.duration} min | 📍 {classItem.location}</p>
                        <p className="level">📊 {classItem.level}</p>

                        <div className="enrollment-bar">
                          <div className="enrollment-fill" style={{width: `${(classItem.enrolled / classItem.capacity) * 100}%`}}></div>
                        </div>
                        <p className="enrollment-text">{classItem.enrolled}/{classItem.capacity} enrolled</p>
                      </div>

                      {selectedClass?.id === classItem.id && (
                        <div className="class-details">
                          <hr />
                          <div className="detail-row">
                            <span>Class Type:</span>
                            <strong>{classItem.className}</strong>
                          </div>
                          <div className="detail-row">
                            <span>Day:</span>
                            <strong>{classItem.day}</strong>
                          </div>
                          <div className="detail-row">
                            <span>Time:</span>
                            <strong>{classItem.time}</strong>
                          </div>
                          <div className="detail-row">
                            <span>Duration:</span>
                            <strong>{classItem.duration} minutes</strong>
                          </div>
                          <div className="detail-row">
                            <span>Trainer:</span>
                            <strong>{classItem.trainer}</strong>
                          </div>
                          <div className="detail-row">
                            <span>Location:</span>
                            <strong>{classItem.location}</strong>
                          </div>
                          <div className="detail-row">
                            <span>Level:</span>
                            <strong>{classItem.level}</strong>
                          </div>
                          {isLoggedIn ? (
                            <button className="btn-register">✅ Sign Up for Class</button>
                          ) : (
                            <a href="/login" className="btn-register">🔑 Login to Sign Up</a>
                          )}
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
