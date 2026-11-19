import React from 'react';
import {BookOpen,ChevronDown,ShieldCheck,X} from 'lucide-react';
import {NavLink} from '../components/NavLink.jsx';
import {navGroups} from '../app/config.jsx';
export function Sidebar({mobile,navRef,setMobile,go,demo,rows,menuButton,navHelp,setNavHelp,page}){const DEMO_MODE=demo;return <>
  <aside id="sidebar-navigation" className={`sidebar ${mobile?'is-open':''}`} ref={navRef} aria-label="Main navigation" role={mobile?'dialog':undefined} aria-modal={mobile||undefined}>
   <a className="brand" href="/" onClick={e=>{e.preventDefault();go('/')}}><span className="brand-mark"><ShieldCheck size={21}/></span><span className="brand-name">Supplier<span>Trust</span><small>SUPPLIER INTELLIGENCE</small></span></a>
   <button className="drawer-close" aria-label="Close navigation" onClick={()=>setMobile(false)}><X size={19}/></button>
   <div className="workspace-chip"><span className="workspace-avatar">ST</span><span><b>{DEMO_MODE?'Demo workspace':'Local workspace'}</b><small>{DEMO_MODE?'Fictional records':'Local prototype'}</small></span><ChevronDown size={15}/></div>
   {navGroups.map(g=><div className="nav-group" key={g.title}><div className="nav-heading">{g.title}</div>{g.items.map(([p,label,Icon])=>menuButton(p,label,Icon,p==='directory'?rows.length:null))}</div>)}
   <div className="nav-group nav-help"><div className="nav-heading">HELP</div><NavLink page="about" label="Help & Product Tour" icon={BookOpen} active={page==='about'} onPreviewChange={setNavHelp} onClick={()=>go({page:'about'})}/></div>
   <div className={`sidebar-foot ${navHelp?'has-context':''}`} id="sidebar-context" role={navHelp?'tooltip':undefined} aria-live="polite">{navHelp?<><div className="sidebar-shield"><BookOpen size={17}/></div><strong>{navHelp.label}</strong><p>{navHelp.description}</p><small className="sidebar-context-hint">{navHelp.hint}</small></>:<><div className="sidebar-shield"><ShieldCheck size={17}/></div><strong>Evidence before conclusions</strong><p>Every indicator points back to recorded information.</p></>}<span className="mode-tag"><i/> {DEMO_MODE?'FICTIONAL · READ ONLY':'LOCAL WORKSPACE'}</span></div>
  </aside>
</>}
