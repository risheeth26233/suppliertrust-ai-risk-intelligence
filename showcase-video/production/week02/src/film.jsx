import React from 'react';
import {AbsoluteFill, OffthreadVideo, Sequence, interpolate, staticFile, useCurrentFrame, useVideoConfig} from 'remotion';
import captions from '../captions.json';
import liveMetadata from '../live-metadata.json';

const C = {bg: '#090d12', panel: '#111923', edge: '#273443', text: '#f4f7fb', muted: '#9babb9', green: '#64e0b0', blue: '#9bbcff'};
const clamp = {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'};
const ease = {durationInFrames: 30, config: {damping: 20, stiffness: 72}};

function Text({children, style = {}, ...props}) {
  return <div {...props} style={{fontFamily: 'Segoe UI Variable, Segoe UI, Inter, Arial, sans-serif', color: C.text, ...style}}>{children}</div>;
}

function Backdrop({seed = 0}) {
  const frame = useCurrentFrame();
  const {width, height} = useVideoConfig();
  return <AbsoluteFill style={{background: `radial-gradient(ellipse at ${56 + Math.sin((frame + seed) / 110) * 5}% ${42 + Math.cos((frame + seed) / 120) * 5}%, #142639 0%, ${C.bg} 62%)`}}>
    <svg width={width} height={height} style={{position: 'absolute', inset: 0, opacity: 0.2}}>
      {Array.from({length: 19}, (_, i) => <line key={i} x1={i * 110} y1="0" x2={i * 110} y2={height} stroke="#7c92a8" strokeWidth="1" opacity="0.12" />)}
      {Array.from({length: 11}, (_, i) => <line key={i} x1="0" y1={i * 110} x2={width} y2={i * 110} stroke="#7c92a8" strokeWidth="1" opacity="0.12" />)}
    </svg>
    <AbsoluteFill style={{background: 'linear-gradient(180deg, transparent 65%, #080b10aa 100%)'}} />
  </AbsoluteFill>;
}

function Kicker({children}) {
  return <Text style={{fontSize: 18, letterSpacing: 4, fontWeight: 700, textTransform: 'uppercase', color: C.green}}>{children}</Text>;
}

function SectionTag({children}) {
  return <Text style={{position: 'absolute', top: 50, left: 72, fontSize: 17, fontWeight: 700, letterSpacing: 2.2, color: '#c5d2df', textTransform: 'uppercase'}}>{children}</Text>;
}

function Shield({size = 72}) {
  return <svg width={size} height={size} viewBox="0 0 72 72" fill="none" aria-hidden="true"><rect x="2" y="2" width="68" height="68" rx="21" fill="#162c43" stroke="#426289" strokeWidth="2"/><path d="M36 13 52 19v13c0 12-7 21-16 27-9-6-16-15-16-27V19l16-6Z" stroke="#87afff" strokeWidth="4" strokeLinejoin="round"/><path d="m28 35 6 6 11-13" stroke="#68dfb0" strokeWidth="4" strokeLinecap="round" strokeLinejoin="round"/></svg>;
}

function SceneOne() {
  const f = useCurrentFrame();
  const titleY = interpolate(f, [0, 28], [38, 0], clamp);
  const titleOpacity = interpolate(f, [0, 18], [0, 1], clamp);
  const cardOpacity = interpolate(f, [145, 172], [0, 1], clamp);
  const cardY = interpolate(f, [145, 177], [30, 0], clamp);
  return <AbsoluteFill><Backdrop seed={4}/><SectionTag>01 / The due diligence gap</SectionTag>
    <AbsoluteFill style={{justifyContent: 'center', padding: '0 150px 170px'}}>
      <Text style={{maxWidth: 1290, fontSize: 76, fontWeight: 680, lineHeight: 1.08, letterSpacing: -2.7, transform: `translateY(${titleY}px)`, opacity: titleOpacity}}>
        Every supplier decision<br/><span style={{color: C.blue}}>begins with</span> incomplete information.
      </Text>
      <Text style={{fontSize: 26, color: C.muted, marginTop: 26}}>A quotation gives you a price. Due diligence asks what supports the relationship.</Text>
      <div style={{display: 'flex', gap: 16, marginTop: 54}}>
        <ResearchCard opacity={cardOpacity} y={cardY} width={650} source="NIST  ·  SP 1326  ·  2026" title="Research pertinent supplier information" detail="Guide scope: ICT cyber supply chains" />
        <ResearchCard opacity={cardOpacity} y={cardY} width={650} source="OECD  ·  RESPONSIBLE BUSINESS OUTLOOK 2026" title="Fewer than 1 in 5 report evaluating supplier risk" detail="Large listed companies · environmental or human-rights criteria · Fig. 2.6" />
      </div>
      <Text style={{position: 'absolute', bottom: 105, left: 0, fontSize: 15, color: '#9baaba'}}>OECD disclosure indicators are partial proxies; the figures do not represent every business or all due diligence.</Text>
    </AbsoluteFill>
    <div style={{position: 'absolute', right: 78, top: 60, padding: '9px 14px', border: '1px solid #395168', borderRadius: 30, background: '#111923cc'}}><Kicker>Research context</Kicker></div>
  </AbsoluteFill>;
}

function ResearchCard({opacity, y, width, source, title, detail}) {
  return <div style={{width, minHeight: 160, opacity, transform: `translateY(${y}px)`, border: `1px solid ${C.edge}`, borderRadius: 20, background: 'linear-gradient(135deg,#121d28ed,#0e151eee)', padding: '23px 27px', boxShadow: '0 28px 70px #0007'}}>
    <Kicker>{source}</Kicker><Text style={{fontSize: 25, fontWeight: 650, marginTop: 14}}>{title}</Text><Text style={{fontSize: 17, color: C.muted, marginTop: 9}}>{detail}</Text>
  </div>;
}

const stages = ['Supplier identity', 'Recorded evidence', 'Screening context', 'Explainable indicators', 'Human review', 'Assessment report'];
function SceneTwo() {
  const f = useCurrentFrame();
  const reveal = interpolate(f, [10, 35], [0, 1], clamp);
  return <AbsoluteFill><Backdrop seed={21}/><SectionTag>02 / One traceable review path</SectionTag>
    <div style={{position: 'absolute', left: 114, top: 222, display: 'flex', alignItems: 'center', gap: 24, opacity: reveal, transform: `translateY(${interpolate(f,[10,35],[20,0],clamp)}px)`}}>
      <Shield size={80}/><div><Text style={{fontSize: 21, letterSpacing: 5, color: C.muted, fontWeight: 700}}>SUPPLIER</Text><Text style={{fontSize: 60, letterSpacing: -2, fontWeight: 720}}>TRUST</Text></div>
    </div>
    <Text style={{position: 'absolute', top: 390, left: 114, fontSize: 34, color: C.blue, fontWeight: 620, opacity: reveal}}>Evidence before decisions.</Text>
    <div style={{position: 'absolute', left: 114, right: 114, top: 573, display: 'flex', gap: 12}}>
      {stages.map((label, i) => {const on = interpolate(f,[54 + i*11,70 + i*11],[0,1],clamp);return <div key={label} style={{flex: 1, minHeight: 126, borderRadius: 16, border: `1px solid ${on ? '#4a9678' : C.edge}`, background: on ? '#10251f' : '#121923', padding: 20, opacity: on, transform: `translateY(${interpolate(f,[54+i*11,70+i*11],[22,0],clamp)}px)`}}><Text style={{color:C.green,fontSize:16,fontWeight:700,letterSpacing:2}}>0{i+1}</Text><Text style={{fontSize:20,fontWeight:620,marginTop:12,lineHeight:1.2}}>{label}</Text></div>})}
    </div>
    <Text style={{position: 'absolute', bottom: 80, left: 114, color: C.muted, fontSize: 19}}>An organized review surface for records, context and human judgment.</Text>
  </AbsoluteFill>;
}

function LiveDemo() {
  const f = useCurrentFrame();
  const scale = interpolate(f, [0, 25, 1620, 1678], [0.965, 1, 1, 0.985], clamp);
  return <AbsoluteFill style={{background: '#070a0e'}}>
    <OffthreadVideo src={staticFile('week02-live-workflow.webm')} startFrom={Math.ceil(liveMetadata.uiOffsetSeconds * 30)} muted style={{width: 1920, height: 1080, objectFit: 'cover', transform: `scale(${scale})`}} />
    <AbsoluteFill style={{background: 'linear-gradient(180deg,#07101945 0%,transparent 17%,transparent 73%,#080c12aa 100%)', pointerEvents: 'none'}} />
    <div style={{position: 'absolute', top: 30, left: 44, padding: '10px 15px', background: '#0b1118df', border: '1px solid #ffffff22', borderRadius: 12, backdropFilter: 'blur(8px)'}}><Text style={{fontSize:15, letterSpacing:1.5, fontWeight:700}}>SUPPLIERTRUST  /  FICTIONAL READ-ONLY DEMO</Text></div>
    <div style={{position:'absolute',right:44,top:30,padding:'10px 15px',background:'#0b1118df',border:'1px solid #ffffff22',borderRadius:12}}><Text style={{fontSize:15,letterSpacing:1.5,color:C.green,fontWeight:700}}>03  /  LIVE WORKFLOW</Text></div>
    <Text style={{position:'absolute',right:45,top:79,fontSize:14,color:'#d5e2ee',letterSpacing:0.5,background:'#071019dd',padding:'7px 11px',borderRadius:9}}>U.S. TREASURY · OFAC FAQ 5</Text>
  </AbsoluteFill>;
}

const architecture = [
  {title:'React', sub:'Workflow UI'},
  {title:'FastAPI', sub:'API boundary'},
  {title:'Evidence +\nscreening', sub:'Recorded context'},
  {title:'Deterministic\nassessment', sub:'Explainable factors'},
  {title:'Report', sub:'Text export'},
];
function SceneFour() {
  const f = useCurrentFrame();
  return <AbsoluteFill><Backdrop seed={70}/><SectionTag>04 / How the workflow is built</SectionTag>
    <Text style={{position:'absolute',top:156,left:112,fontSize:54,fontWeight:680,letterSpacing:-1.5}}>A deliberate path from record to report</Text>
    <div style={{position:'absolute',left:92,right:92,top:358,display:'flex',alignItems:'center',gap:14}}>
      {architecture.map((node,i)=>{const p=interpolate(f,[16+i*13,34+i*13],[0,1],clamp);return <React.Fragment key={node.title}>
        <div style={{flex:1,height:172,border:'1px solid #34485d',borderRadius:20,background:'linear-gradient(150deg,#172433,#101820)',padding:'26px 20px',opacity:p,transform:`translateY(${interpolate(f,[16+i*13,34+i*13],[20,0],clamp)}px)`,boxShadow:'0 22px 54px #0006'}}><Text style={{fontSize:25,fontWeight:700,lineHeight:1.12,whiteSpace:'pre-line'}}>{node.title}</Text><Text style={{fontSize:17,color:C.muted,marginTop:16}}>{node.sub}</Text></div>
        {i<architecture.length-1&&<Text style={{fontSize:28,color:C.green,opacity:interpolate(f,[24+i*13,42+i*13],[0,1],clamp)}}>→</Text>}
      </React.Fragment>})}
    </div>
    <div style={{position:'absolute',left:114,right:114,bottom:118,display:'flex',gap:22}}>
      <div style={{flex:1,borderLeft:'3px solid #63deb0',padding:'13px 22px',background:'#0d1716'}}><Text style={{fontSize:19,fontWeight:700}}>WRITABLE LOCAL APP</Text><Text style={{fontSize:17,color:C.muted,marginTop:8}}>PostgreSQL-backed supported workflow</Text></div>
      <div style={{flex:1,borderLeft:'3px solid #91b3f2',padding:'13px 22px',background:'#111823'}}><Text style={{fontSize:19,fontWeight:700}}>PUBLIC DEMONSTRATION</Text><Text style={{fontSize:17,color:C.muted,marginTop:8}}>Fixed fictional fixture · read-only · no visitor records</Text></div>
    </div>
  </AbsoluteFill>;
}

const strengths = ['One review path', 'Recorded evidence', 'Explainable indicators', 'Structured reporting'];
const limits = ['Fictional · read-only', 'Synthetic screening', 'Limited live integrations', 'Human verification required'];
function SceneFive() {
  const f = useCurrentFrame();
  const a = interpolate(f,[10,34],[0,1],clamp);
  return <AbsoluteFill><Backdrop seed={100}/><SectionTag>05 / Strengths and boundaries</SectionTag>
    <Text style={{position:'absolute',top:148,left:112,fontSize:56,fontWeight:690,letterSpacing:-1.7,opacity:a}}>Useful structure. Clear limits.</Text>
    <div style={{position:'absolute',left:112,right:112,top:286,bottom:105,display:'flex',gap:20}}>
      {[['WHAT IT SUPPORTS',strengths,C.green],['WHAT IT DOES NOT CLAIM',limits,C.blue]].map(([title,items,color],col)=><div key={title} style={{flex:1,padding:28,border:`1px solid ${C.edge}`,borderRadius:20,background:'#111923ee',opacity:interpolate(f,[24+col*10,48+col*10],[0,1],clamp),transform:`translateY(${interpolate(f,[24+col*10,48+col*10],[18,0],clamp)}px)`}}>
        <Kicker>{title}</Kicker>{items.map((item,i)=><Text key={item} style={{display:'flex',alignItems:'center',gap:16,fontSize:25,fontWeight:590,marginTop:22,color:'#e6edf4'}}><span style={{width:9,height:9,borderRadius:9,background:color,boxShadow:`0 0 18px ${color}88`}}/>{item}</Text>)}
      </div>)}
    </div>
    <Text style={{position:'absolute',bottom:104,left:112,color:C.muted,fontSize:17}}>A deterministic indicator is not a fraud prediction. SupplierTrust does not replace investigation or professional judgment.</Text>
  </AbsoluteFill>;
}

function SceneSix() {
  const f=useCurrentFrame();
  const opacity=interpolate(f,[0,18],[0,1],clamp);
  const scale=interpolate(f,[0,30],[0.91,1],clamp);
  return <AbsoluteFill><Backdrop seed={155}/><div style={{position:'absolute',inset:0,display:'flex',flexDirection:'column',alignItems:'center',justifyContent:'center',opacity,transform:`scale(${scale})`}}>
    <Shield size={96}/><Text style={{fontSize:62,fontWeight:720,letterSpacing:-2,marginTop:22}}>SupplierTrust</Text><Text style={{fontSize:25,letterSpacing:3,color:C.blue,fontWeight:700,marginTop:6}}>EVIDENCE BEFORE DECISIONS.</Text>
    <Text style={{fontSize:18,color:C.muted,marginTop:38}}>LIVE DEMO  ·  suppliertrust-ai-risk-intelligence.vercel.app</Text>
    <Text style={{fontSize:18,color:C.muted,marginTop:10}}>GITHUB  ·  risheeth26233/suppliertrust-ai-risk-intelligence</Text>
    <Text style={{fontSize:14,color:'#718092',marginTop:25,letterSpacing:3}}>WEEK 02  /  FICTIONAL DEMONSTRATION</Text>
  </div></AbsoluteFill>;
}

function Captions() {
  const frame=useCurrentFrame();
  const now=frame/30;
  const item=captions.find((x)=>now>=x.start&&now<x.end);
  if(!item)return null;
  const opacity=interpolate(frame,[item.start*30,item.start*30+6,item.end*30-6,item.end*30],[0,1,1,0],clamp);
  return <div style={{position:'absolute',left:150,right:150,bottom:35,display:'flex',justifyContent:'center',opacity,pointerEvents:'none'}}><Text style={{fontSize:22,fontWeight:620,textAlign:'center',lineHeight:1.24,background:'#070b10e8',border:'1px solid #6473856b',borderRadius:14,padding:'12px 19px',maxWidth:1520}}>{item.text}</Text></div>;
}

export function SupplierTrustFilm() {
  return <AbsoluteFill style={{background:C.bg,overflow:'hidden'}}>
    <Sequence from={0} durationInFrames={820}><SceneOne/></Sequence>
    <Sequence from={820} durationInFrames={317}><SceneTwo/></Sequence>
    <Sequence from={1137} durationInFrames={1662}><LiveDemo/></Sequence>
    <Sequence from={2799} durationInFrames={369}><SceneFour/></Sequence>
    <Sequence from={3168} durationInFrames={312}><SceneFive/></Sequence>
    <Sequence from={3480} durationInFrames={120}><SceneSix/></Sequence>
    <Captions/>
  </AbsoluteFill>;
}
