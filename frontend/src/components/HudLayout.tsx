import { useState, useEffect } from 'react';
import { Outlet } from 'react-router';
import { useScrapperStore } from '../lib/scrapperStore';
import { ChevronRight, Code2, GitBranch, Zap, Brain } from 'lucide-react';

// 71 agentes ECC mockados
const AGENTS_ECC = [
  { name: 'Code Analyzer', icon: 'code', status: 'online' },
  { name: 'Review Master', icon: 'review', status: 'online' },
  { name: 'Build Runner', icon: 'build', status: 'online' },
  { name: 'Architect Planner', icon: 'architect', status: 'idle' },
  { name: 'Security Scanner', icon: 'code', status: 'online' },
  { name: 'Performance Monitor', icon: 'build', status: 'online' },
  { name: 'Documentation Gen', icon: 'code', status: 'idle' },
  { name: 'Unit Test Runner', icon: 'review', status: 'online' },
  { name: 'Integration Tester', icon: 'build', status: 'online' },
  { name: 'API Analyzer', icon: 'code', status: 'idle' },
  { name: 'Database Optimizer', icon: 'architect', status: 'online' },
  { name: 'Cache Manager', icon: 'build', status: 'online' },
  { name: 'Deploy Assistant', icon: 'review', status: 'online' },
  { name: 'Log Analyzer', icon: 'code', status: 'idle' },
  { name: 'Metric Collector', icon: 'build', status: 'online' },
  { name: 'Dependency Checker', icon: 'code', status: 'online' },
  { name: 'Version Controller', icon: 'review', status: 'online' },
  { name: 'Config Validator', icon: 'architect', status: 'idle' },
  { name: 'Schema Analyzer', icon: 'code', status: 'online' },
  { name: 'Type Checker', icon: 'build', status: 'online' },
  { name: 'Linter Master', icon: 'review', status: 'online' },
  { name: 'Formatter Agent', icon: 'code', status: 'idle' },
  { name: 'Testing Framework', icon: 'architect', status: 'online' },
  { name: 'Debugger Pro', icon: 'code', status: 'online' },
  { name: 'Profiler Elite', icon: 'build', status: 'online' },
  { name: 'Memory Tracker', icon: 'review', status: 'idle' },
  { name: 'Thread Analyzer', icon: 'code', status: 'online' },
  { name: 'Network Monitor', icon: 'architect', status: 'online' },
  { name: 'API Gateway', icon: 'build', status: 'online' },
  { name: 'Queue Manager', icon: 'review', status: 'idle' },
  { name: 'Cache Warmer', icon: 'code', status: 'online' },
  { name: 'Load Balancer', icon: 'architect', status: 'online' },
  { name: 'CDN Optimizer', icon: 'code', status: 'online' },
  { name: 'DDoS Protector', icon: 'build', status: 'idle' },
  { name: 'Rate Limiter', icon: 'review', status: 'online' },
  { name: 'Auth Manager', icon: 'code', status: 'online' },
  { name: 'Token Validator', icon: 'architect', status: 'online' },
  { name: 'Permission Check', icon: 'build', status: 'idle' },
  { name: 'Audit Logger', icon: 'code', status: 'online' },
  { name: 'Event Stream', icon: 'review', status: 'online' },
  { name: 'Webhook Handler', icon: 'architect', status: 'online' },
  { name: 'Message Queue', icon: 'code', status: 'idle' },
  { name: 'Task Scheduler', icon: 'build', status: 'online' },
  { name: 'Cron Manager', icon: 'review', status: 'online' },
  { name: 'Data Pipeline', icon: 'code', status: 'online' },
  { name: 'ETL Runner', icon: 'architect', status: 'idle' },
  { name: 'Stream Processor', icon: 'build', status: 'online' },
  { name: 'Batch Worker', icon: 'code', status: 'online' },
  { name: 'Job Dispatcher', icon: 'review', status: 'online' },
  { name: 'Backup System', icon: 'architect', status: 'idle' },
  { name: 'Restore Handler', icon: 'code', status: 'online' },
  { name: 'Snapshot Creator', icon: 'build', status: 'online' },
  { name: 'Replication Sync', icon: 'review', status: 'online' },
  { name: 'Failover Agent', icon: 'code', status: 'idle' },
  { name: 'Health Checker', icon: 'architect', status: 'online' },
  { name: 'Alert Manager', icon: 'build', status: 'online' },
  { name: 'Notification Hub', icon: 'review', status: 'online' },
  { name: 'Analytics Engine', icon: 'code', status: 'idle' },
  { name: 'Metrics Exporter', icon: 'architect', status: 'online' },
  { name: 'Trace Collector', icon: 'build', status: 'online' },
  { name: 'Log Aggregator', icon: 'review', status: 'online' },
  { name: 'Search Indexer', icon: 'code', status: 'idle' },
  { name: 'Query Optimizer', icon: 'architect', status: 'online' },
  { name: 'Cache Warmer Pro', icon: 'build', status: 'online' },
  { name: 'Serializer', icon: 'review', status: 'online' },
  { name: 'Encoder/Decoder', icon: 'code', status: 'idle' },
  { name: 'Compressor', icon: 'architect', status: 'online' },
  { name: 'Encryptor', icon: 'build', status: 'online' },
  { name: 'PKI Manager', icon: 'review', status: 'online' },
  { name: 'Certificate Handler', icon: 'code', status: 'idle' },
];

