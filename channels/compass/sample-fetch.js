import fs from 'fs';

const API_BASE_URL = 'http://localhost:3001';

async function fetchWithSavedSession() {
  if (!fs.existsSync('session.json')) {
    console.error('Error: session.json not found. Run sample-login.js first.');
    process.exit(1);
  }

  const session = JSON.parse(fs.readFileSync('session.json', 'utf8'));
  console.log(`Using saved session for: ${session.baseUrl}`);

  const headers = {
    'x-compass-base-url': session.baseUrl,
    ...session.cookies
  };

  try {
    console.log('Fetching user details...');
    const response = await fetch(`${API_BASE_URL}/user-details`, { headers });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(`Request failed: ${JSON.stringify(errorData)}`);
    }

    const userDetails = await response.json();
    console.log('\nUser Details Received:');
    console.log(`- Full Name: ${userDetails.fullName}`);
    console.log(`- Compass ID: ${userDetails.compassID}`);
    console.log(`- Email: ${userDetails.email}`);

    console.log('\nFetching calendar events...');
    const eventsResponse = await fetch(`${API_BASE_URL}/calendar-events`, { headers });
    const events = await eventsResponse.json();
    console.log(`Received ${events.length} events.`);
    if (events.length > 0) {
      console.log(`First event: ${events[0].longTitle}`);
    }

  } catch (error) {
    console.error(`Error: ${error.message}`);
    process.exit(1);
  }
}

fetchWithSavedSession();
