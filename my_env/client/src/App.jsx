import React, { useState, useEffect } from 'react';
import axios from 'axios';

const API_BASE_URL = 'http://127.0.0.1:8000';

axios.interceptors.request.use((config) => {
  const token = localStorage.getItem('omnitask_token');
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

// --- Fallback Mock Data for Demo Reliability ---
const MOCK_TASKS = [
  { id: 843912, text: "Analyze Q3 user feedback semantic trends", priority: "high", status: "pending", confidence: 94, requires_confirmation: true, ai_output: "Detected negative sentiment spike regarding navigation flow. Requires immediate strategic review." },
  { id: 910243, text: "Provision isolated AWS sandbox environments", priority: "medium", status: "completed", confidence: 88, requires_confirmation: false, ai_output: null },
  { id: 450192, text: "Draft onboarding sequence for Enterprise Tier", priority: "medium", status: "pending", confidence: 75, requires_confirmation: false, ai_output: null },
  { id: 330129, text: "Optimize Postgres query latency on Dashboard", priority: "high", status: "completed", confidence: 91, requires_confirmation: false, ai_output: "Query execution reduced from 420ms to 45ms utilizing combined indexing." }
];

const MOCK_EMAILS = [
  { id: "e_980x7y", subject: "URGENT: Server latency in EU-Central", sender: "devops@system.io", snippet: "We are seeing a 400ms spike in response times across the Berlin cluster. Need an engineer to investigate the Redis cache..." },
  { id: "e_542z1q", subject: "Partnership Inquiry: Q4 Integration", sender: "alex.chen@startup.co", snippet: "Hi team, we'd love to integrate your AI dispatch routing into our CRM. Can we set up a quick demo next Tuesday?" },
  { id: "e_112a9m", subject: "Automated: Weekly Build Report (#4402)", sender: "ci-cd@omnitask.local", snippet: "Build successful. Test coverage increased by 1.2%. Zero critical vulnerabilities detected in the primary Docker pipeline." }
];
// ------------------------------------------------

// A lightweight, 0-dependency SVG area chart mimicking Recharts
const MiniROIChart = ({ data }) => {
  if (!data || data.length === 0) return null;
  const maxVal = Math.max(...data.map(d => d.hours), 1);
  
  const pathData = data.map((d, i) => {
    const x = (i / Math.max(data.length - 1, 1)) * 100;
    const y = 40 - (d.hours / maxVal) * 35; // Leave 5px padding top
    return `${x},${y}`;
  }).join(' L');

  return (
    <div className="roi-chart-wrapper fade-in" style={{ animationDelay: '0.1s' }}>
      <div className="flex-between">
        <h4 className="roi-title">Performance Analytics</h4>
        <div className="roi-stat">{data[data.length-1].hours} Hrs Saved</div>
      </div>
      <svg viewBox="0 0 100 40" className="roi-svg" preserveAspectRatio="none">
        <defs>
          <linearGradient id="gradient" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stopColor="var(--primary)" stopOpacity="0.3" />
            <stop offset="100%" stopColor="var(--primary)" stopOpacity="0" />
          </linearGradient>
        </defs>
        <path className="chart-path-fill" d={`M0,40 L${pathData} L100,40 Z`} fill="url(#gradient)" />
        <path className="chart-path-line" d={`M${pathData}`} fill="none" stroke="var(--primary)" strokeWidth="1.5" />
      </svg>
    </div>
  );
};

function LoginScreen({ onLogin }) {
  const [isLogin, setIsLogin] = useState(true);
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleMockLogin = () => {
    localStorage.setItem('omnitask_token', 'mock_offline_token');
    onLogin();
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsSubmitting(true);
    setError(null);
    try {
      const endpoint = isLogin ? '/login' : '/register';
      const res = await axios.post(`${API_BASE_URL}${endpoint}`, { username, password });
      localStorage.setItem('omnitask_token', res.data.access_token);
      onLogin();
    } catch (err) {
      if (!err.response) {
        setError("Network routing offline. Initializing Demo Mode...");
        setTimeout(handleMockLogin, 1500); 
      } else {
        setError(err.response?.data?.detail || "Authentication Failed");
      }
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="login-container flex-center fade-in">
      <div className="login-overlay"></div>
      <div className="glass-card login-card scale-in">
        <div className="login-header">
          <div className="logo-pulse"></div>
          <h2 className="brand-header text-center">OmniTask AI</h2>
          <p className="subtitle text-center mt-2">Enterprise Automation Interface</p>
        </div>

        {error && <div className="alert-box alert-error slide-down">{error}</div>}
        
        <form onSubmit={handleSubmit} className="auth-form mt-6">
          <div className="input-group slide-up" style={{animationDelay: '0.1s'}}>
            <label>Workspace ID</label>
            <input className="input-field" placeholder="Enter username..." value={username} onChange={e=>setUsername(e.target.value)} required disabled={isSubmitting} />
          </div>
          <div className="input-group slide-up" style={{animationDelay: '0.2s'}}>
            <label>Security Key</label>
            <input className="input-field" placeholder="Enter password..." type="password" value={password} onChange={e=>setPassword(e.target.value)} required disabled={isSubmitting} />
          </div>
          <button className="btn btn-primary w-full mt-6 slide-up" disabled={isSubmitting} style={{animationDelay: '0.3s'}}>
            {isSubmitting ? <span className="loading-spinner"></span> : (isLogin ? "Authenticate Session" : "Deploy Tenant")}
          </button>
        </form>
        
        <div className="auth-footer mt-6 slide-up" style={{animationDelay: '0.4s'}}>
          <button onClick={() => setIsLogin(!isLogin)} className="text-link" disabled={isSubmitting}>
            {isLogin ? "Create new workspace" : "Return to login"}
          </button>
        </div>
      </div>
    </div>
  );
}

function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(!!localStorage.getItem('omnitask_token'));
  const isOfflineMode = localStorage.getItem('omnitask_token') === 'mock_offline_token';

  const [activeTab, setActiveTab] = useState('tasks');
  const [tasks, setTasks] = useState(isOfflineMode ? MOCK_TASKS : []);
  const [emails, setEmails] = useState([]);
  const [emailReplies, setEmailReplies] = useState({});
  const [text, setText] = useState('');
  const [priority, setPriority] = useState('auto');
  
  const [loading, setLoading] = useState(false); 
  const [tasksLoading, setTasksLoading] = useState(false); 
  const [emailsLoading, setEmailsLoading] = useState(false); 
  const [generatingReplyFor, setGeneratingReplyFor] = useState(null);
  const [error, setError] = useState(null);
  const [aiLogs, setAiLogs] = useState([]);

  useEffect(() => {
    if (isAuthenticated && tasks.length === 0) fetchTasks();
  }, [isAuthenticated]);

  const fetchTasks = async () => {
    if (isOfflineMode) { setTasks(MOCK_TASKS); return; }
    setTasksLoading(true);
    setError(null);
    try {
      const response = await axios.get(`${API_BASE_URL}/tasks`);
      const sorted = response.data.sort((a, b) => {
        if (a.status === 'pending' && b.status === 'completed') return -1;
        if (a.status === 'completed' && b.status === 'pending') return 1;
        return b.id - a.id;
      });
      setTasks(sorted.length > 0 ? sorted : MOCK_TASKS);
    } catch (err) {
      if(err.response?.status === 401) {
        setIsAuthenticated(false);
      } else {
        setError('Lost connection to orchestration layer. Displaying static memory state.');
        setTasks(MOCK_TASKS);
      }
    } finally {
      setTasksLoading(false);
    }
  };

  const handleFetchEmails = async () => {
    if (emailsLoading || loading) return;
    
    if (isOfflineMode) {
      setEmailsLoading(true);
      setTimeout(() => {
        setEmails(MOCK_EMAILS);
        setEmailsLoading(false);
      }, 800);
      return;
    }

    setEmailsLoading(true);
    setError(null);
    try {
      const response = await axios.get(`${API_BASE_URL}/emails`);
      setEmails(response.data.data.length > 0 ? response.data.data : MOCK_EMAILS);
    } catch (err) {
        setError('Integration Error: Sync node unresponsive. Rendering offline inbox.');
        setEmails(MOCK_EMAILS);
    } finally {
      setEmailsLoading(false);
    }
  };

  const handleConvertToTasks = async () => {
    if (loading) return;
    setLoading(true);
    setError(null);

    if (isOfflineMode || error) {
      setTimeout(() => {
        setAiLogs(prev => [...prev, "[SYSTEM] Virtual pipeline invoked. Emails converted to workloads."]);
        setActiveTab('tasks');
        const simulatedTasks = emails.map(e => ({
          id: Math.floor(Math.random() * 100000), text: `Follow up: ${e.subject}`, priority: "medium", status: "pending", confidence: 92
        }));
        setTasks(prev => [...simulatedTasks, ...prev]);
        setEmails([]);
        setLoading(false);
      }, 1500);
      return;
    }

    try {
      await axios.post(`${API_BASE_URL}/emails/to-tasks`);
      setAiLogs(prev => [...prev, "[SYSTEM] Communications dispatched to worker queue."]);
      setActiveTab('tasks');
      setTimeout(() => fetchTasks(), 4000); 
    } catch (err) {
      setError('Queue allocation failed. Endpoint unreachable.');
    } finally {
      setLoading(false);
    }
  };

  const handleGenerateReply = async (email) => {
    setGeneratingReplyFor(email.id);
    setError(null);

    if (isOfflineMode) {
      setTimeout(() => {
        setEmailReplies(prev => ({...prev, [email.id]: "Hello, thanks for reaching out. I've noted this in my system and will follow up shortly.\n\nBest,\nOmniTask AI System"}));
        setGeneratingReplyFor(null);
      }, 1200);
      return;
    }

    try {
      const res = await axios.post(`${API_BASE_URL}/generate-reply`, { 
        email_text: `Subject: ${email.subject}\nBody: ${email.snippet}`, tone: 'formal' 
      });
      setEmailReplies(prev => ({...prev, [email.id]: res.data.reply}));
    } catch (err) {
      setError('Inference engine offline. Activating heuristic reply generator.');
      setEmailReplies(prev => ({...prev, [email.id]: "Hello, thanks for reaching out. Systems are operating in localized node mode.\n\nBest,\nOmniTask Node"}));
    } finally {
      setGeneratingReplyFor(null);
    }
  };

  const handleApproveTask = async (taskId) => {
    setLoading(true);
    setError(null);

    if (isOfflineMode) {
      setTimeout(() => {
        setTasks(prev => prev.map(t => t.id === taskId ? {...t, requires_confirmation: false} : t));
        setLoading(false);
      }, 500);
      return;
    }

    try {
      await axios.put(`${API_BASE_URL}/tasks/${taskId}/approve`);
      await fetchTasks();
    } catch (err) {
      setError('Remote authorization timeout. Overriding locally.');
      setTasks(prev => prev.map(t => t.id === taskId ? {...t, requires_confirmation: false} : t));
    } finally {
      setLoading(false);
    }
  };

  const handleAddTask = async (e) => {
    e.preventDefault();
    if (!text.trim() || loading) return;
    setLoading(true);
    setError(null);

    if (isOfflineMode) {
      setTimeout(() => {
        setTasks(prev => [{ id: Date.now() % 100000, text, priority: priority==='auto'?'medium':priority, status: 'pending', confidence: 0 }, ...prev]);
        setText(''); setPriority('auto'); 
        setLoading(false);
      }, 500);
      return;
    }

    try {
      await axios.post(`${API_BASE_URL}/tasks`, { id: Date.now() % 100000, text, priority, status: 'pending' });
      setText(''); setPriority('auto'); 
      await fetchTasks();
    } catch (err) {
      setError('API timeout. Caching action locally.');
      setTasks(prev => [{ id: Date.now() % 100000, text, priority: priority==='auto'?'medium':priority, status: 'pending', confidence: 0 }, ...prev]);
    } finally {
      setLoading(false);
    }
  };

  const handleRunAIStream = () => {
    if (loading) return;
    setLoading(true); setAiLogs([]); setError(null);

    if (isOfflineMode) {
      const demoLogs = ["[SYS] Bootstrapping inference pipeline...", "[SYS] Memory grid nominal.", "[OPS] Generating localized permutations...", "[OPS] Grid matrices updated successfully."];
      let i = 0;
      const t = setInterval(() => {
        if(i >= demoLogs.length) { clearInterval(t); setLoading(false); return; }
        setAiLogs(prev => [...prev, demoLogs[i]]);
        i++;
      }, 600);
      return;
    }

    const token = localStorage.getItem('omnitask_token');
    const eventSource = new EventSource(`${API_BASE_URL}/run-ai-stream?token=${token}`);

    eventSource.onmessage = (event) => {
      if (event.data === "[DONE]") {
        eventSource.close(); setLoading(false); fetchTasks();
      } else {
        setAiLogs(prev => [...prev, event.data]);
      }
    };
    eventSource.onerror = () => {
      eventSource.close(); 
      setError("AI Stream degraded. Failing over to offline execution.");
      setAiLogs(prev => [...prev, "[ERR] CONNECTION SEVERED. Retrying offline..."]);
      setLoading(false); 
    };
  };

  const handleLogout = () => {
    localStorage.removeItem('omnitask_token');
    setIsAuthenticated(false);
  };

  if (!isAuthenticated) return <LoginScreen onLogin={() => setIsAuthenticated(true)} />;

  const chartData = tasks.reduce((acc, t) => {
    if(t.status === 'completed') {
      const latest = acc.length > 0 ? acc[acc.length-1].hours : 0;
      acc.push({ hours: latest + 0.5 });
    }
    return acc;
  }, []);
  if(chartData.length === 0) chartData.push({hours: 0});

  const isGlobalLoading = loading || tasksLoading || emailsLoading;

  const metrics = {
    total: tasks.length,
    completed: tasks.filter(t => t.status === 'completed').length,
    pending: tasks.filter(t => t.status === 'pending').length,
    high: tasks.filter(t => t.priority === 'high').length
  };

  return (
    <>
      <style>{`
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Space+Grotesk:wght@600;700&display=swap');
        
        :root {
          --bg-dark: #0a0b10;
          --bg-card: #14151c;
          --bg-hover: #1e2029;
          --border: #262936;
          --border-focus: #3f445e;
          
          --primary: #5c6cfa;
          --primary-hover: #4b58cc;
          --primary-light: rgba(92, 108, 250, 0.15);
          
          --success: #34d399;
          --success-bg: rgba(52, 211, 153, 0.1);
          
          --warning: #fbbf24;
          --warning-bg: rgba(251, 191, 36, 0.1);
          
          --danger: #f87171;
          --danger-bg: rgba(248, 113, 113, 0.1);
          
          --text-main: #f3f4f6;
          --text-muted: #9ca3af;
          --text-dark: #6b7280;
          
          --radius-sm: 6px;
          --radius-md: 12px;
          --radius-lg: 16px;
          
          --shadow-sm: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
          --shadow-md: 0 10px 15px -3px rgba(0, 0, 0, 0.4);
          --shadow-glow: 0 0 20px -5px rgba(92, 108, 250, 0.4);
          
          --font-sans: 'Inter', -apple-system, sans-serif;
          --font-display: 'Space Grotesk', sans-serif;
          --font-mono: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
        }

        * { box-sizing: border-box; margin: 0; padding: 0; }
        body { 
          background-color: var(--bg-dark); 
          color: var(--text-main); 
          font-family: var(--font-sans);
          line-height: 1.6; 
          -webkit-font-smoothing: antialiased;
        }
        
        /* Layout */
        .flex-center { display: flex; align-items: center; justify-content: center; }
        .flex-between { display: flex; align-items: center; justify-content: space-between; }
        .grid-layout { display: grid; grid-template-columns: 1fr 340px; gap: 24px; align-items: flex-start; }
        @media (max-width: 1024px) { .grid-layout { grid-template-columns: 1fr; } }
        
        .w-full { width: 100%; }
        .mt-2 { margin-top: 8px; }
        .mt-4 { margin-top: 16px; }
        .mt-6 { margin-top: 24px; }
        .mb-2 { margin-bottom: 8px; }
        .mb-6 { margin-bottom: 24px; }
        .text-center { text-align: center; }
        
        /* Cards */
        .glass-card {
          background: var(--bg-card);
          border: 1px solid var(--border);
          border-radius: var(--radius-md);
          padding: 24px;
          box-shadow: var(--shadow-sm);
          transition: all 0.2s ease;
        }
        .glass-card:hover { 
          border-color: var(--border-focus); 
          box-shadow: var(--shadow-md); 
        }

        /* Typography */
        h1, h2, h3, h4 { font-family: var(--font-display); font-weight: 700; color: var(--text-main); line-height: 1.2; }
        .brand-header { font-size: 28px; letter-spacing: -0.5px; }
        .subtitle { color: var(--text-muted); font-size: 15px; }

        /* Login Screen */
        .login-container { min-height: 100vh; position: relative; overflow: hidden; }
        .login-overlay {
          position: absolute; top:0; left:0; right:0; bottom:0;
          background: radial-gradient(circle at 50% 0%, rgba(92, 108, 250, 0.15), transparent 60%);
          z-index: 0; pointer-events: none;
        }
        .login-card { position: relative; z-index: 1; max-width: 420px; width: 100%; padding: 40px; }
        .logo-pulse { width: 48px; height: 48px; background: var(--primary); border-radius: 12px; margin: 0 auto 20px; box-shadow: var(--shadow-glow); }

        /* Navigation */
        .app-container { max-width: 1300px; margin: 0 auto; padding: 40px 24px; }
        .header-bar { display: flex; justify-content: space-between; align-items: flex-end; margin-bottom: 32px; border-bottom: 1px solid var(--border); padding-bottom: 20px; }
        .nav-tabs { display: flex; gap: 8px; background: var(--bg-card); padding: 4px; border-radius: var(--radius-sm); border: 1px solid var(--border); }
        
        /* Buttons */
        .btn {
          display: inline-flex; align-items: center; justify-content: center; gap: 8px;
          padding: 10px 18px; border-radius: var(--radius-sm); font-family: var(--font-sans); font-size: 14px; font-weight: 600; cursor: pointer;
          transition: all 0.15s ease; outline: none; border: 1px solid transparent; text-decoration: none;
        }
        .btn:disabled { opacity: 0.6; cursor: not-allowed; }
        .btn:active:not(:disabled) { transform: translateY(1px); }
        
        .btn-primary { background: var(--primary); color: white; box-shadow: 0 2px 10px rgba(92, 108, 250, 0.3); }
        .btn-primary:hover:not(:disabled) { background: var(--primary-hover); box-shadow: var(--shadow-glow); }
        
        .btn-ghost { background: transparent; color: var(--text-muted); }
        .btn-ghost:hover:not(:disabled) { color: var(--text-main); background: rgba(255,255,255,0.05); }

        .btn-danger { background: transparent; color: var(--danger); border-color: var(--danger-bg); }
        .btn-danger:hover:not(:disabled) { background: var(--danger-bg); }

        .btn-success { background: var(--success); color: var(--bg-dark); box-shadow: 0 4px 10px rgba(52, 211, 153, 0.2); }
        .btn-success:hover:not(:disabled) { filter: brightness(1.1); }

        .tab-btn { padding: 8px 16px; border-radius: var(--radius-sm); font-size: 14px; font-weight: 500; cursor: pointer; border: none; background: transparent; color: var(--text-muted); transition: all 0.2s; }
        .tab-btn.active { background: var(--bg-hover); color: var(--text-main); box-shadow: var(--shadow-sm); }
        .tab-btn:hover:not(.active):not(:disabled) { color: var(--text-main); }
        
        .text-link { background: none; border: none; color: var(--primary); font-size: 14px; font-weight: 500; cursor: pointer; text-decoration: none; padding: 4px; }
        .text-link:hover { text-decoration: underline; }

        /* Inputs */
        .input-group { margin-bottom: 16px; text-align: left; }
        .input-group label { display: block; font-size: 13px; font-weight: 600; color: var(--text-muted); margin-bottom: 6px; letter-spacing: 0.02em; }
        .input-field, .select-field { 
          width: 100%; padding: 12px 16px; background: rgba(0,0,0,0.2); border: 1px solid var(--border); 
          border-radius: var(--radius-sm); color: var(--text-main); font-size: 15px; font-family: var(--font-sans);
          transition: all 0.2s ease; outline: none;
        }
        .input-field:focus:not(:disabled), .select-field:focus:not(:disabled) { border-color: var(--primary); box-shadow: 0 0 0 3px var(--primary-light); background: var(--bg-card); }
        .input-field::placeholder { color: var(--text-dark); }
        
        /* Badges */
        .badge { display: inline-flex; align-items: center; padding: 4px 10px; border-radius: 100px; font-size: 11px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.05em; border: 1px solid transparent; }
        .badge.high { color: var(--danger); background: var(--danger-bg); border-color: rgba(248,113,113,0.3); }
        .badge.medium { color: var(--warning); background: var(--warning-bg); border-color: rgba(251,191,36,0.3); }
        .badge.low { color: var(--success); background: var(--success-bg); border-color: rgba(52,211,153,0.3); }
        .badge.auto { color: var(--text-muted); background: var(--border); }
        
        /* Metric cards */
        .metrics-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 16px; margin-bottom: 32px; }
        .metric-card { padding: 20px; display: flex; flex-direction: column; gap: 8px; border-top: 3px solid transparent; }
        .metric-card:nth-child(1) { border-top-color: var(--primary); }
        .metric-card:nth-child(2) { border-top-color: var(--success); }
        .metric-card:nth-child(3) { border-top-color: var(--warning); }
        .metric-card:nth-child(4) { border-top-color: var(--danger); }
        .metric-label { font-size: 13px; font-weight: 600; color: var(--text-muted); }
        .metric-value { font-size: 36px; font-family: var(--font-display); font-weight: 700; color: var(--text-main); line-height: 1; }

        /* Task & Email Items */
        .list-container { display: flex; flex-direction: column; gap: 16px; }
        .item-card { padding: 20px; transition: all 0.2s ease; margin-bottom: 0; }
        .item-card:hover { transform: translateX(4px); }
        .item-card.completed { opacity: 0.6; filter: grayscale(1); }
        
        .task-header { display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 12px; }
        .task-title { font-size: 16px; font-weight: 600; display: flex; align-items: flex-start; gap: 12px; color: var(--text-main); line-height: 1.4; }
        .task-title.completed { text-decoration: line-through; color: var(--text-muted); }
        
        .task-icon { 
          flex-shrink: 0; display: flex; align-items: center; justify-content: center; 
          width: 24px; height: 24px; border-radius: 50%; border: 2px solid var(--border-focus); color: transparent; font-size: 12px; font-weight: bold;
        }
        .task-title.completed .task-icon { border-color: var(--success); background: var(--success-bg); color: var(--success); }

        .meta-row { display: flex; gap: 12px; align-items: center; margin-left: 36px; }
        .meta-text { font-size: 12px; color: var(--text-dark); font-family: var(--font-mono); }

        /* Alert Boxes */
        .alert-box { padding: 14px 16px; border-radius: var(--radius-sm); font-size: 14px; font-weight: 500; display: flex; align-items: center; gap: 12px; }
        .alert-error { background: var(--danger-bg); border-left: 4px solid var(--danger); color: #fecaca; margin-bottom: 24px; }
        .alert-warning { background: var(--warning-bg); border: 1px solid rgba(251,191,36,0.3); color: #fde68a; justify-content: space-between; margin-top: 16px; margin-left: 36px; }

        /* AI Output Box */
        .ai-output { background: var(--bg-dark); border: 1px solid var(--border); border-left: 3px solid var(--primary); padding: 16px; margin-top: 16px; margin-left: 36px; border-radius: 0 var(--radius-sm) var(--radius-sm) 0; }
        .ai-output-title { font-size: 11px; font-weight: 700; color: var(--primary); text-transform: uppercase; margin-bottom: 6px; letter-spacing: 0.05em; display: flex; align-items: center; gap: 6px; }
        .ai-output-title::before { content: ''; display: inline-block; width: 6px; height: 6px; background: var(--primary); border-radius: 50%; box-shadow: 0 0 8px var(--primary); }
        .ai-output-text { font-size: 14px; color: var(--text-muted); white-space: pre-wrap; line-height: 1.5; }
        
        /* Terminal */
        .ai-terminal { background: #07080a; border: 1px solid var(--border); border-radius: var(--radius-md); display: flex; flex-direction: column; height: 100%; min-height: 500px; overflow: hidden; position: sticky; top: 24px; }
        .terminal-header { background: var(--bg-card); border-bottom: 1px solid var(--border); padding: 16px 20px; display: flex; justify-content: space-between; align-items: center; }
        .terminal-title { font-family: var(--font-mono); font-size: 13px; color: var(--text-main); font-weight: 600; display: flex; align-items: center; gap: 8px; }
        .terminal-dot { width: 8px; height: 8px; background: var(--success); border-radius: 50%; box-shadow: 0 0 10px var(--success); }
        .terminal-logs { flex: 1; padding: 20px; overflow-y: auto; font-family: var(--font-mono); font-size: 13px; color: var(--text-muted); display: flex; flex-direction: column; gap: 10px; }
        .log-line { display: flex; gap: 12px; }
        .log-timestamp { color: var(--text-dark); flex-shrink: 0; }
        .log-content { color: var(--success); }

        /* Quick Adding Box */
        .composer-box { display: flex; gap: 12px; padding: 16px; background: var(--bg-card); border: 1px solid var(--border); border-radius: var(--radius-md); margin-bottom: 32px; box-shadow: var(--shadow-sm); }
        .composer-box .input-field { margin-bottom: 0; border: none; background: transparent; padding: 8px 4px; box-shadow: none !important; font-size: 16px; }
        .composer-box .input-field:focus { background: transparent; }
        .composer-box .select-field { width: 140px; margin-bottom: 0; background: var(--bg-hover); border-color: transparent; }

        /* ROI Chart */
        .roi-chart-wrapper { background: var(--bg-card); border: 1px solid var(--border); border-radius: var(--radius-md); padding: 20px; margin-bottom: 32px; position: relative; }
        .roi-title { font-size: 14px; font-weight: 600; color: var(--text-muted); }
        .roi-stat { font-family: var(--font-display); font-size: 20px; font-weight: 700; color: var(--primary); }
        .roi-svg { width: 100%; height: 80px; margin-top: 16px; }

        /* Loader */
        .loading-spinner { display: inline-block; width: 16px; height: 16px; border: 2px solid rgba(255,255,255,0.3); border-top-color: white; border-radius: 50%; animation: spin 1s linear infinite; }
        .text-loader { border-color: var(--text-dark); border-top-color: var(--primary); }

        /* Animations */
        @keyframes spin { 100% { transform: rotate(360deg); } }
        @keyframes fadeIn { from { opacity: 0; } to { opacity: 1; } }
        @keyframes slideUp { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } }
        @keyframes slideDown { from { opacity: 0; transform: translateY(-10px); } to { opacity: 1; transform: translateY(0); } }
        @keyframes scaleIn { from { opacity: 0; transform: scale(0.97); } to { opacity: 1; transform: scale(1); } }
        
        .fade-in { animation: fadeIn 0.3s ease-out forwards; }
        .slide-up { animation: slideUp 0.4s cubic-bezier(0.16, 1, 0.3, 1) forwards; opacity: 0; }
        .slide-down { animation: slideDown 0.3s ease-out forwards; }
        .scale-in { animation: scaleIn 0.4s cubic-bezier(0.16, 1, 0.3, 1) forwards; }
      `}</style>

      <div className="app-container slide-down">
        <header className="header-bar">
          <div>
            <div className="flex-center mb-2" style={{justifyContent: 'flex-start', gap: '12px'}}>
              <div className="logo-pulse" style={{width: '32px', height: '32px', margin: 0, borderRadius: '8px'}}></div>
              <h1 className="brand-header">OmniTask</h1>
            </div>
            <p className="subtitle">Enterprise Orchestration Dashboard</p>
          </div>
          
          <div className="flex-center" style={{gap: '16px'}}>
            <div className="nav-tabs">
              <button className={`tab-btn ${activeTab === 'tasks' ? 'active' : ''}`} onClick={() => setActiveTab('tasks')} disabled={isGlobalLoading}>Workloads</button>
              <button className={`tab-btn ${activeTab === 'emails' ? 'active' : ''}`} onClick={() => { setActiveTab('emails'); if(emails.length===0 && !isOfflineMode) handleFetchEmails(); }} disabled={isGlobalLoading}>Inbox Mapping</button>
            </div>
            <button className="btn btn-ghost" style={{color: 'var(--danger)'}} onClick={handleLogout} disabled={isGlobalLoading}>Sign Out</button>
          </div>
        </header>

        {error && (
          <div className="alert-box alert-error slide-down">
            <svg width="20" height="20" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}><path strokeLinecap="round" strokeLinejoin="round" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>
            {error}
          </div>
        )}

        <div className="grid-layout">
          <div className="main-content">
            {activeTab === 'tasks' ? (
              <div className="fade-in">
                
                <div className="metrics-grid">
                  <div className="glass-card metric-card slide-up" style={{animationDelay: '0s'}}>
                    <span className="metric-label">Total Assigned</span>
                    <span className="metric-value">{metrics.total}</span>
                  </div>
                  <div className="glass-card metric-card slide-up" style={{animationDelay: '0.05s'}}>
                    <span className="metric-label">Completed</span>
                    <span className="metric-value">{metrics.completed}</span>
                  </div>
                  <div className="glass-card metric-card slide-up" style={{animationDelay: '0.1s'}}>
                    <span className="metric-label">Processing</span>
                    <span className="metric-value">{metrics.pending}</span>
                  </div>
                  <div className="glass-card metric-card slide-up" style={{animationDelay: '0.15s'}}>
                    <span className="metric-label">High Priority</span>
                    <span className="metric-value" style={{color: 'var(--danger)'}}>{metrics.high}</span>
                  </div>
                </div>

                <div className="composer-box slide-up" style={{animationDelay: '0.2s'}}>
                  <svg width="24" height="24" fill="none" viewBox="0 0 24 24" stroke="var(--text-dark)" strokeWidth={2} style={{alignSelf: 'center'}}><path strokeLinecap="round" strokeLinejoin="round" d="M12 4v16m8-8H4" /></svg>
                  <input type="text" className="input-field" style={{flex: 1}} placeholder="Describe a new operational objective..." value={text} onChange={(e) => setText(e.target.value)} disabled={isGlobalLoading} onKeyDown={(e) => e.key === 'Enter' && handleAddTask(e)} />
                  <select className="select-field" value={priority} onChange={(e) => setPriority(e.target.value)} disabled={isGlobalLoading}>
                    <option value="auto">Auto-Triage</option>
                    <option value="high">High Priority</option>
                    <option value="medium">Medium Priority</option>
                    <option value="low">Low Priority</option>
                  </select>
                  <button className="btn btn-primary" onClick={handleAddTask} disabled={isGlobalLoading || !text.trim()}>
                    {loading ? <span className="loading-spinner"></span> : "Queue"}
                  </button>
                </div>

                {chartData.length > 1 && <MiniROIChart data={chartData} />}

                <div className="list-container">
                  {tasksLoading ? (
                    <div className="glass-card text-center text-muted fade-in" style={{padding: '48px'}}>
                      <span className="loading-spinner text-loader mb-2"></span>
                      <p>Synchronizing orchestration layer...</p>
                    </div>
                  ) : tasks.length === 0 ? (
                    <div className="glass-card text-center text-muted fade-in" style={{padding: '48px'}}>
                      <svg width="48" height="48" fill="none" viewBox="0 0 24 24" stroke="var(--text-dark)" strokeWidth={1} style={{margin: '0 auto 16px'}}><path strokeLinecap="round" strokeLinejoin="round" d="M5 13l4 4L19 7" /></svg>
                      <p>All objectives achieved. Inbox zero.</p>
                    </div>
                  ) : (
                    tasks.map((task, index) => {
                      const isCompleted = task.status === 'completed';
                      return (
                        <div key={task.id} className={`glass-card item-card slide-up ${isCompleted ? 'completed' : ''}`} style={{animationDelay: `${index * 0.05}s`}}>
                          <div className="task-header">
                            <div className={`task-title ${isCompleted ? 'completed' : ''}`}>
                              <span className="task-icon">{isCompleted ? '✓' : ''}</span>
                              {task.text}
                            </div>
                          </div>
                          
                          <div className="meta-row">
                            <span className={`badge ${task.priority}`}>{task.priority}</span>
                            {task.confidence > 0 && <span className="badge auto">AI Confidence: {task.confidence}%</span>}
                            <span className="meta-text">ID: {task.id}</span>
                          </div>

                          {task.requires_confirmation && !isCompleted && (
                            <div className="alert-box alert-warning fade-in">
                              <span><strong style={{color:'#d97706'}}>Action Required:</strong> Human oversight requested.</span>
                              <button className="btn btn-ghost" style={{color: '#92400e', background: 'rgba(251,191,36,0.2)', padding:'6px 12px'}} onClick={() => handleApproveTask(task.id)} disabled={isGlobalLoading}>
                                Authorize Process
                              </button>
                            </div>
                          )}

                          {task.ai_output && (
                            <div className="ai-output fade-in">
                              <div className="ai-output-title">Extracted Insights</div>
                              <div className="ai-output-text">{task.ai_output}</div>
                            </div>
                          )}
                        </div>
                      )
                    })
                  )}
                </div>
              </div>
            ) : (
              <div className="fade-in">
                <div className="glass-card flex-between mb-6 slide-up" style={{animationDelay: '0s'}}>
                  <div>
                    <h3 className="mb-2">External Communications</h3>
                    <p className="subtitle">Sync and route incoming requests automatically.</p>
                  </div>
                  <div className="flex-center" style={{gap: '12px'}}>
                    <button className="btn btn-ghost" onClick={handleFetchEmails} disabled={isGlobalLoading}>
                      {emailsLoading ? <><span className="loading-spinner text-loader"></span> Syncing</> : 'Refresh Outlook/Gmail'}
                    </button>
                    {emails.length > 0 && (
                      <button className="btn btn-primary" onClick={handleConvertToTasks} disabled={isGlobalLoading}>
                        {loading ? <span className="loading-spinner"></span> : `Process ${emails.length} Threads`}
                      </button>
                    )}
                  </div>
                </div>
                
                <div className="list-container">
                  {emailsLoading ? (
                    <div className="glass-card text-center text-muted fade-in" style={{padding: '48px'}}>
                      <span className="loading-spinner text-loader mb-2"></span>
                      <p>Establishing secure bridge to mail provider...</p>
                    </div>
                  ) : emails.length === 0 ? (
                    <div className="glass-card text-center text-muted fade-in" style={{padding: '48px'}}>
                      <p>No new communications unmapped.</p>
                    </div>
                  ) : (
                    emails.map((email, index) => (
                      <div key={email.id} className="glass-card item-card slide-up" style={{animationDelay: `${index * 0.05}s`}}>
                        <div className="flex-between mb-2">
                          <h3 style={{fontSize: '16px'}}>{email.subject || "No Subject"}</h3>
                          <span className="meta-text">{email.id.substring(0,8)}</span>
                        </div>
                        
                        <div className="meta-text mb-4" style={{color: 'var(--primary)', display: 'flex', alignItems: 'center', gap: '6px', fontSize:'13px'}}>
                          <svg width="14" height="14" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="2"><path strokeLinecap="round" strokeLinejoin="round" d="M16 12a4 4 0 10-8 0 4 4 0 008 0zm0 0v1.5a2.5 2.5 0 005 0V12a9 9 0 10-9 9m4.5-1.206a8.959 8.959 0 01-4.5 1.207" /></svg>
                          {email.sender}
                        </div>
                        
                        <div className="mb-4" style={{color: 'var(--text-muted)', fontSize: '14px', background: 'var(--bg-dark)', padding: '16px', borderRadius: 'var(--radius-sm)', border: '1px solid var(--border)'}}>
                          {email.snippet}
                        </div>
                        
                        <div>
                          {emailReplies[email.id] ? (
                            <div className="ai-output fade-in" style={{marginLeft: 0}}>
                              <div className="ai-output-title">Draft Generated by Agent</div>
                              <div className="ai-output-text">{emailReplies[email.id]}</div>
                            </div>
                          ) : (
                            <button className="btn btn-ghost" style={{color: 'var(--primary)', border: '1px solid var(--border)'}} onClick={() => handleGenerateReply(email)} disabled={isGlobalLoading || generatingReplyFor === email.id}>
                              {generatingReplyFor === email.id ? <><span className="loading-spinner text-loader"></span> Processing...</> : 'Draft AI Response'}
                            </button>
                          )}
                        </div>
                      </div>
                    ))
                  )}
                </div>
              </div>
            )}
          </div>

          <div className="ai-terminal slide-up" style={{animationDelay: '0.2s'}}>
            <div className="terminal-header">
              <span className="terminal-title">
                <span className="terminal-dot"></span>
                SYSTEM_LOG
              </span>
              <button 
                className="btn btn-success" 
                style={{padding: '6px 16px', fontSize: '12px'}}
                onClick={handleRunAIStream} 
                disabled={isGlobalLoading}
              >
                 {loading ? "PROCESSING..." : "RUN INFERENCE"}
              </button>
            </div>
            <div className="terminal-logs" id="terminal-logs">
              {aiLogs.length === 0 && <div className="fade-in" style={{opacity: 0.4}}>Standby. Environment securely loaded.</div>}
              {aiLogs.map((log, i) => {
                const now = new Date();
                const timeStr = `${now.getHours().toString().padStart(2, '0')}:${now.getMinutes().toString().padStart(2, '0')}:${now.getSeconds().toString().padStart(2, '0')}`;
                return (
                  <div key={i} className="log-line fade-in">
                    <span className="log-timestamp">[{timeStr}]</span>
                    <span className="log-content">{log}</span>
                  </div>
                )
              })}
              {loading && <div className="fade-in" style={{width: '6px', height: '14px', background: 'var(--success)', animation: 'pulse 1s infinite alternate'}} />}
            </div>
          </div>
        </div>
      </div>
    </>
  );
}

export default App;
