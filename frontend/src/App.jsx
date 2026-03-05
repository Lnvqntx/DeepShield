// src/App.jsx
import React from 'react';
import { NavLink, Route, Routes, useLocation } from 'react-router-dom';
import ThemeToggle from './components/ThemeToggle';   // <-- NEW
import Dashboard from './pages/Dashboard';
import LiveDetection from './pages/LiveDetection';
import AudioUpload from './pages/AudioUpload';
import Analytics from './pages/Analytics';
import ModelPerformance from './pages/ModelPerformance';
import AudioVisualization from './pages/AudioVisualization';
import SystemArchitecture from './pages/SystemArchitecture';

import './App.css';

function Topbar() {
  const location = useLocation();
  const getPageTitle = () => {
    const map = {
      '/': 'Dashboard',
      '/live': 'Live Detection',
      '/upload': 'Audio Upload',
      '/analytics': 'Analytics',
      '/models': 'Model Performance',
      '/visualization': 'Audio Visualization',
      '/architecture': 'System Architecture'
    };
    return map[location.pathname] || 'AI Deepfake Audio Detection';
  };

  return (
    <div className="topbar">
      <div style={{display:'flex', alignItems:'center', gap:12}}>
        <div style={{width:8, height:8, borderRadius:999, background:'var(--success)', boxShadow:'0 0 12px rgba(34,197,94,0.7)'}}/>
        <strong style={{letterSpacing:'0.3px'}}>{getPageTitle()}</strong>
      </div>

      <div style={{display:'flex', alignItems:'center', gap:12}}>
        <ThemeToggle/> {/* <-- NEW THEME TOGGLE */}

        <div className="search">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none">
            <path d="M21 21l-4.35-4.35m2.35-6.15a8 8 0 11-16 0 8 8 0 0116 0z"
                  stroke="var(--text-secondary)" strokeWidth="2" strokeLinecap="round"/>
          </svg>
          <input className="input" placeholder="Search models, datasets, reports..." style={{background:'transparent', border:'none', padding:0}}/>
        </div>

        <div className="badge badge-info" title="System healthy">
          <span style={{width:8, height:8, borderRadius:999, background:'var(--info)'}}/> All systems nominal
        </div>

        <div className="badge" style={{color:'#ddd', background:'rgba(255,255,255,0.05)'}}>
          EN | HI | TE
        </div>

        <button className="btn btn-ghost">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none">
            <path d="M15 17h5l-1.4-1.4A2 2 0 0118 14.2V11a6 6 0 10-12 0v3.2c0 .53-.21 1.04-.59 1.41L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9"
                  stroke="var(--text-secondary)" strokeWidth="2" strokeLinecap="round"/>
          </svg>
        </button>

        <div style={{width:32, height:32, borderRadius:999, background:'linear-gradient(135deg,#4f46e5,#ef4444)'}}/>
      </div>
    </div>
  );
}

function Sidebar() {
  return (
    <aside className="sidebar">
      <div className="brand" style={{display:'flex', alignItems:'center', gap:12, padding:'16px 16px 12px'}}>
  <div className="logo" style={{flexShrink:0}}>
    <img
      src="/logos/logo.png"
      alt="DeepShield Voice"
      style={{
        width: "100%",
        height: "100%",
        objectFit: "contain",
        filter: "drop-shadow(0 0 12px rgba(249,115,22,0.25))"
      }}
    />
  </div>
  <div>
    <div style={{fontWeight:800, fontSize:16, letterSpacing:'0.5px', color:'var(--text-primary)', lineHeight:1.2}}>DEEPSHIELD</div>
    <div style={{fontSize:10, color:'var(--text-secondary)', letterSpacing:'1.5px', marginTop:2}}>VOICE AI DETECTION</div>
  </div>
</div>

      <nav className="nav">
        <NavLink to="/" end className={({isActive}) => isActive ? 'active' : ''}>
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none"><path d="M3 12l9-9 9 9v8a1 1 0 01-1 1h-6v-7H10v7H4a1 1 0 01-1-1v-8z" stroke="currentColor" strokeWidth="1.5"/></svg>
          Dashboard
        </NavLink>
        <NavLink to="/live" className={({isActive}) => isActive ? 'active' : ''}>
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none"><path d="M7 4v10a5 5 0 1010 0V4h3v16H4V4h3z" stroke="currentColor" strokeWidth="1.5"/></svg>
          Live Detection
        </NavLink>
        <NavLink to="/upload" className={({isActive}) => isActive ? 'active' : ''}>
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none"><path d="M7 16h10M12 4v12m0 0l-4-4m4 4l4-4" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round"/></svg>
          Audio Upload
        </NavLink>
        <NavLink to="/analytics" className={({isActive}) => isActive ? 'active' : ''}>
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none"><path d="M4 20h16M7 20V10m5 10V4m5 16v-8" stroke="currentColor" strokeWidth="1.5"/></svg>
          Analytics
        </NavLink>
        <NavLink to="/models" className={({isActive}) => isActive ? 'active' : ''}>
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none"><path d="M5 3h14v6H5zM5 15h6v6H5zM15 15h4v6h-4z" stroke="currentColor" strokeWidth="1.5"/></svg>
          Model Performance
        </NavLink>
        <NavLink to="/visualization" className={({isActive}) => isActive ? 'active' : ''}>
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none"><path d="M3 7h18M6 3h12M7 21h10" stroke="currentColor" strokeWidth="1.5"/></svg>
          Audio Visualization
        </NavLink>
        <NavLink to="/architecture" className={({isActive}) => isActive ? 'active' : ''}>
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none"><path d="M12 3l8 4v6c0 5-8 8-8 8s-8-3-8-8V7l8-4z" stroke="currentColor" strokeWidth="1.5"/></svg>
          System Architecture
        </NavLink>
      </nav>
      <div style={{marginTop:'auto'}} className="card glass">
        <div className="card-body">
          <div style={{fontWeight:800, marginBottom:6}}>Need help?</div>
          <div style={{color:'var(--text-secondary)', fontSize:13, marginBottom:12}}>Explore docs, API and research papers.</div>
          <div style={{display:'flex', gap:8}}>
            <button className="btn btn-primary" style={{flex:1}}>Docs</button>
            <button className="btn" style={{flex:1}}>API</button>
          </div>
        </div>
      </div>
    </aside>
  );
}

export default function App() {
  return (
    <div className="app">
      <Sidebar/>
      <Topbar/>
      <main className="main">
        <Routes>
          <Route path="/" element={<Dashboard/>}/>
          <Route path="/live" element={<LiveDetection/>}/>
          <Route path="/upload" element={<AudioUpload/>}/>
          <Route path="/analytics" element={<Analytics/>}/>
          <Route path="/models" element={<ModelPerformance/>}/>
          <Route path="/visualization" element={<AudioVisualization/>}/>
          <Route path="/architecture" element={<SystemArchitecture/>}/>
        </Routes>
      </main>
    </div>
  );
}
