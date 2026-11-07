/**
 * REPLICA Identity Component
 * 
 * React component for displaying REPLICA identity, status, and integration
 * with the OpenJarvis frontend
 */

import React, { useState, useEffect } from 'react';

// ============================================================================
// Styles
// ============================================================================

const styles = `
  .replica-container {
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    max-width: 800px;
    margin: 0 auto;
    padding: 20px;
  }

  .replica-header {
    background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
    color: #00d4ff;
    padding: 30px;
    border-radius: 8px;
    border-left: 4px solid #00d4ff;
    margin-bottom: 20px;
    box-shadow: 0 4px 12px rgba(0, 212, 255, 0.2);
  }

  .replica-header h1 {
    margin: 0;
    font-size: 2.5em;
    font-weight: bold;
    text-transform: uppercase;
    letter-spacing: 2px;
  }

  .replica-header p {
    margin: 10px 0 0 0;
    font-size: 1.1em;
    opacity: 0.9;
  }

  .replica-badge {
    display: inline-block;
    background: #00d4ff;
    color: #1a1a2e;
    padding: 4px 12px;
    border-radius: 4px;
    font-weight: bold;
    font-size: 0.85em;
    margin-top: 10px;
  }

  .status-panel {
    background: #f8f9fa;
    border: 1px solid #e0e0e0;
    border-radius: 8px;
    padding: 20px;
    margin-bottom: 20px;
  }

  .status-panel h3 {
    margin: 0 0 15px 0;
    color: #1a1a2e;
    font-size: 1.2em;
    border-bottom: 2px solid #00d4ff;
    padding-bottom: 10px;
  }

  .status-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 15px;
  }

  .status-item {
    background: white;
    padding: 12px;
    border-radius: 4px;
    border-left: 3px solid #00d4ff;
    display: flex;
    justify-content: space-between;
    align-items: center;
  }

  .status-label {
    font-weight: 600;
    color: #333;
    font-size: 0.9em;
  }

  .status-value {
    color: #00d4ff;
    font-weight: bold;
    font-size: 1.1em;
  }

  .status-indicator {
    display: inline-block;
    width: 8px;
    height: 8px;
    border-radius: 50%;
    background: #00d4ff;
    margin-right: 6px;
    animation: pulse 2s infinite;
  }

  @keyframes pulse {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.5; }
  }

  .specialties-section {
    background: #f8f9fa;
    border: 1px solid #e0e0e0;
    border-radius: 8px;
    padding: 20px;
    margin-bottom: 20px;
  }

  .specialties-section h3 {
    margin: 0 0 15px 0;
    color: #1a1a2e;
    font-size: 1.2em;
    border-bottom: 2px solid #00d4ff;
    padding-bottom: 10px;
  }

  .specialties-list {
    display: flex;
    flex-wrap: wrap;
    gap: 10px;
  }

  .specialty-tag {
    background: #00d4ff;
    color: #1a1a2e;
    padding: 6px 12px;
    border-radius: 20px;
    font-size: 0.9em;
    font-weight: 500;
  }

  .lore-section {
    background: #f8f9fa;
    border: 1px solid #e0e0e0;
    border-radius: 8px;
    padding: 20px;
    margin-bottom: 20px;
    border-left: 4px solid #00d4ff;
  }

  .lore-section h3 {
    margin: 0 0 15px 0;
    color: #1a1a2e;
    font-size: 1.2em;
  }

  .lore-text {
    color: #555;
    line-height: 1.6;
    font-size: 0.95em;
  }

  .loading {
    text-align: center;
    padding: 40px;
    color: #666;
  }

  .error {
    background: #fee;
    border: 1px solid #f99;
    color: #c33;
    padding: 15px;
    border-radius: 4px;
    margin-bottom: 20px;
  }

  .greeting-message {
    background: #e8f4f8;
    border-left: 4px solid #00d4ff;
    padding: 20px;
    border-radius: 4px;
    margin-bottom: 20px;
    font-style: italic;
    color: #1a1a2e;
    line-height: 1.6;
  }
`;

// ============================================================================
// Component
// ============================================================================

