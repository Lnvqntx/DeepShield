// src/components/MetricCard.jsx
import React from 'react';

export default function MetricCard({ title, value, delta, icon }) {
  const isUp = delta?.startsWith('+');
  const dClass = isUp ? 'delta up' : 'delta down';
  return (
    <div className="card metric-card">
      <div style={{display:'flex', alignItems:'center', justifyContent:'space-between'}}>
        <div className="icon">{icon}</div>
        <div className={dClass}><span>{delta}</span></div>
      </div>
      <div className="metric-value">{value}</div>
      <div className="metric-title">{title}</div>
    </div>
  );
}
