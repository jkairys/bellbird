import React, { useState, useEffect } from 'react';
import './ChildForm.css';

function ChildForm({ child, onSubmit, onCancel, loading, availableOrganisations, onAddOrg, onRemoveOrg }) {
  const [formData, setFormData] = useState({
    name: '',
    date_of_birth: '',
    gender: '',
    interests: '',
  });

  const [errors, setErrors] = useState({});
  const [selectedOrgId, setSelectedOrgId] = useState(''); // State for selected org to add

  // Populate form when editing
  useEffect(() => {
    if (child) {
      setFormData({
        name: child.name || '',
        date_of_birth: child.date_of_birth || '',
        gender: child.gender || '',
        interests: child.interests || '',
      });
    } else {
      // Reset form for new child
      setFormData({
        name: '',
        date_of_birth: '',
        gender: '',
        interests: '',
      });
    }
    setErrors({});
  }, [child]);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: value,
    }));

    // Clear error for this field when user starts typing
    if (errors[name]) {
      setErrors((prev) => ({
        ...prev,
        [name]: null,
      }));
    }
  };

  const validate = () => {
    const newErrors = {};

    if (!formData.name.trim()) {
      newErrors.name = 'Name is required';
    }

    if (!formData.date_of_birth) {
      newErrors.date_of_birth = 'Date of birth is required';
    } else {
      // Check if date is in the future
      const birthDate = new Date(formData.date_of_birth);
      const today = new Date();
      today.setHours(0, 0, 0, 0);

      if (birthDate > today) {
        newErrors.date_of_birth = 'Date of birth cannot be in the future';
      }
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!validate()) {
      return;
    }

    // Clean up data before submission
    const submitData = {
      name: formData.name.trim(),
      date_of_birth: formData.date_of_birth,
      gender: formData.gender.trim() || null,
      interests: formData.interests.trim() || null,
    };

    // Remove null/empty values
    Object.keys(submitData).forEach((key) => {
      if (submitData[key] === null || submitData[key] === '') {
        delete submitData[key];
      }
    });

    onSubmit(submitData);
  };

  const handleAddOrgSubmit = (e) => {
      e.preventDefault();
      if (selectedOrgId && onAddOrg) {
          onAddOrg(selectedOrgId);
          setSelectedOrgId('');
      }
  };

  const filteredOrgs = availableOrganisations 
      ? availableOrganisations.filter(org => 
          !child?.organisations?.some(childOrg => childOrg.id === org.id)
        )
      : [];

  return (
    <div className="child-form-container">
      <h2>{child ? 'Edit Child' : 'Add Child'}</h2>

      <form onSubmit={handleSubmit} className="child-form">
        <div className="form-group">
          <label htmlFor="name">
            Name <span className="required">*</span>
          </label>
          <input
            type="text"
            id="name"
            name="name"
            value={formData.name}
            onChange={handleChange}
            className={errors.name ? 'error' : ''}
            placeholder="Enter child's full name"
            disabled={loading}
          />
          {errors.name && <span className="error-message">{errors.name}</span>}
        </div>

        <div className="form-group">
          <label htmlFor="date_of_birth">
            Date of Birth <span className="required">*</span>
          </label>
          <input
            type="date"
            id="date_of_birth"
            name="date_of_birth"
            value={formData.date_of_birth}
            onChange={handleChange}
            className={errors.date_of_birth ? 'error' : ''}
            disabled={loading}
          />
          {errors.date_of_birth && <span className="error-message">{errors.date_of_birth}</span>}
        </div>

        <div className="form-group">
          <label htmlFor="gender">Gender (optional)</label>
          <input
            type="text"
            id="gender"
            name="gender"
            value={formData.gender}
            onChange={handleChange}
            placeholder="e.g., male, female, non-binary"
            disabled={loading}
          />
        </div>

        <div className="form-group">
          <label htmlFor="interests">Interests (optional)</label>
          <textarea
            id="interests"
            name="interests"
            value={formData.interests}
            onChange={handleChange}
            placeholder="e.g., Soccer, reading, science experiments"
            rows="4"
            disabled={loading}
          />
        </div>

        <div className="form-actions">
          <button type="button" onClick={onCancel} className="btn btn-cancel" disabled={loading}>
            Cancel
          </button>
          <button type="submit" className="btn btn-primary" disabled={loading}>
            {loading ? 'Saving...' : child ? 'Update' : 'Add Child'}
          </button>
        </div>
      </form>

      {child && (
          <div className="child-organisations-section">
              <h3>Organisations</h3>
              
              {child.organisations && child.organisations.length > 0 ? (
                  <ul className="associated-orgs">
                      {child.organisations.map(org => (
                          <li key={org.id}>
                              {org.name} ({org.type})
                              <button type="button" onClick={() => onRemoveOrg(org.id)} disabled={loading}>Remove</button>
                          </li>
                      ))}
                  </ul>
              ) : (
                  <p>No organisations associated.</p>
              )}

              <div className="add-org-control">
                  <select 
                      value={selectedOrgId} 
                      onChange={(e) => setSelectedOrgId(e.target.value)}
                      disabled={loading}
                  >
                      <option value="">Select Organisation...</option>
                      {filteredOrgs.map(org => (
                          <option key={org.id} value={org.id}>{org.name}</option>
                      ))}
                  </select>
                  <button 
                      type="button" 
                      onClick={handleAddOrgSubmit} 
                      disabled={!selectedOrgId || loading}
                  >
                      Add
                  </button>
              </div>
          </div>
      )}
    </div>
  );
}

export default ChildForm;