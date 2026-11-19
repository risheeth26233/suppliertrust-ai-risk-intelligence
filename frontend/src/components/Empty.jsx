import React from 'react';
import {ArrowRight, Search} from 'lucide-react';
export function Empty({title,body,action,onAction}){return <div className="empty-state"><span className="empty-state-icon"><Search size={20}/></span><h2>{title}</h2><p>{body}</p>{action&&<button className="button button-secondary" onClick={onAction}>{action} <ArrowRight size={15}/></button>}</div>}
