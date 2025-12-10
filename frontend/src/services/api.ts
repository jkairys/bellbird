import type { UserDetailsResponse, EventsResponse } from '../types/api';

const API_BASE_URL = '/api';

export class ApiError extends Error {
  status: number;

  constructor(message: string, status: number) {
    super(message);
    this.name = 'ApiError';
    this.status = status;
  }
}

async function fetchApi<T>(endpoint: string): Promise<T> {
  try {
    const response = await fetch(`${API_BASE_URL}${endpoint}`);

    if (!response.ok) {
      throw new ApiError(
        `API request failed: ${response.statusText}`,
        response.status
      );
    }

    return await response.json();
  } catch (error) {
    if (error instanceof ApiError) {
      throw error;
    }
    throw new ApiError(`Network error: ${(error as Error).message}`, 0);
  }
}

export async function getUserDetails(): Promise<UserDetailsResponse> {
  return fetchApi<UserDetailsResponse>('/user');
}

export async function getEvents(): Promise<EventsResponse> {
  return fetchApi<EventsResponse>('/events');
}
