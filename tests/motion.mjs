import assert from 'node:assert/strict';
import {mkdir, readFile} from 'node:fs/promises';
import {spawn} from 'node:child_process';
import {fileURLToPath} from 'node:url';
import path from 'node:path';
import {chromium} from '../frontend/node_modules/playwright/index.mjs';
import {sampleSpring} from '../frontend/src/motion/spring.mjs';

const root=fileURLToPath(new URL('..',import.meta.url));
const output=path.join(root,'output','motion-playground');
const frontend=path.join(root,'frontend');
const port=5193;
const origin=`http://127.0.0.1:${port}`;
const frames=sampleSpring(0,1);
assert.equal(frames[0].value,0);
assert.equal(frames.at(-1).value,1);
assert.ok(frames.every((frame,i)=>Number.isFinite(frame.value)&&frame.offset>=0&&frame.offset<=1&&(i===0||frame.offset>frames[i-1].offset)));
assert.ok(frames.some(frame=>frame.value>1),'spring has controlled overshoot');
assert.throws(()=>sampleSpring(0,1,{mass:0}),RangeError);
const source=await Promise.all(['spring.mjs','hooks.js','components.jsx','motion.css'].map(name=>readFile(path.join(frontend,'src','motion',name),'utf8')));
assert.ok(source.every(text=>!/[\u3040-\u30ff\u3400-\u9fff]/u.test(text)),'motion source contains no Japanese lettering');
assert.ok(!source.join('\n').includes('<canvas'),'motion library does not create a canvas layer');
await mkdir(output,{recursive:true});

