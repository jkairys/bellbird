import { useMemo } from 'react';
import './ThisWeekView.css';

function ThisWeekView({ events }) {
  // Calculate the current week boundaries (Sunday to Saturday)
  const { weekStart, weekEnd } = useMemo(() => {
    const now = new Date();
    const dayOfWeek = now.getDay(); // 0 = Sunday, 6 = Saturday

    // Get Sunday of current week
    const start = new Date(now);
    start.setDate(now.getDate() - dayOfWeek);
    start.setHours(0, 0, 0, 0);

    // Get Saturday of current week
    const end = new Date(start);
    end.setDate(start.getDate() + 6);
    end.setHours(23, 59, 59, 999);

    return { weekStart: start, weekEnd: end };
  }, []);

  // Filter and group events by day
  const eventsThisWeek = useMemo(() => {
    if (!events?.events) return {};

    const grouped = {};

    events.events.forEach(event => {
      const eventDate = new Date(event.start);

      // Check if event falls within this week
      if (eventDate >= weekStart && eventDate <= weekEnd) {
        const dateKey = eventDate.toLocaleDateString('en-US', {
          weekday: 'long',
          month: 'long',
          day: 'numeric',
          year: 'numeric'
        });

        if (!grouped[dateKey]) {
          grouped[dateKey] = {
            date: eventDate,
            events: []
          };
        }
        grouped[dateKey].events.push(event);
      }
    });

    // Sort events within each day by time
    Object.values(grouped).forEach(day => {
      day.events.sort((a, b) => new Date(a.start) - new Date(b.start));
    });

    return grouped;
  }, [events, weekStart, weekEnd]);

  // Create array of days sorted chronologically
  const sortedDays = useMemo(() => {
    return Object.entries(eventsThisWeek)
      .sort(([, a], [, b]) => a.date - b.date);
  }, [eventsThisWeek]);

  // Format week range for header
  const weekRange = `${weekStart.toLocaleDateString('en-US', { month: 'short', day: 'numeric' })} - ${weekEnd.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })}`;

  // Check if a date is today
  const isToday = (date) => {
    const today = new Date();
    return date.toDateString() === today.toDateString();
  };

  return (
    <div className="this-week-view">
      <div className="week-header">
        <h2>This Week</h2>
        <p className="week-range">{weekRange}</p>
      </div>

      {sortedDays.length === 0 ? (
        <div className="no-events-week">
          <p>No events scheduled for this week</p>
        </div>
      ) : (
        <div className="week-days-list">
          {sortedDays.map(([dateKey, dayData]) => (
            <div key={dateKey} className="day-section">
              <div className={`day-header ${isToday(dayData.date) ? 'today' : ''}`}>
                <h3>{dateKey}</h3>
                {isToday(dayData.date) && <span className="today-badge">Today</span>}
              </div>

              <div className="day-events-list">
                {dayData.events.map((event, idx) => (
                  <div key={event.id || idx} className="week-event-card">
                    <div className="event-time-section">
                      {event.all_day ? (
                        <span className="all-day-badge">All Day</span>
                      ) : (
                        <span className="event-time">
                          {new Date(event.start).toLocaleTimeString([], {
                            hour: 'numeric',
                            minute: '2-digit'
                          })}
                        </span>
                      )}
                    </div>

                    <div className="event-details-section">
                      <h4 className="event-title">{event.title}</h4>
                      {event.description && (
                        <p className="event-description">{event.description}</p>
                      )}
                      {event.location && (
                        <p className="event-location">📍 {event.location}</p>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          ))}
        </div>
      )}

      {events?.batch && (
        <p className="week-sync-info">
          Last synced: {new Date(events.batch.created_at).toLocaleString()}
        </p>
      )}
    </div>
  );
}

export default ThisWeekView;