const getIcon = (iconType: string) => {
  const iconProps = { size: 14, strokeWidth: 1.5 };
  switch (iconType) {
    case 'code': return <Code2 {...iconProps} />;
    case 'review': return <GitBranch {...iconProps} />;
    case 'build': return <Zap {...iconProps} />;
    case 'architect': return <Brain {...iconProps} />;
    default: return <Code2 {...iconProps} />;
  }
};

export function HudLayout() {
  const [selectedAgent, setSelectedAgent] = useState<string | null>(null);
  const tasks = useScrapperStore((s) => s.tasks);
  const activeTasks = tasks.filter((t) => t.status === 'running');

  useEffect(() => {
    // Simular scrapers em background
    if (Math.random() > 0.95) {
      const mockTasks = [
        { name: 'Scanning repositories...', id: 'scan-1' },
        { name: 'Analyzing code patterns...', id: 'scan-2' },
        { name: 'Running REA engine...', id: 'scan-3' },
      ];
      mockTasks.forEach((t) => {
        if (Math.random() > 0.7) {
          // Occasionally show scraper activity
        }
      });
    }
  }, []);

  return (
    <div className="hud-container">
      {/* Sidebar HUD */}
      <aside className="hud-sidebar">
        <div className="hud-logo">
          <span className="hud-logo-text">JARVIS</span>
          <span className="hud-logo-subtitle">v3.14</span>
        </div>

        {/* Agents List */}
        <div className="hud-agents-section">
          <div className="hud-section-header">
            <span>AGENTS</span>
            <span className="hud-agent-count">{AGENTS_ECC.length}</span>
          </div>
          <div className="hud-agents-list">
            {AGENTS_ECC.map((agent, idx) => (
              <button
                key={idx}
                className={`hud-agent-item ${selectedAgent === agent.name ? 'active' : ''} ${
                  agent.status === 'online' ? 'online' : 'idle'
                }`}
                onClick={() => setSelectedAgent(agent.name)}
              >
                <div className="hud-agent-icon">{getIcon(agent.icon)}</div>
                <div className="hud-agent-info">
                  <div className="hud-agent-name">{agent.name}</div>
                  <div className={`hud-agent-status ${agent.status}`}>
                    <span className="hud-status-dot" />
                    {agent.status}
                  </div>
                </div>
                <ChevronRight size={12} />
              </button>
            ))}
          </div>
        </div>

        {/* Scraper Activity */}
        {activeTasks.length > 0 && (
          <div className="hud-activity-section">
            <div className="hud-section-header">SCRAPERS</div>
            <div className="hud-activity-list">
              {activeTasks.map((task) => (
                <div key={task.id} className="hud-activity-item">
                  <div className="hud-activity-name">{task.message}</div>
                  <div className="hud-progress-bar">
                    <div
                      className="hud-progress-fill"
                      style={{ width: `${task.progress}%` }}
                    />
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </aside>

      {/* Main Content Area */}
      <main className="hud-main">
        <div className="hud-chat-container">
          <Outlet />
        </div>
      </main>
    </div>
  );
}
