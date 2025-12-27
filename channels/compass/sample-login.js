import 'dotenv/config';
import fs from 'fs';

const API_BASE_URL = 'http://localhost:3001';
const COMPASS_BASE_URL = process.env.COMPASS_BASE_URL || 'https://seaford-northps-vic.compass.education';
const USERNAME = process.env.COMPASS_USERNAME || 'KAI0002';
const PASSWORD = process.env.COMPASS_PASSWORD || 'Sh1ttyCompass';

async function loginAndSave() {
  console.log(`Logging into Compass via API...`);

  try {
    const response = await fetch(`${API_BASE_URL}/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        baseUrl: COMPASS_BASE_URL,
        username: USERNAME,
        password: PASSWORD
      })
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(`Login failed: ${JSON.stringify(errorData)}`);
    }

    const cookies = {};
    for (const [key, value] of response.headers.entries()) {
      if (key.toLowerCase().startsWith('x-cookie-')) {
        cookies[key] = value;
      }
    }

    const session = {
      baseUrl: COMPASS_BASE_URL.replace(/^https?:\/\//, ''),
      cookies
    };

    fs.writeFileSync('session.json', JSON.stringify(session, null, 2));
    console.log('Login successful! Session saved to session.json');
    console.log(`Captured ${Object.keys(cookies).length} cookies.`);

  } catch (error) {
    console.error(`Error: ${error.message}`);
    process.exit(1);
  }
}

loginAndSave();
