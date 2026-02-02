import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { applicationsAPI } from '../services/api';
import './Hiring.css';

export default function Hiring() {
  const navigate = useNavigate();
  const [userRole, setUserRole] = useState('user');

  useEffect(() => {
    // Safely parse user data
    let user = {}
    try {
      const userStr = localStorage.getItem('user')
      if (userStr) {
        user = JSON.parse(userStr)
      }
    } catch (e) {
      // If parsing fails, assume regular user
      user = {}
    }
    
    setUserRole(user.role || 'user');
    
    // Admins shouldn't be hiring themselves
    if (user.role === 'admin') {
      navigate('/admin/reports');
    }
  }, [navigate]);

  const [jobListings] = useState([
    {
      id: 1,
      title: 'Senior Fitness Trainer',
      department: 'Training',
      location: 'Main Studio',
      experience: '3+ years',
      salary: '$40,000 - $50,000',
      description: 'We are looking for an experienced fitness trainer to lead group classes and personal training sessions.',
      requirements: [
        'Certification from ACE or NASM',
        '3+ years fitness training experience',
        'Strong communication skills',
        'CPR/AED certification',
        'Ability to work flexible hours including weekends'
      ],
      benefits: [
        'Competitive salary',
        'Health insurance',
        'Free gym membership',
        'Professional development opportunities',
        'Performance bonuses'
      ]
    },
    {
      id: 2,
      title: 'Yoga Instructor',
      department: 'Classes',
      location: 'Studio A',
      experience: '1+ years',
      salary: '$30,000 - $40,000',
      description: 'Join our team as a Yoga Instructor and help members achieve their wellness goals through guided yoga sessions.',
      requirements: [
        'Yoga Teacher Certification (RYT-200)',
        '1+ years teaching experience',
        'Passion for wellness and mindfulness',
        'Excellent class management skills'
      ],
      benefits: [
        'Flexible schedule',
        'Free yoga classes',
        'Wellness programs',
        'Supportive community',
        'Growth opportunities'
      ]
    },
    {
      id: 3,
      title: 'Gym Manager',
      department: 'Management',
      location: 'Main Branch',
      experience: '5+ years',
      salary: '$50,000 - $65,000',
      description: 'Lead and manage daily gym operations, ensure member satisfaction, and oversee a team of fitness professionals.',
      requirements: [
        '5+ years in fitness industry management',
        'Leadership and team management experience',
        'Strong financial and budgeting skills',
        'Excellent customer service skills',
        'Knowledge of gym operations and safety'
      ],
      benefits: [
        'Competitive salary',
        'Performance bonus',
        'Health insurance',
        'Retirement plan',
        'Flexible work schedule'
      ]
    }
  ]);

  const [applications, setApplications] = useState([]);
  const [selectedJob, setSelectedJob] = useState(null);
  const [formData, setFormData] = useState({
    fullName: '',
    email: '',
    phone: '',
    position: '',
    experience: '',
    cv: null,
    coverLetter: ''
  });
  const [submitMessage, setSubmitMessage] = useState('');

  const handleJobClick = (job) => {
    setSelectedJob(selectedJob?.id === job.id ? null : job);
    if (selectedJob?.id !== job.id) {
      setFormData(prev => ({ ...prev, position: job.title }));
    }
  };

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleFileChange = (e) => {
    setFormData(prev => ({
      ...prev,
      cv: e.target.files[0]
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    // Validation
    if (!formData.fullName || !formData.email || !formData.phone || !formData.position || !formData.cv) {
      setSubmitMessage('Please fill in all required fields.');
      return;
    }

    try {
      // Prepare form data with file
      const submitData = new FormData();
      submitData.append('fullName', formData.fullName);
      submitData.append('email', formData.email);
      submitData.append('phone', formData.phone);
      submitData.append('position', formData.position);
      submitData.append('experience', formData.experience);
      submitData.append('coverLetter', formData.coverLetter);
      submitData.append('cv', formData.cv);

      // Try to submit to backend API
      const token = localStorage.getItem('token');
      const response = await fetch('http://localhost:8000/api/applications/submit', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`
        },
        body: submitData
      });

      if (response.ok) {
        setSubmitMessage('✅ Application submitted successfully! We will review your CV and contact you soon.');
        // Reset form
        setFormData({
          fullName: '',
          email: '',
          phone: '',
          position: '',
          experience: '',
          cv: null,
          coverLetter: ''
        });
      } else {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to submit application');
      }
    } catch (err) {
      setSubmitMessage(`❌ Error: ${err.message || 'Failed to submit application'}`);
      console.error('Application submission error:', err);
    }
  };
        coverLetter: ''
      });

      // Clear message after 5 seconds
      setTimeout(() => setSubmitMessage(''), 5000);
    } catch (err) {
      // If backend fails, use local submission
      console.error('API submission failed, using local storage:', err);
      
      const newApplication = {
        id: applications.length + 1,
        ...formData,
        appliedAt: new Date().toLocaleDateString(),
        status: 'pending'
      };

      setApplications(prev => [...prev, newApplication]);
      setSubmitMessage('✅ Application submitted successfully! We will review your CV and contact you soon.');

      // Reset form
      setFormData({
        fullName: '',
        email: '',
        phone: '',
        position: '',
        experience: '',
        cv: null,
        coverLetter: ''
      });

      // Clear message after 5 seconds
      setTimeout(() => setSubmitMessage(''), 5000);
    }
  };

  return (
    <div className="hiring-page">
      <div className="hiring-header">
        <h1>💼 Join Our Team!</h1>
        <p>Be part of a dynamic fitness community. Apply now to become a trainer or manager!</p>
      </div>

      {submitMessage && (
        <div className={`submit-message ${submitMessage.includes('successfully') ? 'success' : 'error'}`}>
          {submitMessage}
        </div>
      )}

      <div className="hiring-content">
        {/* Job Listings Section */}
        <div className="jobs-section">
          <h2>Available Positions</h2>
          <div className="jobs-grid">
            {jobListings.map(job => (
              <div
                key={job.id}
                className={`job-card ${selectedJob?.id === job.id ? 'selected' : ''}`}
                onClick={() => handleJobClick(job)}
              >
                <div className="job-card-header">
                  <h3>{job.title}</h3>
                  <span className="department-badge">{job.department}</span>
                </div>

                <div className="job-info">
                  <p><strong>📍</strong> {job.location}</p>
                  <p><strong>⏱️</strong> {job.experience}</p>
                  <p><strong>💰</strong> {job.salary}</p>
                </div>

                <p className="job-description">{job.description}</p>

                {selectedJob?.id === job.id && (
                  <div className="job-details">
                    <div className="requirements">
                      <h4>Requirements:</h4>
                      <ul>
                        {job.requirements.map((req, idx) => (
                          <li key={idx}>{req}</li>
                        ))}
                      </ul>
                    </div>

                    <div className="benefits">
                      <h4>Benefits:</h4>
                      <ul>
                        {job.benefits.map((benefit, idx) => (
                          <li key={idx}>{benefit}</li>
                        ))}
                      </ul>
                    </div>
                  </div>
                )}

                <button className="btn-view-more">
                  {selectedJob?.id === job.id ? 'Hide Details ▲' : 'View Details ▼'}
                </button>
              </div>
            ))}
          </div>
        </div>

        {/* Application Form Section */}
        <div className="application-section">
          <h2>Apply Now</h2>

          <form onSubmit={handleSubmit} className="application-form">
            <div className="form-group">
              <label htmlFor="fullName">Full Name *</label>
              <input
                type="text"
                id="fullName"
                name="fullName"
                value={formData.fullName}
                onChange={handleInputChange}
                placeholder="John Doe"
                required
              />
            </div>

            <div className="form-row">
              <div className="form-group">
                <label htmlFor="email">Email Address *</label>
                <input
                  type="email"
                  id="email"
                  name="email"
                  value={formData.email}
                  onChange={handleInputChange}
                  placeholder="john@example.com"
                  required
                />
              </div>

              <div className="form-group">
                <label htmlFor="phone">Phone Number *</label>
                <input
                  type="tel"
                  id="phone"
                  name="phone"
                  value={formData.phone}
                  onChange={handleInputChange}
                  placeholder="+1 (555) 000-0000"
                  required
                />
              </div>
            </div>

            <div className="form-group">
              <label htmlFor="position">Applying for Position *</label>
              <select
                id="position"
                name="position"
                value={formData.position}
                onChange={handleInputChange}
                required
              >
                <option value="">Select a position</option>
                {jobListings.map(job => (
                  <option key={job.id} value={job.title}>
                    {job.title} - {job.department}
                  </option>
                ))}
              </select>
            </div>

            <div className="form-group">
              <label htmlFor="experience">Years of Experience</label>
              <select
                id="experience"
                name="experience"
                value={formData.experience}
                onChange={handleInputChange}
              >
                <option value="">Select experience level</option>
                <option value="0-1">0-1 years</option>
                <option value="1-3">1-3 years</option>
                <option value="3-5">3-5 years</option>
                <option value="5+">5+ years</option>
              </select>
            </div>

            <div className="form-group">
              <label htmlFor="cv">Upload CV/Resume *</label>
              <div className="file-input-wrapper">
                <input
                  type="file"
                  id="cv"
                  name="cv"
                  onChange={handleFileChange}
                  accept=".pdf,.doc,.docx"
                  required
                />
                <span className="file-label">
                  {formData.cv ? `✓ ${formData.cv.name}` : 'Choose a PDF or Word document'}
                </span>
              </div>
              <p className="file-note">Accepted formats: PDF, DOC, DOCX (Max 5MB)</p>
            </div>

            <div className="form-group">
              <label htmlFor="coverLetter">Cover Letter</label>
              <textarea
                id="coverLetter"
                name="coverLetter"
                value={formData.coverLetter}
                onChange={handleInputChange}
                placeholder="Tell us why you would be a great fit for this position..."
                rows="5"
              />
            </div>

            <button type="submit" className="btn-submit">
              📤 Submit Application
            </button>
          </form>

          {applications.length > 0 && (
            <div className="applications-history">
              <h3>Your Applications</h3>
              <div className="history-list">
                {applications.map(app => (
                  <div key={app.id} className="history-item">
                    <div className="history-info">
                      <p><strong>{app.position}</strong></p>
                      <p className="history-date">Applied: {app.appliedAt}</p>
                    </div>
                    <span className={`status-badge status-${app.status}`}>
                      {app.status.toUpperCase()}
                    </span>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
