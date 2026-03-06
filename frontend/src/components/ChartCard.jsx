// src/components/ChartCard.jsx
import React from 'react';
import { AreaChart, Area, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid, BarChart, Bar, PieChart, Pie, Cell } from 'recharts';
import { useTheme } from '../contexts/ThemeContext';

function useTooltipStyle() {
  const { theme } = useTheme();
  return {
    background: theme === 'dark' ? '#1E1E2F' : '#ffffff',
    border: '1px solid var(--border)',
    borderRadius: 8,
    color: 'var(--text-primary)',
  };
}

function useGridStroke() {
  const { theme } = useTheme();
  return theme === 'dark' ? 'rgba(255,255,255,0.06)' : 'rgba(0,0,0,0.08)';
}

export function SparkArea({ data, color='var(--accent)' }) {
  const tooltipStyle = useTooltipStyle();
  const gridStroke = useGridStroke();
  return (
    <ResponsiveContainer width="100%" height={80}>
      <AreaChart data={data}>
        <defs>
          <linearGradient id="g" x1="0" y1="0" x2="0" y2="1">
            <stop offset="5%" stopColor={color} stopOpacity={0.35}/>
            <stop offset="95%" stopColor={color} stopOpacity={0}/>
          </linearGradient>
        </defs>
        <CartesianGrid stroke={gridStroke} />
        <XAxis hide />
        <YAxis hide />
        <Tooltip
          contentStyle={tooltipStyle}
          labelStyle={{color:'var(--text-secondary)'}}
        />
        <Area type="monotone" dataKey="v" stroke={color} fill="url(#g)" strokeWidth={2} dot={false}/>
      </AreaChart>
    </ResponsiveContainer>
  );
}

export function TrendCard({ title, data, color='var(--accent)' }) {
  return (
    <div className="card">
      <div className="card-header">
        <div className="card-title">{title}</div>
      </div>
      <div className="card-body">
        <SparkArea data={data} color={color}/>
      </div>
    </div>
  );
}

export function BarPerf({ data, color='var(--accent)' }) {
  const tooltipStyle = useTooltipStyle();
  const gridStroke = useGridStroke();
  return (
    <div className="card">
      <div className="card-header"><div className="card-title">Accuracy Over Time</div></div>
      <div className="card-body" style={{height:260}}>
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={data}>
            <CartesianGrid stroke={gridStroke}/>
            <XAxis dataKey="t" stroke="var(--text-secondary)"/>
            <YAxis stroke="var(--text-secondary)"/>
            <Tooltip contentStyle={tooltipStyle} />
            <Bar dataKey="acc" fill={color} radius={[6,6,0,0]}/>
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}

export function PieDist({ data }) {
  const COLORS = ['#22C55E', '#EF4444', '#F59E0B', '#38BDF8'];
  const tooltipStyle = useTooltipStyle();
  return (
    <div className="card">
      <div className="card-header"><div className="card-title">Fake vs Real Distribution</div></div>
      <div className="card-body" style={{height:260}}>
        <ResponsiveContainer width="100%" height="100%">
          <PieChart>
            <Pie data={data} dataKey="v" nameKey="name" innerRadius={50} outerRadius={90} paddingAngle={4}>
              {data.map((e,i) => <Cell key={i} fill={COLORS[i%COLORS.length]}/>)}
            </Pie>
            <Tooltip contentStyle={tooltipStyle}/>
          </PieChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
