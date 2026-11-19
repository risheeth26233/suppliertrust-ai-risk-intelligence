import React from 'react';
export function Metric({icon:Icon,label,value,note,color}){return <article className={`metric-card metric-${color}`}><div className="metric-head"><span>{label}</span><i><Icon size={18}/></i></div><strong>{value}</strong><small>{note}</small></article>}
