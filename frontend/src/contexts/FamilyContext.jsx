import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';
import {
  getChildren, createChild, updateChild, deleteChild,
  getOrganisations, createOrganisation, updateOrganisation, deleteOrganisation,
  getOrganisation, // details
  createChannel, updateChannel, deleteChannel,
  addChildOrganisation, removeChildOrganisation, getChild // details
} from '../services/familyApi';

const FamilyContext = createContext();

export function useFamily() {
  return useContext(FamilyContext);
}

export function FamilyProvider({ children }) {
  const [childrenList, setChildrenList] = useState([]);
  const [organisationsList, setOrganisationsList] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [toast, setToast] = useState(null);

  // Toast helper
  const showToast = useCallback((message, type = 'success') => {
    setToast({ message, type });
    setTimeout(() => setToast(null), 5000);
  }, []);

  const clearError = useCallback(() => setError(null), []);
  const clearToast = useCallback(() => setToast(null), []);

  // Fetch Data
  const refreshChildren = useCallback(async () => {
    setLoading(true);
    try {
      const data = await getChildren();
      setChildrenList(data);
    } catch (err) {
      setError(err.message);
      showToast('Failed to load children', 'error');
    } finally {
      setLoading(false);
    }
  }, [showToast]);

  const refreshOrganisations = useCallback(async (type = null) => {
    setLoading(true);
    try {
      const data = await getOrganisations(type);
      setOrganisationsList(data);
    } catch (err) {
      setError(err.message);
      showToast('Failed to load organisations', 'error');
    } finally {
      setLoading(false);
    }
  }, [showToast]);

  useEffect(() => {
    refreshChildren();
    refreshOrganisations();
  }, [refreshChildren, refreshOrganisations]);

  // Child Operations
  const addChild = async (data) => {
    setLoading(true);
    try {
      await createChild(data);
      await refreshChildren();
      showToast('Child created successfully', 'success');
      return true;
    } catch (err) {
      showToast(err.message, 'error');
      return false;
    } finally {
      setLoading(false);
    }
  };

  const editChild = async (id, data) => {
    setLoading(true);
    try {
      await updateChild(id, data);
      await refreshChildren();
      showToast('Child updated successfully', 'success');
      return true;
    } catch (err) {
      showToast(err.message, 'error');
      return false;
    } finally {
      setLoading(false);
    }
  };

  const removeChild = async (id) => {
    setLoading(true);
    try {
      await deleteChild(id);
      await refreshChildren();
      showToast('Child deleted successfully', 'success');
      return true;
    } catch (err) {
      showToast(err.message, 'error');
      return false;
    } finally {
      setLoading(false);
    }
  };

  const fetchChildDetails = async (id) => {
      setLoading(true);
      try {
          return await getChild(id);
      } catch (err) {
          showToast(err.message, 'error');
          return null;
      } finally {
          setLoading(false);
      }
  };

  // Organisation Operations
  const addOrganisation = async (data) => {
    setLoading(true);
    try {
      await createOrganisation(data);
      await refreshOrganisations();
      showToast('Organisation created successfully', 'success');
      return true;
    } catch (err) {
      showToast(err.message, 'error');
      return false;
    } finally {
      setLoading(false);
    }
  };

  const editOrganisation = async (id, data) => {
    setLoading(true);
    try {
      await updateOrganisation(id, data);
      await refreshOrganisations();
      showToast('Organisation updated successfully', 'success');
      return true;
    } catch (err) {
      showToast(err.message, 'error');
      return false;
    } finally {
      setLoading(false);
    }
  };

  const removeOrganisation = async (id) => {
    setLoading(true);
    try {
      await deleteOrganisation(id);
      await refreshOrganisations();
      showToast('Organisation deleted successfully', 'success');
      return true;
    } catch (err) {
      showToast(err.message, 'error');
      return false;
    } finally {
      setLoading(false);
    }
  };

  const fetchOrganisationDetails = async (id) => {
      setLoading(true);
      try {
          return await getOrganisation(id);
      } catch (err) {
          showToast(err.message, 'error');
          return null;
      } finally {
          setLoading(false);
      }
  };

  // Association Operations
  const associateChild = async (childId, orgId) => {
      setLoading(true);
      try {
          await addChildOrganisation(childId, orgId);
          showToast('Association added', 'success');
          return true;
      } catch (err) {
          showToast(err.message, 'error');
          return false;
      } finally {
          setLoading(false);
      }
  };

  const dissociateChild = async (childId, orgId) => {
      setLoading(true);
      try {
          await removeChildOrganisation(childId, orgId);
          showToast('Association removed', 'success');
          return true;
      } catch (err) {
          showToast(err.message, 'error');
          return false;
      } finally {
          setLoading(false);
      }
  };

  // Channel Operations
  const addChannel = async (orgId, data) => {
      setLoading(true);
      try {
          await createChannel(orgId, data);
          showToast('Channel added', 'success');
          return true;
      } catch (err) {
          showToast(err.message, 'error');
          return false;
      } finally {
          setLoading(false);
      }
  };

  const editChannel = async (id, data) => {
      setLoading(true);
      try {
          await updateChannel(id, data);
          showToast('Channel updated', 'success');
          return true;
      } catch (err) {
          showToast(err.message, 'error');
          return false;
      } finally {
          setLoading(false);
      }
  };

  const removeChannel = async (id) => {
      setLoading(true);
      try {
          await deleteChannel(id);
          showToast('Channel deleted', 'success');
          return true;
      } catch (err) {
          showToast(err.message, 'error');
          return false;
      } finally {
          setLoading(false);
      }
  };

  const value = {
    childrenList,
    organisationsList,
    loading,
    error,
    toast,
    clearError,
    clearToast,
    refreshChildren,
    refreshOrganisations,
    addChild,
    editChild,
    removeChild,
    fetchChildDetails,
    addOrganisation,
    editOrganisation,
    removeOrganisation,
    fetchOrganisationDetails,
    associateChild,
    dissociateChild,
    addChannel,
    editChannel,
    removeChannel
  };

  return (
    <FamilyContext.Provider value={value}>
      {children}
    </FamilyContext.Provider>
  );
}
