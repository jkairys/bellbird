/**
 * ChildList component - Displays all children with edit/delete buttons.
 */

import React from 'react';
import './ChildList.css';

function ChildList({ children, onEdit, onDelete, loading }) {
  if (loading) {
    return <div className="child-list-loading">Loading children...</div>;
  }

  if (!children || children.length === 0) {
    return (
      <div className="child-list-empty">
        <p>No children added yet.</p>
        <p>Click "Add Child" to create your first child profile.</p>
      </div>
    );
  }

  const formatDate = (dateString) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
    });
  };

  const calculateAge = (dateOfBirth) => {
    const today = new Date();
    const birthDate = new Date(dateOfBirth);
    let age = today.getFullYear() - birthDate.getFullYear();
    const monthDiff = today.getMonth() - birthDate.getMonth();

    if (monthDiff < 0 || (monthDiff === 0 && today.getDate() < birthDate.getDate())) {
      age--;
    }

    return age;
  };

  return (
    <div className="child-list">
      <h2>Your Children</h2>
      <div className="child-cards">
        {children.map((child) => (
          <div key={child.id} className="child-card">
            <div className="child-card-header">
              <h3>{child.name}</h3>
              <span className="child-age">{calculateAge(child.date_of_birth)} years old</span>
            </div>

            <div className="child-card-body">
              <div className="child-info">
                <label>Date of Birth:</label>
                <span>{formatDate(child.date_of_birth)}</span>
              </div>

              {child.gender && (
                <div className="child-info">
                  <label>Gender:</label>
                  <span>{child.gender}</span>
                </div>
              )}

              {child.interests && (
                <div className="child-info">
                  <label>Interests:</label>
                  <span>{child.interests}</span>
                </div>
              )}

              {child.organisations && child.organisations.length > 0 && (
                <div className="child-info">
                  <label>Organisations:</label>
                  <div className="org-badges">
                    {child.organisations.map(org => (
                      <span key={org.id} className="org-badge">{org.name}</span>
                    ))}
                  </div>
                </div>
              )}
            </div>

            <div className="child-card-actions">
              <button
                onClick={() => onEdit(child)}
                className="btn btn-edit"
                aria-label={`Edit ${child.name}`}
              >
                Edit
              </button>
              <button
                onClick={() => onDelete(child)}
                className="btn btn-delete"
                aria-label={`Delete ${child.name}`}
              >
                Delete
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

export default ChildList;