const server=spawn(process.execPath,['node_modules/vite/bin/vite.js','--host','127.0.0.1','--port',String(port),'--strictPort'],{cwd:frontend,stdio:'ignore'});
let browser;
try{
 let ready=false;
 for(let i=0;i<80;i++){
  if(server.exitCode!==null)throw Error('Vite playground server exited before becoming ready');
  try{const response=await fetch(`${origin}/dev/motion.html`);if(response.ok){ready=true;break}}catch{}
  await new Promise(resolve=>setTimeout(resolve,150));
 }
 assert.ok(ready,'local playground starts');
 browser=await chromium.launch({headless:true,...(process.env.PW_CHANNEL?{channel:process.env.PW_CHANNEL}:{})});
 const page=await browser.newPage({viewport:{width:1440,height:1100}});
 const errors=[];
 page.on('pageerror',error=>errors.push(error.message));
 page.on('console',message=>{if(message.type()==='error')errors.push(message.text())});
 await page.goto(`${origin}/dev/motion.html`);
 await page.getByRole('heading',{name:'Effects-only motion'}).waitFor();
 await page.screenshot({path:path.join(output,'motion-playground-desktop.png'),fullPage:true});

 const primary=page.getByRole('button',{name:/Open investigation/});
 const hover=page.getByRole('button',{name:'Hover / keyboard focus'});
 await hover.hover();
 await page.waitForTimeout(170);
 assert.equal(await hover.evaluate(button=>getComputedStyle(button).filter),'brightness(1.07)','hover feedback is visible');
 const pressed=page.getByRole('button',{name:'Advance review'});
 const box=await pressed.boundingBox();
 await page.mouse.move(box.x+box.width/2,box.y+box.height/2);
 await page.mouse.down();
 assert.equal(await pressed.evaluate(button=>getComputedStyle(button).scale),'0.985','active feedback compresses the control');
 await page.mouse.up();
 await page.getByRole('switch',{name:'Reduce motion'}).focus();
 await page.keyboard.press('Tab');
 assert.equal(await primary.evaluate(button=>button.matches(':focus-visible')),true,'keyboard focus is visible');
 await page.keyboard.press('Enter');
 const burst=primary.locator('svg.motion-burst');
 await burst.waitFor({state:'attached'});
 for(const [time,name] of [[90,'motion-primary-090ms.png'],[220,'motion-primary-220ms.png'],[360,'motion-primary-360ms.png']]){
  await primary.evaluate((button,currentTime)=>{for(const animation of button.getAnimations({subtree:true})){animation.pause();animation.currentTime=currentTime}},time);
  await page.screenshot({path:path.join(output,name),fullPage:true});
 }
 assert.equal(await burst.locator('text,path,image,use').count(),0,'impact effect uses geometry only');
 const motionMarkup=await page.locator('.playground').innerText();
 assert.ok(!/[\u3040-\u30ff\u3400-\u9fff]/u.test(motionMarkup),'rendered playground contains no Japanese lettering');

 await page.getByRole('tab',{name:'Evidence'}).click();
 await page.getByRole('tabpanel').getByText('Evidence keeps its selected state',{exact:false}).waitFor();
 await page.getByRole('tab',{name:'Evidence'}).focus();
 await page.keyboard.press('ArrowRight');
 assert.equal(await page.getByRole('tab',{name:'Report'}).getAttribute('aria-selected'),'true','tabs support arrow navigation');
 await page.getByRole('switch',{name:'Screening context enabled'}).uncheck();
 assert.equal(await page.getByRole('switch',{name:'Screening context enabled'}).isChecked(),false);
 await page.getByRole('button',{name:'Hover or focus for context'}).focus();
 await page.getByRole('tooltip').waitFor();
 await page.keyboard.press('Escape');
 await page.getByRole('tooltip').waitFor({state:'detached'});
 await page.getByLabel('Work email').fill('not-an-email');
 await page.getByRole('button',{name:'Reset sample'}).focus();
 assert.equal(await page.getByLabel('Work email').getAttribute('aria-invalid'),'true','invalid input is described and marked');
 await page.getByText('Enter a valid email address.').waitFor();

 const complete=page.getByRole('button',{name:'Complete next step'});
 for(let i=0;i<3;i++)await complete.click();
 assert.equal(await page.locator('.motion-progress').locator('progress').getAttribute('value'),'100','progress reaches completion through actions');
 await page.getByRole('status').getByText('State updated',{exact:false}).waitFor();
 await page.getByRole('button',{name:'Dismiss notification'}).click();
 await page.waitForTimeout(180);

 const sample=page.getByTestId('mount-sample');
 await sample.click();
 await sample.evaluate(button=>{window.__sampleAnimations=button.getAnimations({subtree:true})});
 assert.ok(await sample.evaluate(button=>button.getAnimations().length>0),'sample starts a finite press animation');
 await page.getByRole('button',{name:'Unmount sample'}).click();
 assert.equal(await page.getByTestId('mount-sample').count(),0,'sample unmounted');
 assert.ok(await page.evaluate(()=>window.__sampleAnimations.every(animation=>animation.playState==='idle')),'unmount cancels component animations');
 await page.getByRole('button',{name:'Dismiss notification'}).click();
 await page.waitForTimeout(180);

 await page.emulateMedia({reducedMotion:'reduce'});
 await primary.click();
 assert.equal(await page.locator('svg.motion-burst').count(),0,'system reduced-motion preference suppresses decorative effects');
 await page.getByRole('button',{name:'Dismiss notification'}).click();
 await page.emulateMedia({reducedMotion:'no-preference'});
 await page.getByRole('switch',{name:'Reduce motion'}).check();
 await primary.click();
 assert.equal(await page.locator('svg.motion-burst').count(),0,'workspace motion-off setting suppresses decorative effects');
 await page.getByRole('button',{name:'Dismiss notification'}).click();
 await page.goto(`${origin}/dev/motion.html`);
 await page.getByRole('heading',{name:'Effects-only motion'}).waitFor();
 await page.getByRole('switch',{name:'Reduce motion'}).check();
 await page.screenshot({path:path.join(output,'motion-playground-reduced.png'),fullPage:true});
 await page.setViewportSize({width:375,height:812});
 await page.goto(`${origin}/dev/motion.html`);
 await page.getByRole('heading',{name:'Effects-only motion'}).waitFor();
 await page.getByRole('switch',{name:'Reduce motion'}).check();
 assert.ok(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth),'mobile playground has no horizontal overflow');
 await page.screenshot({path:path.join(output,'motion-playground-mobile.png'),fullPage:true});
 assert.deepEqual(errors,[],'browser console and page have no errors');
 console.log('Motion sampler, geometry-only effects, button/tab/toggle/progress/toast/tooltip/input states, cleanup, reduced motion and mobile layout passed. Screenshots saved under output/motion-playground/.');
}finally{
 await browser?.close();
 server.kill();
}
