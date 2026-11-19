import {useCallback, useEffect, useLayoutEffect, useRef} from 'react';
import {sampleSpring} from './spring.mjs';
export const motionOff=el=>typeof matchMedia==='undefined'||matchMedia('(prefers-reduced-motion: reduce)').matches||Boolean(el?.closest('[data-motion="off"]'));
export function useMotion(){
 const animations=useRef(new Set());
 const cancel=useCallback(()=>{for(const a of animations.current)a.cancel();animations.current.clear()},[]);
 useEffect(()=>{const media=matchMedia('(prefers-reduced-motion: reduce)');const stop=()=>{if(media.matches||document.hidden)cancel()};media.addEventListener('change',stop);document.addEventListener('visibilitychange',stop);return()=>{cancel();media.removeEventListener('change',stop);document.removeEventListener('visibilitychange',stop)}},[cancel]);
 const play=useCallback((el,frames,options={})=>{cancel();if(!el||motionOff(el)||!el.animate)return;const a=el.animate(frames,{duration:420,easing:'linear',...options});animations.current.add(a);a.onfinish=()=>animations.current.delete(a);a.oncancel=()=>animations.current.delete(a);return a},[cancel]);
 return {play,cancel};
}
export function useSlidingIndicator(ref,selected){
 const {play}=useMotion();const previous=useRef(null);
 useLayoutEffect(()=>{const root=ref.current;if(!root)return;const indicator=root.querySelector('[data-motion-indicator]');const active=root.querySelector('[aria-current="page"],[aria-selected="true"]');if(!indicator||!active)return;
 const measure=()=>{const box={x:active.offsetLeft,y:active.offsetTop+active.offsetHeight-2,w:active.offsetWidth};indicator.style.width=`${box.w}px`;indicator.style.transform=`translate(${box.x}px,${box.y}px)`;
 const old=previous.current;if(old&&old.w&&box.w)play(indicator,sampleSpring(0,1).map(({value:t,offset})=>({offset,transform:`translate(${old.x+(box.x-old.x)*t}px,${old.y+(box.y-old.y)*t}px) scaleX(${(old.w+(box.w-old.w)*t)/box.w})`})));previous.current=box};
 measure();const observer=new ResizeObserver(measure);observer.observe(root);observer.observe(active);return()=>observer.disconnect();},[ref,selected,play]);
}
export function useReveal(ref,identity){const {play}=useMotion();useEffect(()=>{play(ref.current,[{opacity:.7,transform:'translateY(4px)'},{opacity:1,transform:'translateY(0)'}],{duration:180,easing:'cubic-bezier(.22,1,.36,1)'})},[identity,play,ref]);}