export function ReplicaIdentity({ baseUrl = 'http://127.0.0.1:8000' }) {
  const [replica, setReplica] = useState(null);
  const [status, setStatus] = useState(null);
  const [greeting, setGreeting] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        setError(null);
        
        // Fetch REPLICA info
        const infoRes = await fetch(`${baseUrl}/v1/replica/info`);
        if (!infoRes.ok) throw new Error('Failed to fetch REPLICA info');
        const replicaData = await infoRes.json();
        setReplica(replicaData);

        // Fetch REPLICA status
        const statusRes = await fetch(`${baseUrl}/v1/replica/status`);
        if (!statusRes.ok) throw new Error('Failed to fetch REPLICA status');
        const statusData = await statusRes.json();
        setStatus(statusData);

        // Fetch REPLICA greeting
        const greetingRes = await fetch(`${baseUrl}/v1/replica/greeting`, {
          method: 'POST'
        });
        if (!greetingRes.ok) throw new Error('Failed to fetch REPLICA greeting');
        const greetingData = await greetingRes.json();
        setGreeting(greetingData);

        setLoading(false);
      } catch (err) {
        setError(err.message);
        setLoading(false);
      }
    };

    fetchData();

    // Update status every 5 seconds
    const statusInterval = setInterval(async () => {
      try {
        const statusRes = await fetch(`${baseUrl}/v1/replica/status`);
        if (statusRes.ok) {
          const statusData = await statusRes.json();
          setStatus(statusData);
        }
      } catch (err) {
        // Silently fail on status updates
      }
    }, 5000);

    return () => clearInterval(statusInterval);
  }, [baseUrl]);

  if (loading) {
    return <div className="loading">Carregando REPLICA...</div>;
  }

  if (error) {
    return <div className="error">Erro: {error}</div>;
  }

  if (!replica || !status) {
    return <div className="loading">Inicializando REPLICA...</div>;
  }

  return (
    <div className="replica-container">
      <style>{styles}</style>

      {/* Header */}
      <div className="replica-header">
        <h1>{replica.name}</h1>
        <p>{replica.type}</p>
        <span className="replica-badge">{replica.status.toUpperCase()}</span>
      </div>

      {/* Greeting */}
      {greeting && (
        <div className="greeting-message">
          {greeting.message}
        </div>
      )}

      {/* Status Panel */}
      <div className="status-panel">
        <h3>Operational Status</h3>
        <div className="status-grid">
          <div className="status-item">
            <span className="status-label">Mode</span>
            <span className="status-value">
              <span className="status-indicator"></span>
              {status.operational_mode}
            </span>
          </div>
          <div className="status-item">
            <span className="status-label">Agents Active</span>
            <span className="status-value">
              {status.agents_active}/{status.agents_total}
            </span>
          </div>
          <div className="status-item">
            <span className="status-label">Memory</span>
            <span className="status-value">{status.memory_backend}</span>
          </div>
          <div className="status-item">
            <span className="status-label">Memory Status</span>
            <span className="status-value">
              <span className="status-indicator"></span>
              {status.memory_status}
            </span>
          </div>
          <div className="status-item">
            <span className="status-label">Routing</span>
            <span className="status-value">
              <span className="status-indicator"></span>
              {status.routing_status}
            </span>
          </div>
          <div className="status-item">
            <span className="status-label">Repositories</span>
            <span className="status-value">{replica.repositories_count}</span>
          </div>
        </div>
      </div>

      {/* Specialties */}
      <div className="specialties-section">
        <h3>Specialties</h3>
        <div className="specialties-list">
          {replica.specialties.map((specialty, i) => (
            <span key={i} className="specialty-tag">
              {specialty}
            </span>
          ))}
        </div>
      </div>

      {/* Lore */}
      <div className="lore-section">
        <h3>Identity & Lore</h3>
        <div className="lore-text">
          <p><strong>Origin:</strong> {replica.origin}</p>
          <p><strong>Version:</strong> {replica.version}</p>
          <p><strong>About:</strong></p>
          <p>{replica.lore}</p>
        </div>
      </div>
    </div>
  );
}

// ============================================================================
// Standalone App (for testing)
// ============================================================================

export default function App() {
  return (
    <div style={{ backgroundColor: '#f5f5f5', minHeight: '100vh', padding: '20px 0' }}>
      <ReplicaIdentity />
    </div>
  );
}
