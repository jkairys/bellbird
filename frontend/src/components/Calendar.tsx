import { useState, useMemo } from 'react';
import './Calendar.css';

function Calendar({ events }) {
  const [currentDate, setCurrentDate] = useState(new Date());

  // Get the first day of the current month
  const firstDayOfMonth = new Date(currentDate.getFullYear(), currentDate.getMonth(), 1);
  // Get the last day of the current month
  const lastDayOfMonth = new Date(currentDate.getFullYear(), currentDate.getMonth() + 1, 0);

  // Get the day of week for the first day (0 = Sunday, 6 = Saturday)
  const firstDayOfWeek = firstDayOfMonth.getDay();

  // Calculate total days in the month
  const daysInMonth = lastDayOfMonth.getDate();

  // Generate calendar days array
  const calendarDays = useMemo(() => {
    const days = [];

    // Add empty cells for days before the first day of the month
    for (let i = 0; i < firstDayOfWeek; i++) {
      days.push(null);
    }

    // Add actual days of the month
    for (let day = 1; day <= daysInMonth; day++) {
      days.push(day);
    }

    return days;
  }, [firstDayOfWeek, daysInMonth]);

  // Map events to dates
  const eventsByDate = useMemo(() => {
    const map = {};

    if (!events?.events) return map;

    events.events.forEach(event => {
      const eventDate = new Date(event.start);
      const dateKey = `${currentDate.getFullYear()}-${currentDate.getMonth()}-${eventDate.getDate()}`;

      // Only include events from the current month
      if (eventDate.getMonth() === currentDate.getMonth() &&
          eventDate.getFullYear() === currentDate.getFullYear()) {
        if (!map[dateKey]) {
          map[dateKey] = [];
        }
        map[dateKey].push(event);
      }
    });

    return map;
  }, [events, currentDate]);

  // Navigation functions
  const goToPreviousMonth = () => {
    setCurrentDate(new Date(currentDate.getFullYear(), currentDate.getMonth() - 1, 1));
  };

  const goToNextMonth = () => {
    setCurrentDate(new Date(currentDate.getFullYear(), currentDate.getMonth() + 1, 1));
  };

  const goToToday = () => {
    setCurrentDate(new Date());
  };

  // Format month and year for display
  const monthYear = currentDate.toLocaleDateString('en-US', {
    month: 'long',
    year: 'numeric'
  });

  // Check if a date is today
  const isToday = (day) => {
    const today = new Date();
    return day === today.getDate() &&
           currentDate.getMonth() === today.getMonth() &&
           currentDate.getFullYear() === today.getFullYear();
  };

  // Get events for a specific day
  const getEventsForDay = (day) => {
    const dateKey = `${currentDate.getFullYear()}-${currentDate.getMonth()}-${day}`;
    return eventsByDate[dateKey] || [];
  };

  return (
    <div className="calendar">
      <div className="calendar-header">
        <button onClick={goToPreviousMonth} className="nav-button">←</button>
        <div className="calendar-title">
          <h2>{monthYear}</h2>
          <button onClick={goToToday} className="today-button">Today</button>
        </div>
        <button onClick={goToNextMonth} className="nav-button">→</button>
      </div>

      <div className="calendar-grid">
        {/* Day of week headers */}
        {['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'].map(day => (
          <div key={day} className="calendar-day-header">
            {day}
          </div>
        ))}

        {/* Calendar day cells */}
        {calendarDays.map((day, index) => {
          if (day === null) {
            return <div key={`empty-${index}`} className="calendar-day empty"></div>;
          }

          const dayEvents = getEventsForDay(day);
          const isTodayDate = isToday(day);

          return (
            <div
              key={day}
              className={`calendar-day ${isTodayDate ? 'today' : ''} ${dayEvents.length > 0 ? 'has-events' : ''}`}
            >
              <div className="day-number">{day}</div>

              {dayEvents.length > 0 && (
                <div className="day-events">
                  {dayEvents.slice(0, 3).map((event, idx) => (
                    <div
                      key={event.id || idx}
                      className={`event-dot ${event.all_day ? 'all-day' : ''}`}
                      title={`${event.title}${event.all_day ? ' (All Day)' : ''}`}
                    >
                      <span className="event-title">{event.title}</span>
                      {!event.all_day && (
                        <span className="event-time">
                          {new Date(event.start).toLocaleTimeString([], {
                            hour: 'numeric',
                            minute: '2-digit'
                          })}
                        </span>
                      )}
                    </div>
                  ))}
                  {dayEvents.length > 3 && (
                    <div className="event-more">+{dayEvents.length - 3} more</div>
                  )}
                </div>
              )}
            </div>
          );
        })}
      </div>

      {events?.batch && (
        <p className="calendar-sync-info">
          Last synced: {new Date(events.batch.created_at).toLocaleString()}
        </p>
      )}
    </div>
  );
}

export default Calendar;
