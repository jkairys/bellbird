import 'dotenv/config';
import express from 'express';
import { CompassClient } from 'compass-education';

// Monkey-patch unmarshalCookies to prevent corruption if it's called
try {
  const originalUnmarshal = CompassClient.unmarshalCookies;
  CompassClient.unmarshalCookies = function (cookies) {
    if (Array.isArray(cookies) && cookies.length > 0 && typeof cookies[0] !== 'string') {
      return cookies;
    }
    return originalUnmarshal(cookies);
  };
} catch (e) {
  console.warn("Failed to patch unmarshalCookies", e.message);
}

const app = express();
app.use(express.json());

app.use((req, res, next) => {
  console.log(`${new Date().toISOString()} - ${req.method} ${req.url}`);
  next();
});

const PORT = process.env.PORT || 3001;

app.get('/health', (req, res) => {
  res.json({ status: 'ok' });
});

/**
 * Robustly initializes a CompassClient by ensuring the browser is ready
 * and that we have the necessary session metadata (userID).
 */
const getClientFromIncomingRequest = async (req) => {
  const baseUrlInput = req.headers['x-compass-base-url'] || req.query.baseUrl || req.body.baseUrl;
  if (!baseUrlInput) throw new Error('Missing baseURL');

  // Ensure baseURL has protocol AND No trailing slash
  let fullBaseUrl = baseUrlInput.startsWith('http') ? baseUrlInput : `https://${baseUrlInput}`;
  fullBaseUrl = fullBaseUrl.replace(/\/$/, '');

  const cookies = Object.entries(req.headers)
    .filter(([key]) => key.startsWith('x-cookie-'))
    .map(([key, value]) => `${key.replace('x-cookie-', '')}=${value}`);

  if (cookies.length === 0) throw new Error('No cookies provided');

  console.log(`[API-NEW] Initialising client for ${fullBaseUrl}`);

  const client = new CompassClient({ baseURL: fullBaseUrl, cookies });
  await client.initialise();

  console.log(`[DEBUG] Navigating to ${fullBaseUrl} to trigger ID extraction...`);
  await client.page.goto(fullBaseUrl, { waitUntil: 'networkidle2' });

  const sessionData = await client.page.evaluate(() => {
    return {
      userId: window?.Compass?.organisationUserId,
      configKey: window?.Compass?.referenceDataCacheKeys?.schoolConfigKey,
      url: window.location.href
    };
  });

  console.log(`[DEBUG] Page URL: ${sessionData.url}, Extracted userID: ${sessionData.userId}`);

  if (sessionData.userId) {
    client.userID = sessionData.userId;
  }
  if (sessionData.configKey) {
    client.schoolConfigKey = sessionData.configKey;
  }

  // Set the baseURL to exactly what the browser says it is
  client.baseURL = sessionData.url.replace(/\/$/, '');

  return client;
};

app.get('/user-details', async (req, res) => {
  let client;
  try {
    client = await getClientFromIncomingRequest(req);
    console.log("[DEBUG] Calling getUserDetails...");
    const userDetails = await client.getUserDetails();
    res.json(userDetails);
  } catch (error) {
    console.error('[API] Error in /user-details:', error.message);
    res.status(500).json({ error: error.message });
  } finally {
    if (client) await client.logout();
  }
});

app.post('/login', async (req, res) => {
  const { baseUrl, username, password } = req.body;
  let client;
  try {
    const fullBaseUrl = baseUrl.startsWith('http') ? baseUrl : `https://${baseUrl}`;
    client = new CompassClient(fullBaseUrl);
    await client.login({ username, password });
    if (client.cookies) {
      client.cookies.forEach(c => res.setHeader(`x-cookie-${c.name}`, c.value));
    }
    res.json({ message: 'Login successful' });
  } catch (error) {
    console.error('[API] Login Error:', error.message);
    res.status(401).json({ error: error.message });
  } finally {
    if (client) await client.logout();
  }
});

app.get('/calendar-events', async (req, res) => {
  const { startDate, endDate } = req.query;
  let client;
  try {
    client = await getClientFromIncomingRequest(req);
    const events = await client.getCalendarEvents({
      startDate: startDate || new Date().toISOString().split('T')[0],
      endDate: endDate || new Date().toISOString().split('T')[0]
    });
    res.json(events);
  } catch (error) {
    console.error('[API] Calendar Error:', error.message);
    res.status(500).json({ error: error.message });
  } finally {
    if (client) await client.logout();
  }
});

app.listen(PORT, () => {
  console.log(`Compass Stateless API Adapter listening on port ${PORT}`);
});