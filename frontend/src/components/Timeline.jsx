// src/components/Timeline.jsx
import React from 'react';

// items: [{id, label, status:'REAL'|'FAKE', time?:string}]
export default function Timeline({ items }) {
  return (
    <div className="timeline">
      {items.map((it) => (
        <div key={it.id} className={`chunk ${it.status === 'REAL' ? 'real' : 'fake'}`}>
          {it.label} • {it.status}
        </div>
      ))}
    </div>
  );
}
