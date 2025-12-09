import React, { useState, useEffect } from 'react';
import './ChannelConfig.css';

function ChannelConfig({ channel, onSave, onCancel, onDelete, loading }) {
  const [channelType, setChannelType] = useState('compass');
  const [credentials, setCredentials] = useState({
    username: '',
    password: '',
    base_url: 'https://school-vic.compass.education'
  });
  const [isActive, setIsActive] = useState(true);
  
  useEffect(() => {
    if (channel) {
      setChannelType(channel.channel_type);
      setIsActive(channel.is_active);
      if (channel.config && channel.config.base_url) {
          setCredentials(prev => ({ ...prev, base_url: channel.config.base_url }));
      }
    }
  }, [channel]);

  const handleSubmit = (e) => {
    e.preventDefault();
    const data = {
      channel_type: channelType,
      is_active: isActive,
    };
    
    // Handle credentials for Compass
    if (channelType === 'compass') {
        const hasCreds = credentials.username && credentials.password;
        
        if (!channel && !hasCreds) {
            alert("Username and Password are required for new channel");
            return;
        }
        
        if (hasCreds) {
            data.credentials = {
                username: credentials.username,
                password: credentials.password,
                base_url: credentials.base_url
            };
        } else if (channel) {
            // Updating existing channel without changing creds
            // We might want to update base_url though?
            // If API supports updating config separately...
            // My API implementation: if credentials provided -> validate & update.
            // if config provided -> update config.
            
            // So if user changed base_url but not password, we should send config?
            // But base_url is tied to auth usually.
            
            // For now, if no creds provided during update, we assume config (base_url) update only if changed?
            // Let's simplified: if credentials provided, we send them. 
            // If base_url changed but no creds, we send config?
            
            if (channel.config?.base_url !== credentials.base_url) {
                data.config = { base_url: credentials.base_url };
            }
        }
    }

    onSave(data);
  };

  return (
    <div className="channel-config">
      <h4>{channel ? 'Edit Channel' : 'Add Channel'}</h4>
      
      <form onSubmit={handleSubmit}>
        <div className="form-group">
            <label>Type</label>
            <select value={channelType} onChange={e => setChannelType(e.target.value)} disabled={loading || channel}>
                <option value="compass">Compass</option>
                <option value="other">Other</option>
            </select>
        </div>

        {channelType === 'compass' && (
            <>
                <div className="form-group">
                    <label>Base URL</label>
                    <input 
                        type="url" 
                        value={credentials.base_url} 
                        onChange={e => setCredentials({...credentials, base_url: e.target.value})}
                        required
                        disabled={loading}
                    />
                </div>
                <div className="form-group">
                    <label>Username {channel ? '(leave blank to keep)' : '*'}</label>
                    <input 
                        type="text" 
                        value={credentials.username} 
                        onChange={e => setCredentials({...credentials, username: e.target.value})}
                        required={!channel}
                        disabled={loading}
                    />
                </div>
                <div className="form-group">
                    <label>Password {channel ? '(leave blank to keep)' : '*'}</label>
                    <input 
                        type="password" 
                        value={credentials.password} 
                        onChange={e => setCredentials({...credentials, password: e.target.value})}
                        required={!channel}
                        disabled={loading}
                    />
                </div>
            </>
        )}

        <div className="form-group checkbox">
            <label>
                <input 
                    type="checkbox" 
                    checked={isActive} 
                    onChange={e => setIsActive(e.target.checked)}
                    disabled={loading}
                />
                Active
            </label>
        </div>

        <div className="actions">
            <button type="submit" disabled={loading} className="btn btn-primary">Save</button>
            <button type="button" onClick={onCancel} disabled={loading} className="btn">Cancel</button>
            {channel && onDelete && (
                <button type="button" onClick={() => onDelete(channel.id)} disabled={loading} className="btn btn-delete">
                    Delete
                </button>
            )}
        </div>
      </form>
    </div>
  );
}

export default ChannelConfig;
