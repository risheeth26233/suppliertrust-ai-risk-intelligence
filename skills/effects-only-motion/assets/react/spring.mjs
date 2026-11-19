// Original finite spring sampler. No shared clock, timers, canvas, or runtime dependencies.
export function sampleSpring(from, to, {stiffness=420, damping=32, mass=1, duration=0.42}={}) {
  if (![from,to,stiffness,damping,mass,duration].every(Number.isFinite) || stiffness<=0 || damping<=0 || mass<=0 || duration<=0) throw new RangeError('Spring values must be finite and physical parameters positive.');
  const frames=[];let x=from,v=0;const count=Math.min(240,Math.max(2,Math.ceil(duration*120)));const dt=duration/count;
  for(let i=0;i<=count;i++) {frames.push({value:x,offset:i/count});const substeps=Math.max(1,Math.ceil(dt/.004));for(let j=0;j<substeps;j++){const h=dt/substeps;v+=(-stiffness*(x-to)-damping*v)/mass*h;x+=v*h;}}
  frames[frames.length-1].value=to;return frames;
}
