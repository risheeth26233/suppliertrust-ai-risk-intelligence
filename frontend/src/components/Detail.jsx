import React from 'react';
import {ArrowUpRight} from 'lucide-react';
export function Detail({label,value,link}){return <div className="detail-item"><small>{label}</small>{link?<a href={link} target="_blank" rel="noreferrer">{value||'Not provided'} <ArrowUpRight size={13}/></a>:<strong>{value||'Not provided'}</strong>}</div>}
