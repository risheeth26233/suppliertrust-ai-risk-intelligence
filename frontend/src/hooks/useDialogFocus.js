import {useEffect, useRef} from 'react';
export function useDialogFocus(onClose){
 const ref=useRef(null);const closeRef=useRef(onClose);closeRef.current=onClose;
 useEffect(()=>{const previous=document.activeElement;const root=ref.current;root?.querySelector('button,input,select,textarea')?.focus();const key=e=>{if(e.key==='Escape'){e.preventDefault();closeRef.current();return}if(e.key!=='Tab')return;const controls=[...root.querySelectorAll('button:not(:disabled),input,select,textarea,a[href]')];const first=controls[0],last=controls.at(-1);if(e.shiftKey&&document.activeElement===first){e.preventDefault();last?.focus()}else if(!e.shiftKey&&document.activeElement===last){e.preventDefault();first?.focus()}};root?.addEventListener('keydown',key);return()=>{root?.removeEventListener('keydown',key);previous?.focus?.()}},[]);
 return ref;
}
