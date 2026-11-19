import {API} from '../app/config.jsx';
export async function request(path,options={}){const r=await fetch(API+path,{...options,headers:{...(options.body instanceof FormData?{}:{'Content-Type':'application/json'}),...options.headers}});if(!r.ok){const x=await r.json().catch(()=>({}));throw Error(typeof x.detail==='string'?x.detail:'Please check the form and try again.')}return r.json()}
