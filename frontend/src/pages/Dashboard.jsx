import React from 'react';
import MetricCard from '../components/MetricCard.jsx';
import { TrendCard, PieDist, BarPerf } from '../components/ChartCard.jsx';

export default function Dashboard() {
  const statData = [
    { title: 'Total Audio Analyzed', value: '1.24M', delta: '+8.4%', icon: <svg width="18" height="18" viewBox="0 0 24 24" fill="none"><path d="M3 12h18M12 3v18" stroke="currentColor" strokeWidth="1.5"/></svg> },
    { title: 'Fake Voices Detected', value: '18,432', delta: '+3.1%', icon: <svg width="18" height="18" viewBox="0 0 24 24" fill="none"><path d="M12 3l8 4v6c0 5-8 8-8 8s-8-3-8-8V7l8-4z" stroke="currentColor" strokeWidth="1.5"/></svg> },
    { title: 'Live Calls Monitored', value: '2,104', delta: '+2.9%', icon: <svg width="18" height="18" viewBox="0 0 24 24" fill="none"><path d="M22 16.92V21a1 1 0 01-1.09 1 19 19 0 01-8.3-8.3A1 1 0 0113 12h-1V9a1 1 0 011-1 20 20 0 0119 6.92z" stroke="currentColor" strokeWidth="1.5"/></svg> },
    { title: 'Detection Accuracy', value: '98.6%', delta: '+0.4%', icon: <svg width="18" height="18" viewBox="0 0 24 24" fill="none"><path d="M9 12l2 2 4-4M21 12a9 9 0 11-18 0 9 9 0 0118 0z" stroke="currentColor" strokeWidth="1.5"/></svg> },
  ];

  const trendData = Array.from({length: 20}).map((_,i) => ({ t: `${i}`, v: Math.round(80 + Math.sin(i/2)*10 + Math.random()*8) }));
  const dist = [
    { name: 'Real', v: 76 },
    { name: 'Fake', v: 24 },
  ];
  const perf = Array.from({length: 12}).map((_,i)=>({ t:`${i+1}/${24}`, acc: 92 + Math.random()*6 }));

  return (
    <div className="grid" style={{gap:16}}>
      <div className="grid grid-4">
        {statData.map((s, idx) => <MetricCard key={idx} {...s}/>)}
      </div>

      <div className="grid grid-3">
        <TrendCard title="Audio Analysis Volume (24h)" data={trendData} color="var(--accent)"/>
        <PieDist data={dist}/>
        <TrendCard title="False Positive Rate" data={trendData.map(d => ({t:d.t, v: 10 + Math.random()*6}))} color="var(--info)"/>
      </div>

      <BarPerf data={perf}/>
      <div className="card">
        <div className="card-header"><div className="card-title">System Alerts</div></div>
        <div className="card-body">
          <div style={{display:'grid', gridTemplateColumns:'1fr 1fr', gap:12}}>
            <div className="glass" style={{padding:12}}>
              <div style={{display:'flex', alignItems:'center', gap:10}}>
                <div className="badge badge-success">Resolved</div>
                <div style={{fontWeight:800}}>Model drift threshold reached</div>
              </div>
              <div style={{color:'var(--text-secondary)', marginTop:6}}>Fine‑tuned model retrained. Accuracy +0.6%.</div>
            </div>
            <div className="glass" style={{padding:12}}>
              <div style={{display:'flex', alignItems:'center', gap:10}}>
                <div className="badge badge-danger">Active</div>
                <div style={{fontWeight:800}}>Spike in fake calls</div>
              </div>
              <div style={{color:'var(--text-secondary)', marginTop:6}}>Region APAC, EN/HI flagged. Investigating source.</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
