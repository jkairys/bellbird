/**
 * API service functions for family management (children, organisations, channels).
 *
 * All functions handle error responses and return structured data.
 */

import type {
  Child,
  Organisation,
  Channel,
  CreateChildData,
  UpdateChildData,
  CreateOrganisationData,
  UpdateOrganisationData,
  CreateChannelData,
  UpdateChannelData,
} from '../types/api';

const API_BASE_URL = '/api';

/**
 * Handle API responses and errors.
 * @param response - Fetch response object
 * @returns Parsed JSON data
 * @throws Error with API error message
 */
async function handleResponse<T>(response: Response): Promise<T> {
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
 * @param childData - Child data (name, date_of_birth, gender?, interests?)
 * @returns Created child object with id
 */
export async function createChild(childData: CreateChildData): Promise<Child> {
  const response = await fetch(`${API_BASE_URL}/children`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(childData),
  });

  return handleResponse<Child>(response);
}

/**
 * Get all children.
 * @returns Array of child objects
 */
export async function getChildren(): Promise<Child[]> {
  const response = await fetch(`${API_BASE_URL}/children`);
  return handleResponse<Child[]>(response);
}

/**
 * Get a single child by ID.
 * @param childId - Child UUID
 * @returns Child object
 */
export async function getChild(childId: string): Promise<Child> {
  const response = await fetch(`${API_BASE_URL}/children/${childId}`);
  return handleResponse<Child>(response);
}

/**
 * Update a child profile.
 * @param childId - Child UUID
 * @param childData - Updated child data
 * @returns Updated child object
 */
export async function updateChild(childId: string, childData: UpdateChildData): Promise<Child> {
  const response = await fetch(`${API_BASE_URL}/children/${childId}`, {
    method: 'PUT',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(childData),
  });

  return handleResponse<Child>(response);
}

/**
 * Delete a child profile.
 * @param childId - Child UUID
 * @returns void
 */
export async function deleteChild(childId: string): Promise<void> {
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

// ==================== ORGANISATION API FUNCTIONS ====================

/**
 * Create a new organisation.
 * @param orgData - Organisation data
 * @returns Created organisation
 */
export async function createOrganisation(orgData: CreateOrganisationData): Promise<Organisation> {
  const response = await fetch(`${API_BASE_URL}/organisations`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(orgData),
  });

  return handleResponse<Organisation>(response);
}

/**
 * Get all organisations.
 * @param type - Optional filter by organisation type
 * @returns Array of organisations
 */
export async function getOrganisations(type: string | null = null): Promise<Organisation[]> {
  const url = type
    ? `${API_BASE_URL}/organisations?type=${encodeURIComponent(type)}`
    : `${API_BASE_URL}/organisations`;

  const response = await fetch(url);
  return handleResponse<Organisation[]>(response);
}

/**
 * Get a single organisation by ID.
 * @param orgId - Organisation UUID
 * @returns Organisation object
 */
export async function getOrganisation(orgId: string): Promise<Organisation> {
  const response = await fetch(`${API_BASE_URL}/organisations/${orgId}`);
  return handleResponse<Organisation>(response);
}

/**
 * Update an organisation.
 * @param orgId - Organisation UUID
 * @param orgData - Updated organisation data
 * @returns Updated organisation
 */
export async function updateOrganisation(orgId: string, orgData: UpdateOrganisationData): Promise<Organisation> {
  const response = await fetch(`${API_BASE_URL}/organisations/${orgId}`, {
    method: 'PUT',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(orgData),
  });

  return handleResponse<Organisation>(response);
}

/**
 * Delete an organisation.
 * @param orgId - Organisation UUID
 * @returns void
 */
export async function deleteOrganisation(orgId: string): Promise<void> {
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

// ==================== ASSOCIATION API FUNCTIONS ====================

/**
 * Get all organisations for a child.
 * @param childId - Child UUID
 * @returns Array of organisations
 */
export async function getChildOrganisations(childId: string): Promise<Organisation[]> {
  const response = await fetch(`${API_BASE_URL}/children/${childId}/organisations`);
  return handleResponse<Organisation[]>(response);
}

/**
 * Associate a child with an organisation.
 * @param childId - Child UUID
 * @param organisationId - Organisation UUID
 * @returns void
 */
export async function addChildOrganisation(childId: string, organisationId: string): Promise<void> {
  const response = await fetch(`${API_BASE_URL}/children/${childId}/organisations`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ organisation_id: organisationId }),
  });

  return handleResponse<void>(response);
}

/**
 * Remove a child-organisation association.
 * @param childId - Child UUID
 * @param organisationId - Organisation UUID
 * @returns void
 */
export async function removeChildOrganisation(childId: string, organisationId: string): Promise<void> {
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

// ==================== CHANNEL API FUNCTIONS ====================

/**
 * Get all channels for an organisation.
 * @param orgId - Organisation UUID
 * @returns Array of channel objects
 */
export async function getOrganisationChannels(orgId: string): Promise<Channel[]> {
  const response = await fetch(`${API_BASE_URL}/organisations/${orgId}/channels`);
  return handleResponse<Channel[]>(response);
}

/**
 * Create a new channel for an organisation.
 * @param orgId - Organisation UUID
 * @param channelData - Channel data
 * @returns Created channel object
 */
export async function createChannel(orgId: string, channelData: CreateChannelData): Promise<Channel> {
  const response = await fetch(`${API_BASE_URL}/organisations/${orgId}/channels`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(channelData),
  });

  return handleResponse<Channel>(response);
}

/**
 * Get a single channel by ID.
 * @param channelId - Channel UUID
 * @returns Channel object
 */
export async function getChannel(channelId: string): Promise<Channel> {
  const response = await fetch(`${API_BASE_URL}/channels/${channelId}`);
  return handleResponse<Channel>(response);
}

/**
 * Update a channel.
 * @param channelId - Channel UUID
 * @param channelData - Updated channel data
 * @returns Updated channel object
 */
export async function updateChannel(channelId: string, channelData: UpdateChannelData): Promise<Channel> {
  const response = await fetch(`${API_BASE_URL}/channels/${channelId}`, {
    method: 'PUT',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(channelData),
  });

  return handleResponse<Channel>(response);
}

/**
 * Delete a channel.
 * @param channelId - Channel UUID
 * @returns void
 */
export async function deleteChannel(channelId: string): Promise<void> {
  const response = await fetch(`${API_BASE_URL}/channels/${channelId}`, {
    method: 'DELETE',
  });

  if (!response.ok) {
    const data = await response.json().catch(() => ({}));
    const message = data.message || data.error || `HTTP ${response.status}: ${response.statusText}`;
    throw new Error(message);
  }

  return;
}
