import { useState, useEffect } from 'react';
import { getUserDetails, getEvents } from '../services/api';
import './Dashboard.css';

function Dashboard() {
  const [user, setUser] = useState(null);
  const [events, setEvents] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

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

  const displayEvents = events?.events?.slice(0, 10) || [];
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
        <h2>Upcoming Events</h2>
        {user?.batch && (
          <p className="batch-info">
            Last synced: {new Date(user.batch.created_at).toLocaleString()}
          </p>
        )}

        {displayEvents.length === 0 ? (
          <p className="no-events">No events found</p>
        ) : (
          <div className="events-list">
            {displayEvents.map((event, index) => (
              <div key={event.activity_id || event.instance_id || index} className="event-card">
                <div className="event-header">
                  <h3>{event.long_title_without_time || event.long_title || event.title}</h3>
                  {event.all_day ? (
                    <span className="event-badge all-day">All Day</span>
                  ) : (
                    <span className="event-time">
                      {new Date(event.start).toLocaleTimeString([], {
                        hour: '2-digit',
                        minute: '2-digit'
                      })}
                    </span>
                  )}
                </div>

                <div className="event-details">
                  <p className="event-date">
                    {new Date(event.start).toLocaleDateString([], {
                      weekday: 'long',
                      year: 'numeric',
                      month: 'long',
                      day: 'numeric'
                    })}
                  </p>

                  {event.description && event.description.trim() && (
                    <p className="event-description">{event.description}</p>
                  )}

                  {event.location && (
                    <p className="event-location">📍 {event.location}</p>
                  )}

                  {event.managers && event.managers.length > 0 && (
                    <p className="event-attendees">
                      👥 {event.managers.length} manager{event.managers.length !== 1 ? 's' : ''}
                    </p>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}

        {events?.events?.length > 10 && (
          <p className="showing-count">
            Showing 10 of {events.events.length} events
          </p>
        )}
      </section>
    </div>
  );
}

export default Dashboard;
