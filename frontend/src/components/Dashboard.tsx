import { useState, useEffect } from 'react';
import { getUserDetails, getEvents } from '../services/api';
import Calendar from './Calendar';
import ThisWeekView from './ThisWeekView';
import './Dashboard.css';

function Dashboard() {
  const [user, setUser] = useState(null);
  const [events, setEvents] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [viewMode, setViewMode] = useState('calendar'); // 'calendar' or 'thisWeek'

  useEffect(() => {
    async function fetchData() {
      try {
        setLoading(true);
        setError(null);

        const [userData, eventsData] = await Promise.all([
          getUserDetails(),
          getEvents()
        ]);

        setUser(userData);
        setEvents(eventsData);
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    }

    fetchData();
  }, []);

  if (loading) {
    return <div className="loading">Loading dashboard...</div>;
  }

  if (error) {
    return (
      <div className="error">
        <h2>Error loading dashboard</h2>
        <p>{error}</p>
        <p className="error-hint">
          Make sure the API server is running with: <code>poetry run bellweaver api serve</code>
        </p>
      </div>
    );
  }

  const userName = user?.user?.user_preferred_name || user?.user?.user_first_name || 'User';
  const userFullName = user?.user?.user_full_name;

  return (
    <div className="dashboard">
      <header className="dashboard-header">
        <h1>Welcome, {userName}</h1>
        {user?.user && (
          <div className="user-info">
            {userFullName && <p><strong>Full Name:</strong> {userFullName}</p>}
            <p><strong>Email:</strong> {user.user.user_email || 'N/A'}</p>
            {user.user.user_display_code && (
              <p><strong>Display Code:</strong> {user.user.user_display_code}</p>
            )}
          </div>
        )}
      </header>

      <section className="events-section">
        <div className="view-controls">
          <button
            className={`view-button ${viewMode === 'calendar' ? 'active' : ''}`}
            onClick={() => setViewMode('calendar')}
          >
            📅 Calendar
          </button>
          <button
            className={`view-button ${viewMode === 'thisWeek' ? 'active' : ''}`}
            onClick={() => setViewMode('thisWeek')}
          >
            📋 This Week
          </button>
        </div>

        {viewMode === 'calendar' ? (
          <Calendar events={events} />
        ) : (
          <ThisWeekView events={events} />
        )}

        {events?.event_count > 0 && (
          <p className="total-count">
            Total events in database: {events.event_count}
          </p>
        )}
      </section>
    </div>
  );
}

export default Dashboard;

