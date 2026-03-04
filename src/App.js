import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { PieChart, Pie, Cell, ResponsiveContainer, Legend, Tooltip, BarChart, Bar, XAxis, YAxis, CartesianGrid } from 'recharts';
import './App.css';

function App() {
  const [todayData, setTodayData] = useState(null);
  const [historyData, setHistoryData] = useState([]);
  const [dashboardStats, setDashboardStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('dashboard');
  const [employeeId, setEmployeeId] = useState('');
  const [checkInMessage, setCheckInMessage] = useState('');
  const [checkInStatus, setCheckInStatus] = useState('');

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      const [todayRes, historyRes, statsRes] = await Promise.all([
        axios.get('/api/attendance/today'),
        axios.get('/api/attendance/history'),
        axios.get('/api/dashboard/stats')
      ]);

      setTodayData(todayRes.data);
      setHistoryData(historyRes.data);
      setDashboardStats(statsRes.data);
    } catch (error) {
      console.error('Error fetching data:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleCheckIn = async (e) => {
    if (e.key === 'Enter' && employeeId.trim()) {
      try {
        const response = await axios.post('/api/attendance/check-in', {
          employee_id: employeeId.trim()
        });
        
        setCheckInMessage(`✅ ${response.data.message} - Time: ${response.data.check_in_time}`);
        setCheckInStatus(response.data.status);
        setEmployeeId('');
        
        // Refresh data
        fetchData();
        
        // Clear message after 3 seconds
        setTimeout(() => {
          setCheckInMessage('');
          setCheckInStatus('');
        }, 3000);
        
      } catch (error) {
        if (error.response) {
          setCheckInMessage(`❌ ${error.response.data.error}`);
        } else {
          setCheckInMessage('❌ Check in error!');
        }
        setCheckInStatus('error');
        
        setTimeout(() => {
          setCheckInMessage('');
          setCheckInStatus('');
        }, 3000);
      }
    }
  };

  const pieData = todayData ? [
    { name: 'On-Time', value: todayData.present_count, color: '#10b981' },
    { name: 'Late', value: todayData.late_count || 0, color: '#f59e0b' },
    { name: 'Absent', value: todayData.absent_count, color: '#ef4444' }
  ] : [];

  const barData = historyData.slice(-7).map(day => ({
    date: new Date(day.date).toLocaleDateString('th-TH', { day: 'numeric', month: 'short' }),
    attendance: day.attendance_percentage
  }));

  if (loading) {
    return (
      <div className="loading-container">
        <div className="spinner"></div>
        <p>loading...</p>
      </div>
    );
  }

  return (
    <div className="App">
      <header className="app-header">
        <h1>🏢 Attendance Tracking System</h1>
        
        {/* Check-in Section */}
        <div className="check-in-section">
          <div className="check-in-container">
            <input
              type="text"
              placeholder="Enter Employee ID..."
              value={employeeId}
              onChange={(e) => setEmployeeId(e.target.value)}
              onKeyDown={handleCheckIn}
              className="check-in-input"
            />
            {checkInMessage && (
              <div className={`check-in-message ${checkInStatus}`}>
                {checkInMessage}
              </div>
            )}
          </div>
        </div>
      </header>

      <nav className="nav-tabs">
        <button 
          className={activeTab === 'dashboard' ? 'active' : ''}
          onClick={() => setActiveTab('dashboard')}
        >
          📊 DashBoard
        </button>
        <button 
          className={activeTab === 'details' ? 'active' : ''}
          onClick={() => setActiveTab('details')}
        >
          👥 Details
        </button>
        <button 
          className={activeTab === 'history' ? 'active' : ''}
          onClick={() => setActiveTab('history')}
        >
          📈 History
        </button>
      </nav>

      <main className="main-content">
        {activeTab === 'dashboard' && (
          <div className="dashboard-section">
            <div className="stats-grid">
              <div className="stat-card">
                <h3>Today</h3>
                <div className="stat-number">{dashboardStats?.today.present || 0}/{dashboardStats?.today.total || 0}</div>
                <div className="stat-percentage">{dashboardStats?.today.percentage || 0}%</div>
              </div>
              <div className="stat-card">
                <h3>Week</h3>
                <div className="stat-number">{dashboardStats?.week.present || 0}/{dashboardStats?.week.total || 0}</div>
                <div className="stat-percentage">{dashboardStats?.week.percentage || 0}%</div>
              </div>
              <div className="stat-card">
                <h3>Month</h3>
                <div className="stat-number">{dashboardStats?.month.present || 0}/{dashboardStats?.month.total || 0}</div>
                <div className="stat-percentage">{dashboardStats?.month.percentage || 0}%</div>
              </div>
            </div>

            <div className="charts-container">
              <div className="chart-card">
                <h3>Attendance Rate</h3>
                <ResponsiveContainer width="100%" height={300}>
                  <PieChart>
                    <Pie
                      data={pieData}
                      cx="50%"
                      cy="50%"
                      labelLine={false}
                      label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                      outerRadius={80}
                      fill="#8884d8"
                      dataKey="value"
                    >
                      {pieData.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={entry.color} />
                      ))}
                    </Pie>
                    <Tooltip />
                    <Legend />
                  </PieChart>
                </ResponsiveContainer>
              </div>

              <div className="chart-card">
                <h3>Last 7 Days</h3>
                <ResponsiveContainer width="100%" height={300}>
                  <BarChart data={barData}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="date" />
                    <YAxis />
                    <Tooltip formatter={(value) => `${value}%`} />
                    <Bar dataKey="attendance" fill="#3b82f6" />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </div>
          </div>
        )}

        {activeTab === 'details' && (
          <div className="details-section">
            <div className="section-header">
              <h2>Attendance Details</h2>
              <p>Date: {todayData?.date}</p>
            </div>
            
            <div className="summary-cards">
              <div className="summary-card present">
                <h3>✅ On-Time</h3>
                <div className="big-number">{todayData?.present_count || 0}</div>
              </div>
              <div className="summary-card late">
                <h3>⏰ Late</h3>
                <div className="big-number">{todayData?.late_count || 0}</div>
              </div>
              <div className="summary-card absent">
                <h3>❌ Absent</h3>
                <div className="big-number">{todayData?.absent_count || 0}</div>
              </div>
              <div className="summary-card total">
                <h3>📊 Total</h3>
                <div className="big-number">{todayData?.total_employees || 0}</div>
              </div>
            </div>

            <div className="attendance-list">
              <h3>Employees Who Attended Today</h3>
              {todayData?.attendance_details?.length > 0 ? (
                <table className="attendance-table">
                  <thead>
                    <tr>
                      <th>Employee Name</th>
                      <th>Employee ID</th>
                      <th>Clock-in</th>
                      <th>Clock-out</th>
                      <th>Status</th>
                    </tr>
                  </thead>
                  <tbody>
                    {todayData.attendance_details.map((emp, index) => (
                      <tr key={index}>
                        <td>{emp.employee_name}</td>
                        <td>{emp.employee_id}</td>
                        <td>{emp.check_in || '-'}</td>
                        <td>{emp.check_out || '-'}</td>
                        <td>
                          <span className={`status-badge ${emp.status}`}>
                            {emp.status === 'present' ? 'On-Time' : 
                             emp.status === 'late' ? 'Late' : emp.status}
                          </span>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              ) : (
                <p className="no-data">No Data</p>
              )}
            </div>
          </div>
        )}

        {activeTab === 'history' && (
          <div className="history-section">
            <div className="section-header">
              <h2>Work History for Last 30 Days</h2>
            </div>
            
            <div className="history-table-container">
              <table className="history-table">
                <thead>
                  <tr>
                    <th>Date</th>
                    <th>On-Time</th>
                    <th>Late</th>
                    <th>Absent</th>
                    <th>Total</th>
                    <th>Percentage</th>
                  </tr>
                </thead>
                <tbody>
                  {historyData.map((day, index) => (
                    <tr key={index}>
                      <td>{new Date(day.date).toLocaleDateString('th-TH')}</td>
                      <td className="present-cell">{day.present_count}</td>
                      <td className="late-cell">{day.late_count || 0}</td>
                      <td className="absent-cell">{day.absent_count}</td>
                      <td>{day.total_employees}</td>
                      <td>
                        <div className="percentage-bar">
                          <div 
                            className="percentage-fill" 
                            style={{ width: `${day.attendance_percentage}%` }}
                          ></div>
                          <span className="percentage-text">{day.attendance_percentage}%</span>
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}
      </main>

      <footer className="app-footer">
        <p>© 2026 Attendance Tracking System</p>
      </footer>
    </div>
  );
}

export default App;
