// ==================== USER TYPES ====================
export interface User {
  user_preferred_name?: string;
  user_first_name?: string;
  user_full_name?: string;
  user_email?: string;
  user_display_code?: string;
}

export interface UserDetailsResponse {
  user: User;
}

// ==================== EVENT TYPES ====================
export interface Event {
  id: string;
  title: string;
  start: string; // ISO date string
  end?: string;
  all_day: boolean;
  location?: string;
  description?: string;
}

export interface EventBatch {
  created_at: string; // ISO date string
  id: string;
}

export interface EventsResponse {
  events: Event[];
  event_count: number;
  batch?: EventBatch;
}

// ==================== FAMILY TYPES ====================
export interface Child {
  id: string;
  name: string;
  date_of_birth: string; // YYYY-MM-DD format
  gender?: string;
  year_level?: string;
  interests?: string;
  organisations?: Organisation[];
  created_at?: string;
  updated_at?: string;
}

export interface Organisation {
  id: string;
  name: string;
  type: string; // e.g., "school", "club"
  address?: string;
  contact_email?: string;
  contact_phone?: string;
  channels?: Channel[];
  created_at?: string;
  updated_at?: string;
}

export interface Channel {
  id: string;
  organisation_id: string;
  name: string;
  type: string; // e.g., "compass", "classdojo"
  config?: Record<string, unknown>;
  is_active: boolean;
  created_at?: string;
  updated_at?: string;
}

// ==================== API REQUEST TYPES ====================
export interface CreateChildData {
  name: string;
  date_of_birth: string;
  gender?: string;
  year_level?: string;
  interests?: string;
}

export interface UpdateChildData extends Partial<CreateChildData> {}

export interface CreateOrganisationData {
  name: string;
  type: string;
  address?: string;
  contact_email?: string;
  contact_phone?: string;
}

export interface UpdateOrganisationData extends Partial<CreateOrganisationData> {}

export interface CreateChannelData {
  name: string;
  type: string;
  config?: Record<string, unknown>;
  is_active?: boolean;
}

export interface UpdateChannelData extends Partial<CreateChannelData> {}

// ==================== CONTEXT TYPES ====================
export interface Toast {
  message: string;
  type: 'success' | 'error' | 'info';
}

export interface FamilyContextValue {
  childrenList: Child[];
  organisationsList: Organisation[];
  loading: boolean;
  error: string | null;
  toast: Toast | null;
  clearError: () => void;
  clearToast: () => void;
  refreshChildren: () => Promise<void>;
  refreshOrganisations: (type?: string | null) => Promise<void>;
  addChild: (data: CreateChildData) => Promise<boolean>;
  editChild: (id: string, data: UpdateChildData) => Promise<boolean>;
  removeChild: (id: string) => Promise<boolean>;
  fetchChildDetails: (id: string) => Promise<Child | null>;
  addOrganisation: (data: CreateOrganisationData) => Promise<boolean>;
  editOrganisation: (id: string, data: UpdateOrganisationData) => Promise<boolean>;
  removeOrganisation: (id: string) => Promise<boolean>;
  fetchOrganisationDetails: (id: string) => Promise<Organisation | null>;
  associateChild: (childId: string, orgId: string) => Promise<boolean>;
  dissociateChild: (childId: string, orgId: string) => Promise<boolean>;
  addChannel: (orgId: string, data: CreateChannelData) => Promise<boolean>;
  editChannel: (id: string, data: UpdateChannelData) => Promise<boolean>;
  removeChannel: (id: string) => Promise<boolean>;
}
