import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import './AdminReports.css';

export default function AdminReports() {
  const navigate = useNavigate();
  const [users, setUsers] = useState([]);
  const [stats, setStats] = useState({
    total: 0,
    byRole: {},
    byStatus: {},
    registeredToday: 0,
    registeredThisMonth: 0
  });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [dateRange, setDateRange] = useState({
    startDate: new Date(new Date().getFullYear(), new Date().getMonth(), 1).toISOString().split('T')[0],
    endDate: new Date().toISOString().split('T')[0]
  });

  useEffect(() => {
    // Safely parse user data
    let user = {}
    try {
      const userStr = localStorage.getItem('user')
      if (userStr) {
        user = JSON.parse(userStr)
      }
    } catch (e) {
      // If parsing fails, assume not an admin
      user = {}
    }
    
    // Check if user is admin
    if (user.role !== 'admin') {
      // Redirect non-admins away
      navigate('/dashboard');
      return;
    }
    fetchUsers();
  }, [navigate]);

  const fetchUsers = async () => {
    try {
      setLoading(true);
      const response = await fetch('/api/users', {
        headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` }
      });
      
      if (!response.ok) throw new Error('Failed to fetch users');
      
      const data = await response.json();
      setUsers(data.users || data);
      calculateStats(data.users || data);
      setError('');
    } catch (err) {
      setError(err.message);
      console.error('Error fetching users:', err);
    } finally {
      setLoading(false);
    }
  };

  const calculateStats = (userList) => {
    const now = new Date();
    const today = new Date(now.getFullYear(), now.getMonth(), now.getDate());
    const monthStart = new Date(now.getFullYear(), now.getMonth(), 1);

    const byRole = {};
    const byStatus = {};
    let registeredToday = 0;
    let registeredThisMonth = 0;

    userList.forEach(user => {
      // Count by role
      const role = user.role || 'user';
      byRole[role] = (byRole[role] || 0) + 1;

      // Count by status
      const status = user.status || 'active';
      byStatus[status] = (byStatus[status] || 0) + 1;

      // Check registration date
      if (user.created_at || user.createdAt) {
        const createdDate = new Date(user.created_at || user.createdAt);
        const createdDay = new Date(createdDate.getFullYear(), createdDate.getMonth(), createdDate.getDate());
        
        if (createdDay.getTime() === today.getTime()) {
          registeredToday++;
        }
        if (createdDate >= monthStart) {
          registeredThisMonth++;
        }
      }
    });

    setStats({
      total: userList.length,
      byRole,
      byStatus,
      registeredToday,
      registeredThisMonth
    });
  };

  const exportToCSV = () => {
    if (users.length === 0) {
      alert('No users to export');
      return;
    }

    const headers = ['ID', 'Name', 'Email', 'Role', 'Status', 'Created At'];
    const rows = users.map(user => [
      user.id || '',
      user.name || user.username || '',
      user.email || '',
      user.role || 'user',
      user.status || 'active',
      user.created_at || user.createdAt || ''
    ]);

    const csvContent = [
      headers.join(','),
      ...rows.map(row => row.map(cell => `"${cell}"`).join(','))
    ].join('\n');

    const blob = new Blob([csvContent], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `users-report-${new Date().toISOString().split('T')[0]}.csv`;
    document.body.appendChild(a);
    a.click();
    window.URL.revokeObjectURL(url);
    document.body.removeChild(a);
  };

  const exportToPDF = () => {
    // Simple PDF export using basic formatting
    let pdfContent = 'USER REPORT\n';
    pdfContent += `Generated: ${new Date().toLocaleString()}\n`;
    pdfContent += '='.repeat(50) + '\n\n';

    pdfContent += 'STATISTICS\n';
    pdfContent += `-`.repeat(50) + '\n';
    pdfContent += `Total Users: ${stats.total}\n`;
    pdfContent += `Registered Today: ${stats.registeredToday}\n`;
    pdfContent += `Registered This Month: ${stats.registeredThisMonth}\n\n`;

    pdfContent += 'BY ROLE:\n';
    Object.entries(stats.byRole).forEach(([role, count]) => {
      pdfContent += `  ${role}: ${count}\n`;
    });

    pdfContent += '\nBY STATUS:\n';
    Object.entries(stats.byStatus).forEach(([status, count]) => {
      pdfContent += `  ${status}: ${count}\n`;
    });

    pdfContent += '\n' + '='.repeat(50) + '\n';
    pdfContent += 'USER DETAILS\n';
    pdfContent += '='.repeat(50) + '\n\n';

    users.forEach(user => {
      pdfContent += `Name: ${user.name || user.username || 'N/A'}\n`;
      pdfContent += `Email: ${user.email || 'N/A'}\n`;
      pdfContent += `Role: ${user.role || 'user'}\n`;
      pdfContent += `Status: ${user.status || 'active'}\n`;
      pdfContent += `Created: ${user.created_at || user.createdAt || 'N/A'}\n`;
      pdfContent += '-'.repeat(50) + '\n\n';
    });

    const blob = new Blob([pdfContent], { type: 'text/plain' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `users-report-${new Date().toISOString().split('T')[0]}.txt`;
    document.body.appendChild(a);
    a.click();
    window.URL.revokeObjectURL(url);
    document.body.removeChild(a);
  };

  return (
    <div className="admin-reports">
      <div className="reports-header">
        <h1>📊 User Reports & Analytics</h1>
        <p>Comprehensive overview of all registered users</p>
      </div>

      {error && <div className="error-message">{error}</div>}

      {/* Statistics Cards */}
      <div className="stats-grid">
        <div className="stat-card">
          <div className="stat-value">{stats.total}</div>
          <div className="stat-label">Total Users</div>
        </div>
        <div className="stat-card">
          <div className="stat-value">{stats.registeredToday}</div>
          <div className="stat-label">Registered Today</div>
        </div>
        <div className="stat-card">
          <div className="stat-value">{stats.registeredThisMonth}</div>
          <div className="stat-label">This Month</div>
        </div>
      </div>

      {/* Role & Status Breakdown */}
      <div className="breakdown-section">
        <div className="breakdown-card">
          <h3>Users by Role</h3>
          <div className="breakdown-list">
            {Object.entries(stats.byRole).map(([role, count]) => (
              <div key={role} className="breakdown-item">
                <span className="role-badge">{role}</span>
                <span className="count">{count}</span>
                <div className="progress-bar">
                  <div 
                    className="progress-fill" 
                    style={{width: `${(count / stats.total) * 100}%`}}
                  ></div>
                </div>
              </div>
            ))}
          </div>
        </div>

        <div className="breakdown-card">
          <h3>Users by Status</h3>
          <div className="breakdown-list">
            {Object.entries(stats.byStatus).map(([status, count]) => (
              <div key={status} className="breakdown-item">
                <span className={`status-badge status-${status}`}>{status}</span>
                <span className="count">{count}</span>
                <div className="progress-bar">
                  <div 
                    className="progress-fill" 
                    style={{width: `${(count / stats.total) * 100}%`}}
                  ></div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Export Options */}
      <div className="export-section">
        <h3>Export Report</h3>
        <div className="export-buttons">
          <button className="btn btn-primary" onClick={exportToCSV}>
            📥 Export to CSV
          </button>
          <button className="btn btn-secondary" onClick={exportToPDF}>
            📄 Export as Text Report
          </button>
          <button className="btn btn-info" onClick={fetchUsers}>
            🔄 Refresh Data
          </button>
        </div>
      </div>

      {/* Users Table */}
      <div className="users-table-section">
        <h3>Detailed User List ({users.length} users)</h3>
        {loading ? (
          <div className="loading">Loading users...</div>
        ) : users.length === 0 ? (
          <div className="no-data">No users found</div>
        ) : (
          <div className="table-wrapper">
            <table className="users-table">
              <thead>
                <tr>
                  <th>ID</th>
                  <th>Name</th>
                  <th>Email</th>
                  <th>Role</th>
                  <th>Status</th>
                  <th>Registered</th>
                </tr>
              </thead>
              <tbody>
                {users.map((user, idx) => (
                  <tr key={user.id || idx}>
                    <td>{user.id || 'N/A'}</td>
                    <td>{user.name || user.username || 'N/A'}</td>
                    <td>{user.email || 'N/A'}</td>
                    <td><span className="role-badge">{user.role || 'user'}</span></td>
                    <td><span className={`status-badge status-${user.status || 'active'}`}>{user.status || 'active'}</span></td>
                    <td>{new Date(user.created_at || user.createdAt).toLocaleDateString()}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}
