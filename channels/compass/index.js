import 'dotenv/config';
import { CompassClient } from 'compass-education';

// Load credentials from environment variables
const baseUrl = process.env.COMPASS_BASE_URL?.replace(/^https?:\/\//, '') || '';
const username = process.env.COMPASS_USERNAME || '';
const password = process.env.COMPASS_PASSWORD || '';

if (!baseUrl || !username || !password) {
  console.error('Missing required environment variables: COMPASS_BASE_URL, COMPASS_USERNAME, COMPASS_PASSWORD');
  process.exit(1);
}

// Create a new client instance:
const compass = new CompassClient(baseUrl);

(async () => {
  // Log into compass:
  await compass
    .login({
      username,
      password
    });

  // Fetch my timetable for today:
  const todayTimetable = await compass.getCalendarEvents();
  console.log(todayTimetable);

  // Fetch my timetable for a specific day:
  const specificDayTimetable = await compass.getCalendarEvents({
    startDate: "2022-01-01", // Can also be a Date object.
    endDate: "2022-01-01" // Can also be a Date object.
  });
  console.log(specificDayTimetable);

  // What is my name?
  const userDetails = await compass.getUserDetails();
  console.log(userDetails.fullName);

  // Terminate the session:
  await compass.logout();
})();