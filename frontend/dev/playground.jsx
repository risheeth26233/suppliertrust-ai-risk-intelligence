import React, {useState} from 'react';
import {createRoot} from 'react-dom/client';
import {ArrowUpRight, Check, RotateCcw} from 'lucide-react';
import {AnimatedButton, AnimatedCard, AnimatedInput, AnimatedProgress, AnimatedTabs, AnimatedToast, AnimatedToggle, MotionTooltip} from '../src/motion/components.jsx';
import './playground.css';

function Playground(){
 const [section,setSection]=useState('profile');const [enabled,setEnabled]=useState(true);const [value,setValue]=useState(20);const [toast,setToast]=useState(false);const [motionOff,setMotionOff]=useState(false);const [mounted,setMounted]=useState(true);const [email,setEmail]=useState('');
 const advance=()=>setValue(current=>{const next=Math.min(100,current+20);if(next===100)setToast(true);return next});
 const reset=()=>{setValue(20);setToast(false)};
 return <main className="playground" data-motion={motionOff?'off':'on'}>
  <header className="playground-header"><div className="brand-mark">ST</div><div><p className="eyebrow">INTERACTION SYSTEM · LOCAL PREVIEW</p><h1>Effects-only motion</h1><p>Small, useful responses for a serious supplier intelligence workspace.</p></div><span className="demo-chip"><i/> DEVELOPMENT ONLY</span></header>
  <section className="notice"><b>Visual feedback, no sound effects or lettering.</b><span>Finite, component-local animations. Your system reduced-motion preference is respected.</span></section>
  <section className="card motion-settings"><div><span className="eyebrow">ACCESSIBILITY</span><h2>Motion preference</h2><p>Turn off motion in this preview to inspect the same controls without animation.</p></div><AnimatedToggle label="Reduce motion" checked={motionOff} onChange={setMotionOff}/></section>
  <div className="play-grid">
   <AnimatedCard className="showcase-card"><span className="eyebrow">BUTTON FEEDBACK</span><h2>One clear action at a time</h2><p>Press feedback settles quickly. The primary action adds a short, abstract geometric impact.</p><div className="control-row"><AnimatedButton burst onClick={()=>setToast(true)}>Open investigation <ArrowUpRight size={16}/></AnimatedButton><AnimatedButton className="secondary" onClick={advance}>Advance review</AnimatedButton></div><div className="control-row state-row"><AnimatedButton className="secondary" onClick={()=>setToast(true)}>Hover / keyboard focus</AnimatedButton><AnimatedButton className="secondary" disabled>Disabled action</AnimatedButton></div><p className="caption">Hover with a pointer, use Tab for focus, or press and hold to see the active state.</p></AnimatedCard>
   <AnimatedCard className="showcase-card"><span className="eyebrow">CONTEXTUAL NAVIGATION</span><h2>Move between review sections</h2><p>Selection stays visible as the indicator slides to the current destination.</p><AnimatedTabs label="Playground sections" selected={section} onSelect={setSection} items={[
    {id:'profile',label:'Profile',content:<p>Supplier identity and recorded findings are shown in context.</p>},
    {id:'evidence',label:'Evidence',content:<p>Evidence keeps its selected state and source details together.</p>},
    {id:'report',label:'Report',content:<p>Reports remain a clear destination with a familiar keyboard model.</p>}
   ]}/></AnimatedCard>
   <AnimatedCard className="showcase-card"><span className="eyebrow">STATE AND PROGRESS</span><h2>Show completion only when earned</h2><p>Progress uses a native control; completion follows the real state change.</p><AnimatedToggle label="Screening context enabled" checked={enabled} onChange={setEnabled}/><AnimatedProgress label="Review preparation" value={value}/><div className="control-row"><AnimatedButton className="secondary" disabled={value===100} onClick={advance}>Complete next step</AnimatedButton><AnimatedButton className="secondary" onClick={reset}><RotateCcw size={15}/> Reset sample</AnimatedButton></div></AnimatedCard>
   <AnimatedCard className="showcase-card"><span className="eyebrow">FOCUS AND VALIDATION</span><h2>Respond where the user is working</h2><p>Keyboard and pointer input share the same feedback and validation state.</p><div className="control-row"><MotionTooltip text="A short explanation appears on hover or keyboard focus."><button className="motion-button secondary" type="button">Hover or focus for context</button></MotionTooltip></div><AnimatedInput label="Work email" type="email" value={email} onChange={e=>setEmail(e.target.value)} onBlur={e=>e.currentTarget.dataset.touched='true'} placeholder="you@company.com" error={email&&!/^\S+@\S+\.\S+$/.test(email)?'Enter a valid email address.':undefined}/></AnimatedCard>
   <AnimatedCard className="showcase-card"><span className="eyebrow">ANIMATION CLEANUP</span><h2>Mount only when needed</h2><p>The sample button unmounts while its press animation is in progress. No shared animation loop is left behind.</p><div className="control-row">{mounted?<AnimatedButton data-testid="mount-sample" onClick={()=>setToast(true)}>Start and unmount</AnimatedButton>:<span className="caption">Sample unmounted.</span>}<button className="plain-button" type="button" onClick={()=>setMounted(value=>!value)}>{mounted?'Unmount sample':'Mount sample'}</button></div></AnimatedCard>
   <AnimatedCard className="showcase-card disabled-card"><span className="eyebrow">DISABLED STATE</span><h2>Unavailable action</h2><p>Disabled controls stay legible and do not trigger feedback.</p><AnimatedButton burst disabled>Refresh unavailable source</AnimatedButton></AnimatedCard>
  </div>
  <footer><span>SupplierTrust motion playground · local development artifact</span><span>Graphite · emerald · reduced-motion aware</span></footer>
  <AnimatedToast open={toast} onClose={()=>setToast(false)}><Check size={16}/> State updated. Review progress is recorded.</AnimatedToast>
 </main>
}

if(!import.meta.env.DEV)throw new Error('The motion playground is available only in local development.');
createRoot(document.getElementById('root')).render(<Playground/>);
