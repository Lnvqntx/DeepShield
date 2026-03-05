import React from 'react';
import { TrendCard, BarPerf, PieDist } from '../components/ChartCard.jsx';

export default function Analytics() {
  const vol = Array.from({length: 24}).map((_,i) => ({ t: `${i}:00`, v: 40 + Math.sin(i/2)*10 + Math.random()*18 }));
  const acc = Array.from({length: 24}).map((_,i)=>({ t:`${i}:00`, acc: 92 + Math.sin(i/3)*2 + Math.random()*3 }));
  const langDist = [
    { name:'English', v: 56 },
    { name:'Hindi', v: 27 },
    { name:'Telugu', v: 17 },
  ];

  return (
    <div className="grid" style={{gap:16}}>
      <TrendCard title="Audio Analysis Volume (24h)" data={vol} color="var(--accent)"/>
      <BarPerf data={acc}/>
      <div className="grid grid-3">
        <TrendCard title="False Negative Rate" data={vol.map(d=>({t:d.t, v: 8 + Math.random()*5}))} color="var(--danger)"/>
        <PieDist data={langDist}/>
        <TrendCard title="Processing Latency (ms)" data={vol.map(d=>({t:d.t, v: 120 + Math.random()*40}))} color="var(--info)"/>
      </div>

      <div className="card">
        <div className="card-header"><div className="card-title">Recent Analysis Events</div></div>
        <div className="card-body">
          <table className="table">
            <thead>
              <tr><th>Time</th><th>Source</th><th>Language</th><th>Result</th><th>Confidence</th></tr>
            </thead>
            <tbody>
              {Array.from({length: 8}).map((_,i) => {
                const isFake = Math.random() < 0.25;
                const langs = ['English','Hindi','Telugu'];
                const l = langs[Math.floor(Math.random()*langs.length)];
                const conf = 60 + Math.random()*38;
                return (
                  <tr key={i}>
                    <td>{new Date(Date.now()-i*3600e3).toLocaleTimeString()}</td>
                    <td>{isFake ? 'Live Call' : 'Upload'}</td>
                    <td>{l}</td>
                    <td><span className={`badge ${isFake ? 'badge-danger' : 'badge-success'}`}>{isFake ? 'FAKE' : 'REAL'}</span></td>
                    <td>{Math.round(conf)}%</td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
