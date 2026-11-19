import React, {useState} from 'react';
import {Search} from 'lucide-react';
import {explain} from '../app/config.jsx';
export function NavLink({page,label,icon:Icon,active,parent,count,onClick,onPreviewChange}){
 const [hover,setHover]=useState(false),[focused,setFocused]=useState(false),visible=hover||focused;
 const description=page==='tour'?'Walk through the real SupplierTrust workspace one step at a time.':page==='about'?explain.about:explain[page]||explain.directory;
 const hint=page==='directory'?'Search · filter · investigate':page==='tour'?'Keyboard: ← → · Esc to exit':'Open this section';
 const show=()=>onPreviewChange?.({page,label,description,hint});
 const close=()=>{setHover(false);setFocused(false);onPreviewChange?.(null)};
 return <div className={`nav-wrap ${active?'active':''}`} data-nav-page={page} onMouseEnter={()=>{setHover(true);show()}} onMouseLeave={()=>{setHover(false);if(!focused)onPreviewChange?.(null)}} onFocus={()=>{setFocused(true);show()}} onBlur={e=>{if(!e.currentTarget.contains(e.relatedTarget)){setFocused(false);if(!hover)onPreviewChange?.(null)}}} onKeyDown={e=>{if(e.key==='Escape')close()}}>
  <button className={`nav-link ${active?'selected':''} ${parent?'parent':''}`} aria-current={active?'page':parent?'location':undefined} aria-label={parent?`${label}, parent section`:label} title={description} aria-describedby={visible?'sidebar-context':undefined} onClick={()=>{close();onClick?.()}}><Icon size={18}/><span>{label}</span>{count!=null&&<small className="nav-count">{count}</small>}</button>
 </div>;
}
