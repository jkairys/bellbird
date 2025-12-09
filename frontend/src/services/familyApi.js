/**
 * API service functions for family management (children, organisations, channels).
 *
 * All functions handle error responses and return structured data.
 */

const API_BASE_URL = '/api';

/**
 * Handle API responses and errors.
 * @param {Response} response - Fetch response object
 * @returns {Promise<any>} Parsed JSON data
 * @throws {Error} API error with message
 */
async function handleResponse(response) {
  const data = await response.json().catch(() => ({}));

  if (!response.ok) {
    const message = data.message || data.error || `HTTP ${response.status}: ${response.statusText}`;
    throw new Error(message);
  }

  return data;
}

// ==================== CHILD API FUNCTIONS ====================

/**
 * Create a new child profile.
 * @param {Object} childData - Child data (name, date_of_birth, gender?, interests?)
 * @returns {Promise<Object>} Created child object with id
 */
export async function createChild(childData) {
  const response = await fetch(`${API_BASE_URL}/children`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(childData),
  });

  return handleResponse(response);
}

/**
 * Get all children.
 * @returns {Promise<Array>} Array of child objects
 */
export async function getChildren() {
  const response = await fetch(`${API_BASE_URL}/children`);
  return handleResponse(response);
}

/**
 * Get a single child by ID.
 * @param {string} childId - Child UUID
 * @returns {Promise<Object>} Child object
 */
export async function getChild(childId) {
  const response = await fetch(`${API_BASE_URL}/children/${childId}`);
  return handleResponse(response);
}

/**
 * Update a child profile.
 * @param {string} childId - Child UUID
 * @param {Object} childData - Updated child data
 * @returns {Promise<Object>} Updated child object
 */
export async function updateChild(childId, childData) {
  const response = await fetch(`${API_BASE_URL}/children/${childId}`, {
    method: 'PUT',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(childData),
  });

  return handleResponse(response);
}

/**
 * Delete a child profile.
 * @param {string} childId - Child UUID
 * @returns {Promise<void>}
 */
export async function deleteChild(childId) {
  const response = await fetch(`${API_BASE_URL}/children/${childId}`, {
    method: 'DELETE',
  });

  if (!response.ok) {
    const data = await response.json().catch(() => ({}));
    const message = data.message || data.error || `HTTP ${response.status}: ${response.statusText}`;
    throw new Error(message);
  }

  // 204 No Content - no body to parse
  return;
}

// ==================== ORGANISATION API FUNCTIONS (Future) ====================

/**
 * Create a new organisation.
 * @param {Object} orgData - Organisation data
 * @returns {Promise<Object>} Created organisation
 */
export async function createOrganisation(orgData) {
  const response = await fetch(`${API_BASE_URL}/organisations`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(orgData),
  });

  return handleResponse(response);
}

/**
 * Get all organisations.
 * @param {string} [type] - Optional filter by organisation type
 * @returns {Promise<Array>} Array of organisations
 */
export async function getOrganisations(type = null) {
  const url = type
    ? `${API_BASE_URL}/organisations?type=${encodeURIComponent(type)}`
    : `${API_BASE_URL}/organisations`;

  const response = await fetch(url);
  return handleResponse(response);
}

/**
 * Get a single organisation by ID.
 * @param {string} orgId - Organisation UUID
 * @returns {Promise<Object>} Organisation object
 */
export async function getOrganisation(orgId) {
  const response = await fetch(`${API_BASE_URL}/organisations/${orgId}`);
  return handleResponse(response);
}

/**
 * Update an organisation.
 * @param {string} orgId - Organisation UUID
 * @param {Object} orgData - Updated organisation data
 * @returns {Promise<Object>} Updated organisation
 */
export async function updateOrganisation(orgId, orgData) {
  const response = await fetch(`${API_BASE_URL}/organisations/${orgId}`, {
    method: 'PUT',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(orgData),
  });

  return handleResponse(response);
}

/**
 * Delete an organisation.
 * @param {string} orgId - Organisation UUID
 * @returns {Promise<void>}
 */
export async function deleteOrganisation(orgId) {
  const response = await fetch(`${API_BASE_URL}/organisations/${orgId}`, {
    method: 'DELETE',
  });

  if (!response.ok) {
    const data = await response.json().catch(() => ({}));
    const message = data.message || data.error || `HTTP ${response.status}: ${response.statusText}`;
    throw new Error(message);
  }

  return;
}

// ==================== ASSOCIATION API FUNCTIONS (Future) ====================

/**
 * Get all organisations for a child.
 * @param {string} childId - Child UUID
 * @returns {Promise<Array>} Array of organisations
 */
export async function getChildOrganisations(childId) {
  const response = await fetch(`${API_BASE_URL}/children/${childId}/organisations`);
  return handleResponse(response);
}

/**
 * Associate a child with an organisation.
 * @param {string} childId - Child UUID
 * @param {string} organisationId - Organisation UUID
 * @returns {Promise<void>}
 */
export async function addChildOrganisation(childId, organisationId) {
  const response = await fetch(`${API_BASE_URL}/children/${childId}/organisations`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ organisation_id: organisationId }),
  });

  return handleResponse(response);
}

/**
 * Remove a child-organisation association.
 * @param {string} childId - Child UUID
 * @param {string} organisationId - Organisation UUID
 * @returns {Promise<void>}
 */
export async function removeChildOrganisation(childId, organisationId) {
  const response = await fetch(`${API_BASE_URL}/children/${childId}/organisations/${organisationId}`, {
    method: 'DELETE',
  });

  if (!response.ok) {
    const data = await response.json().catch(() => ({}));
    const message = data.message || data.error || `HTTP ${response.status}: ${response.statusText}`;
    throw new Error(message);
  }

  return;
}
