import React from 'react';
import { BarPerf } from '../components/ChartCard.jsx';

export default function ModelPerformance() {
  const baseline = Array.from({length: 10}).map((_,i)=>({ t:`Epoch ${i+1}`, acc: 88 + i*0.7 + Math.random()*1.2 }));
  const finetuned = Array.from({length: 10}).map((_,i)=>({ t:`Epoch ${i+1}`, acc: 91 + i*0.6 + Math.random()*1.0 }));
  const confusion = [
    { name:'TP', v: 18420 },
    { name:'TN', v: 21230 },
    { name:'FP', v: 620 },
    { name:'FN', v: 480 },
  ];

  return (
    <div className="grid" style={{gap:16}}>
      <div className="grid grid-2">
        <BarPerf data={baseline}/>
        <BarPerf data={finetuned}/>
      </div>

      <div className="card">
        <div className="card-header"><div className="card-title">Baseline Model Accuracy</div></div>
        <div className="card-body" style={{display:'grid', gridTemplateColumns:'repeat(4, 1fr)', gap:12}}>
          <div className="glass" style={{padding:12}}><div className="card-subtitle">Accuracy</div><div style={{fontSize:28, fontWeight:800}}>93.2%</div></div>
          <div className="glass" style={{padding:12}}><div className="card-subtitle">Precision</div><div style={{fontSize:28, fontWeight:800}}>92.1%</div></div>
          <div className="glass" style={{padding:12}}><div className="card-subtitle">Recall</div><div style={{fontSize:28, fontWeight:800}}>94.6%</div></div>
          <div className="glass" style={{padding:12}}><div className="card-subtitle">F1</div><div style={{fontSize:28, fontWeight:800}}>93.3%</div></div>
        </div>
      </div>

      <div className="card">
        <div className="card-header"><div className="card-title">Fine‑tuned Model Accuracy</div></div>
        <div className="card-body" style={{display:'grid', gridTemplateColumns:'repeat(4, 1fr)', gap:12}}>
          <div className="glass" style={{padding:12}}><div className="card-subtitle">Accuracy</div><div style={{fontSize:28, fontWeight:800}}>97.4%</div></div>
          <div className="glass" style={{padding:12}}><div className="card-subtitle">Precision</div><div style={{fontSize:28, fontWeight:800}}>96.8%</div></div>
          <div className="glass" style={{padding:12}}><div className="card-subtitle">Recall</div><div style={{fontSize:28, fontWeight:800}}>98.1%</div></div>
          <div className="glass" style={{padding:12}}><div className="card-subtitle">F1</div><div style={{fontSize:28, fontWeight:800}}>97.4%</div></div>
        </div>
      </div>

      <div className="card">
        <div className="card-header"><div className="card-title">Confusion Matrix (Fine‑tuned)</div></div>
        <div className="card-body">
          <div style={{display:'grid', gridTemplateColumns:'repeat(4, 1fr)', gap:12}}>
            {confusion.map((c,i)=>(
              <div key={i} className="glass" style={{padding:12}}>
                <div className="card-subtitle">{c.name}</div>
                <div style={{fontSize:28, fontWeight:800}}>{c.v.toLocaleString()}</div>
              </div>
            ))}
          </div>
        </div>
      </div>

      <div className="card">
        <div className="card-header"><div className="card-title">Inference Latency</div></div>
        <div className="card-body" style={{display:'grid', gridTemplateColumns:'repeat(3, 1fr)', gap:12}}>
          <div className="glass" style={{padding:12}}><div className="card-subtitle">Mean</div><div style={{fontSize:28, fontWeight:800}}>118 ms</div></div>
          <div className="glass" style={{padding:12}}><div className="card-subtitle">P95</div><div style={{fontSize:28, fontWeight:800}}>172 ms</div></div>
          <div className="glass" style={{padding:12}}><div className="card-subtitle">P99</div><div style={{fontSize:28, fontWeight:800}}>215 ms</div></div>
        </div>
      </div>
    </div>
  );
}
