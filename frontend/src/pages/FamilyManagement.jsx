/**
 * FamilyManagement page - Main page for managing children and families.
 */

import React, { useState, useEffect } from 'react';
import ChildList from '../components/family/ChildList';
import ChildForm from '../components/family/ChildForm';
import {
  getChildren,
  createChild,
  updateChild,
  deleteChild,
} from '../services/familyApi';
import './FamilyManagement.css';

function FamilyManagement() {
  const [children, setChildren] = useState([]);
  const [loading, setLoading] = useState(false);
  const [showForm, setShowForm] = useState(false);
  const [editingChild, setEditingChild] = useState(null);
  const [error, setError] = useState(null);
  const [toast, setToast] = useState(null);

  // Show toast notification
  const showToast = (message, type = 'success') => {
    setToast({ message, type });
    setTimeout(() => setToast(null), 5000);
  };

  // Load children on component mount
  useEffect(() => {
    loadChildren();
  }, []);

  const loadChildren = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await getChildren();
      setChildren(data);
    } catch (err) {
      setError('Failed to load children: ' + err.message);
      showToast('Failed to load children: ' + err.message, 'error');
    } finally {
      setLoading(false);
    }
  };

  const handleAddChild = () => {
    setEditingChild(null);
    setShowForm(true);
  };

  const handleEditChild = (child) => {
    setEditingChild(child);
    setShowForm(true);
  };

  const handleDeleteChild = async (child) => {
    const confirmDelete = window.confirm(
      `Are you sure you want to delete ${child.name}? This action cannot be undone.`
    );

    if (!confirmDelete) {
      return;
    }

    setLoading(true);
    try {
      await deleteChild(child.id);
      await loadChildren();
      showToast(`${child.name} has been deleted successfully`, 'success');
    } catch (err) {
      showToast('Failed to delete child: ' + err.message, 'error');
    } finally {
      setLoading(false);
    }
  };

  const handleSubmitChild = async (childData) => {
    setLoading(true);
    setError(null);

    try {
      if (editingChild) {
        // Update existing child
        await updateChild(editingChild.id, childData);
        showToast(`${childData.name} has been updated successfully`, 'success');
      } else {
        // Create new child
        await createChild(childData);
        showToast(`${childData.name} has been added successfully`, 'success');
      }

      await loadChildren();
      setShowForm(false);
      setEditingChild(null);
    } catch (err) {
      setError(err.message);
      showToast('Failed to save child: ' + err.message, 'error');
    } finally {
      setLoading(false);
    }
  };

  const handleCancelForm = () => {
    setShowForm(false);
    setEditingChild(null);
    setError(null);
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
          <button onClick={() => setToast(null)} className="toast-close">
            ×
          </button>
        </div>
      )}

      {error && (
        <div className="error-banner">
          {error}
          <button onClick={() => setError(null)} className="error-close">
            ×
          </button>
        </div>
      )}

      <div className="page-actions">
        {!showForm && (
          <button onClick={handleAddChild} className="btn btn-primary">
            + Add Child
          </button>
        )}
      </div>

      {showForm && (
        <ChildForm
          child={editingChild}
          onSubmit={handleSubmitChild}
          onCancel={handleCancelForm}
          loading={loading}
        />
      )}

      {!showForm && (
        <ChildList
          children={children}
          onEdit={handleEditChild}
          onDelete={handleDeleteChild}
          loading={loading}
        />
      )}
    </div>
  );
}

export default FamilyManagement;
