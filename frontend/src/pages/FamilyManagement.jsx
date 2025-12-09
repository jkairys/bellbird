import React, { useState, useEffect } from 'react';
import ChildList from '../components/family/ChildList';
import ChildForm from '../components/family/ChildForm';
import OrganisationList from '../components/family/OrganisationList';
import OrganisationForm from '../components/family/OrganisationForm';
import { useFamily } from '../contexts/FamilyContext'; // Import useFamily hook
import './FamilyManagement.css';

function FamilyManagement() {
  const {
    childrenList,
    organisationsList,
    loading,
    error, // Although toast handles error now, keeping for consistency.
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
  } = useFamily(); // Use the FamilyContext

  // Tab State
  const [activeTab, setActiveTab] = useState('children'); // 'children' | 'organisations'

  // Child Form State
  const [showChildForm, setShowChildForm] = useState(false);
  const [editingChild, setEditingChild] = useState(null);

  // Organisation Form/Filter State
  const [showOrgForm, setShowOrgForm] = useState(false);
  const [editingOrg, setEditingOrg] = useState(null);
  const [orgTypeFilter, setOrgTypeFilter] = useState('');

  // Child Handlers (now using context functions)
  const handleAddChild = () => {
    setEditingChild(null);
    setShowChildForm(true);
  };

  const handleEditChild = async (child) => {
    const fullChild = await fetchChildDetails(child.id);
    if (fullChild) {
      setEditingChild(fullChild);
      setShowChildForm(true);
    }
  };

  const handleDeleteChild = async (child) => {
    if (!window.confirm(`Are you sure you want to delete ${child.name}? This action cannot be undone.`)) return;
    const success = await removeChild(child.id);
    if (success) {
      // Toast handled by context
    }
  };

  const handleSubmitChild = async (childData) => {
    let success;
    if (editingChild) {
      success = await editChild(editingChild.id, childData);
    } else {
      success = await addChild(childData);
    }
    if (success) {
      setShowChildForm(false);
      setEditingChild(null);
    }
  };

  const handleCancelChildForm = () => {
    setShowChildForm(false);
    setEditingChild(null);
  };

  // Organisation Handlers (now using context functions)
  const handleAddOrg = () => {
    setEditingOrg(null);
    setShowOrgForm(true);
  };

  const handleEditOrg = async (org) => {
    const fullOrg = await fetchOrganisationDetails(org.id);
    if (fullOrg) {
      setEditingOrg(fullOrg);
      setShowOrgForm(true);
    }
  };

  const handleDeleteOrg = async (org) => {
    if (!window.confirm(`Are you sure you want to delete ${org.name}?`)) return;
    const success = await removeOrganisation(org.id);
    if (success) {
      // Toast handled by context
    }
  };

  const handleSubmitOrg = async (orgData) => {
    let success;
    if (editingOrg) {
      success = await editOrganisation(editingOrg.id, orgData);
    } else {
      success = await addOrganisation(orgData);
    }
    if (success) {
      setShowOrgForm(false);
      setEditingOrg(null);
    }
  };

  const handleCancelOrgForm = () => {
    setShowOrgForm(false);
    setEditingOrg(null);
  };
  
  const handleOrgFilter = (type) => {
      // Context's refreshOrganisations handles filtering
      refreshOrganisations(type || null);
  };

  // Channel Handlers (passed to OrganisationForm, which passes to ChannelConfig)
  const handleAddChannel = async (orgId, channelData) => {
      const success = await addChannel(orgId, channelData);
      if (success) {
          // Refresh the currently editing org to show new channel
          const fullOrg = await fetchOrganisationDetails(orgId);
          if (fullOrg) setEditingOrg(fullOrg);
      }
      return success; // Return success status to ChannelConfig
  };

  const handleUpdateChannel = async (channelId, channelData) => {
      const success = await editChannel(channelId, channelData);
      if (success) {
          // Refresh the currently editing org to show updated channel
          if (editingOrg) {
             const fullOrg = await fetchOrganisationDetails(editingOrg.id);
             if (fullOrg) setEditingOrg(fullOrg);
          }
      }
      return success; // Return success status to ChannelConfig
  };

  const handleDeleteChannel = async (channelId) => {
      const success = await removeChannel(channelId);
      if (success) {
          // Refresh the currently editing org to reflect channel removal
          if (editingOrg) {
             const fullOrg = await fetchOrganisationDetails(editingOrg.id);
             if (fullOrg) setEditingOrg(fullOrg);
          }
      }
      return success; // Return success status to ChannelConfig
  };


  return (
    <div className="family-management">
      <header className="page-header">
        <h1>Family Management</h1>
        <p>Manage your children's profiles and school information</p>
      </header>

      {toast && (
        <div className={`toast toast-${toast.type}`}>
          {toast.message}
          <button onClick={clearToast} className="toast-close">×</button>
        </div>
      )}

      {error && ( // Display generic error if any, not handled by toast
        <div className="error-banner">
          {error}
          <button onClick={clearError} className="error-close">×</button>
        </div>
      )}

      {/* Tabs */}
      <div className="tabs">
        <button 
          className={`tab-btn ${activeTab === 'children' ? 'active' : ''}`}
          onClick={() => setActiveTab('children')}
        >
          Children
        </button>
        <button 
          className={`tab-btn ${activeTab === 'organisations' ? 'active' : ''}`}
          onClick={() => setActiveTab('organisations')}
        >
          Organisations
        </button>
      </div>

      <div className="page-actions">
        {activeTab === 'children' && !showChildForm && (
          <button onClick={handleAddChild} className="btn btn-primary" disabled={loading}>+ Add Child</button>
        )}
        {activeTab === 'organisations' && !showOrgForm && (
          <button onClick={handleAddOrg} className="btn btn-primary" disabled={loading}>+ Add Organisation</button>
        )}
      </div>

      {/* Children Tab Content */}
      {activeTab === 'children' && (
        <>
          {showChildForm ? (
            <ChildForm
              child={editingChild}
              onSubmit={handleSubmitChild}
              onCancel={handleCancelChildForm}
              loading={loading}
              availableOrganisations={organisationsList} // Pass available organisations
              onAddOrg={
                  async (orgId) => { // T068, T070
                      if (editingChild) {
                          const success = await associateChild(editingChild.id, orgId);
                          if (success) {
                              const updatedChild = await fetchChildDetails(editingChild.id);
                              if (updatedChild) setEditingChild(updatedChild);
                          }
                      }
                  }
              }
              onRemoveOrg={
                  async (orgId) => { // T068, T070
                      if (editingChild) {
                          const success = await dissociateChild(editingChild.id, orgId);
                          if (success) {
                              const updatedChild = await fetchChildDetails(editingChild.id);
                              if (updatedChild) setEditingChild(updatedChild);
                          }
                      }
                  }
              }
            />
          ) : (
            <ChildList
              children={childrenList}
              onEdit={handleEditChild}
              onDelete={handleDeleteChild}
              loading={loading}
            />
          )}
        </>
      )}

      {/* Organisations Tab Content */}
      {activeTab === 'organisations' && (
        <>
          {showOrgForm ? (
            <OrganisationForm
              existingOrg={editingOrg}
              onSubmit={handleSubmitOrg}
              onCancel={handleCancelOrgForm}
              loading={loading}
              onAddChannel={handleAddChannel}
              onUpdateChannel={handleUpdateChannel}
              onDeleteChannel={handleDeleteChannel}
            />
          ) : (
            <OrganisationList
              organisations={organisationsList}
              onEdit={handleEditOrg}
              onDelete={handleDeleteOrg}
              onFilter={handleOrgFilter}
              loading={loading}
            />
          )}
        </>
      )}
    </div>
  );
}

export default FamilyManagement;