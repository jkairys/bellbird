import React, { useState } from 'react';

function OrganisationList({ organisations, onEdit, onDelete, onFilter, loading }) {
  const [typeFilter, setTypeFilter] = useState('');

  const orgTypes = [
    { value: '', label: 'All Types' },
    { value: 'school', label: 'School' },
    { value: 'daycare', label: 'Daycare' },
    { value: 'kindergarten', label: 'Kindergarten' },
    { value: 'sports_team', label: 'Sports Team' },
    { value: 'other', label: 'Other' }
  ];

  const handleFilterChange = (e) => {
    const newVal = e.target.value;
    setTypeFilter(newVal);
    onFilter(newVal);
  };

  if (loading && (!organisations || organisations.length === 0)) return <div>Loading organisations...</div>;

  return (
    <div className="organisation-list">
      <h3>Organisations</h3>
      
      <div className="filter-controls">
        <select 
          value={typeFilter} 
          onChange={handleFilterChange}
        >
          {orgTypes.map(t => (
            <option key={t.value} value={t.value}>{t.label}</option>
          ))}
        </select>
      </div>

      {(!organisations || organisations.length === 0) ? (
        <p>No organisations found.</p>
      ) : (
        <ul>
          {organisations.map(org => (
            <li key={org.id} className="organisation-item">
              <div>
                <strong>{org.name}</strong> ({org.type})
                {org.address && <div>{org.address}</div>}
                {(!org.channels || !org.channels.some(c => c.is_active)) && (
                    <div style={{marginTop: '5px'}}>
                        <span style={{
                            backgroundColor: '#fff3cd', 
                            color: '#856404', 
                            padding: '2px 6px', 
                            borderRadius: '4px', 
                            fontSize: '0.8rem'
                        }}>
                            Needs Setup
                        </span>
                    </div>
                )}
              </div>
              <div className="actions">
                <button onClick={() => onEdit(org)}>Edit</button>
                <button onClick={() => onDelete(org)}>Delete</button>
              </div>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}

export default OrganisationList;