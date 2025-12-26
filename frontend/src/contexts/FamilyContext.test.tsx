import { describe, it, expect, vi, beforeEach } from 'vitest';
import { renderHook, waitFor, act } from '@testing-library/react';
import { FamilyProvider, useFamily } from './FamilyContext';
import type { Child, Organisation } from '../types/api';

// Mock fetch globally
const mockFetch = vi.fn();
global.fetch = mockFetch;

// Sample data for tests
const mockChildren: Child[] = [
  {
    id: '1',
    name: 'Test Child',
    date_of_birth: '2018-05-15',
    gender: 'female',
    organisations: [],
  },
];

const mockOrganisations: Organisation[] = [
  {
    id: '1',
    name: 'Test School',
    type: 'school',
    address: '123 Main St',
  },
];

describe('FamilyContext', () => {
  beforeEach(() => {
    vi.resetAllMocks();
  });

  it('should throw error when useFamily is used outside provider', () => {
    // We need to suppress console.error for this test
    const consoleSpy = vi.spyOn(console, 'error').mockImplementation(() => {});

    expect(() => {
      renderHook(() => useFamily());
    }).toThrow('useFamily must be used within a FamilyProvider');

    consoleSpy.mockRestore();
  });

  it('should provide initial empty state', async () => {
    mockFetch.mockResolvedValue({
      ok: true,
      json: async () => [],
    });

    const { result } = renderHook(() => useFamily(), {
      wrapper: FamilyProvider,
    });

    await waitFor(() => {
      expect(result.current.loading).toBe(false);
    });

    expect(result.current.childrenList).toEqual([]);
    expect(result.current.organisationsList).toEqual([]);
    expect(result.current.error).toBeNull();
  });

  it('should fetch children on mount', async () => {
    mockFetch
      .mockResolvedValueOnce({
        ok: true,
        json: async () => mockChildren,
      })
      .mockResolvedValueOnce({
        ok: true,
        json: async () => mockOrganisations,
      });

    const { result } = renderHook(() => useFamily(), {
      wrapper: FamilyProvider,
    });

    await waitFor(() => {
      expect(result.current.childrenList).toHaveLength(1);
    });

    expect(result.current.childrenList[0].name).toBe('Test Child');
  });

  it('should handle API errors gracefully', async () => {
    mockFetch.mockRejectedValue(new Error('Network error'));

    const { result } = renderHook(() => useFamily(), {
      wrapper: FamilyProvider,
    });

    await waitFor(() => {
      expect(result.current.loading).toBe(false);
    });

    expect(result.current.toast?.type).toBe('error');
  });

  it('should add a child', async () => {
    // Initial fetch returns empty
    mockFetch
      .mockResolvedValueOnce({ ok: true, json: async () => [] })
      .mockResolvedValueOnce({ ok: true, json: async () => [] });

    const { result } = renderHook(() => useFamily(), {
      wrapper: FamilyProvider,
    });

    await waitFor(() => {
      expect(result.current.loading).toBe(false);
    });

    // Mock the POST and subsequent GET
    mockFetch
      .mockResolvedValueOnce({
        ok: true,
        json: async () => ({ id: '2', name: 'New Child', date_of_birth: '2020-01-01' }),
      })
      .mockResolvedValueOnce({
        ok: true,
        json: async () => [{ id: '2', name: 'New Child', date_of_birth: '2020-01-01' }],
      });

    await act(async () => {
      const success = await result.current.addChild({
        name: 'New Child',
        date_of_birth: '2020-01-01',
      });
      expect(success).toBe(true);
    });

    expect(result.current.toast?.type).toBe('success');
  });
});
