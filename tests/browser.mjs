import assert from 'node:assert/strict';
import {mkdir} from 'node:fs/promises';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {chromium} from '../frontend/node_modules/playwright/index.mjs';
const base=process.env.SUPPLIERTRUST_FRONTEND_URL||'http://127.0.0.1:5173';
const demoBase=process.env.SUPPLIERTRUST_DEMO_URL||'http://127.0.0.1:5174';
const out=path.join(fileURLToPath(new URL('..',import.meta.url)),'output','playwright');await mkdir(out,{recursive:true});
const browser=await chromium.launch({headless:true,...(process.env.PW_CHANNEL?{channel:process.env.PW_CHANNEL}:{})});
const errors=[];const p=await browser.newPage({viewport:{width:1440,height:1000},acceptDownloads:true});
p.on('pageerror',e=>errors.push(e.message));p.on('console',m=>{if(m.type()==='error')errors.push(m.text())});p.on('dialog',d=>d.accept());
const tab=async(name)=>{await p.locator('.investigation-tabs').getByRole('button',{name,exact:true}).click()};
const heading=async(name)=>p.getByRole('heading',{level:1,name,exact:true}).waitFor();
try{
 await p.goto(base);await heading('Command Center');
 await p.getByRole('button',{name:'Supplier Directory',exact:true}).click();await heading('Supplier directory');
 await p.getByRole('button',{name:/Add supplier/}).first().click();
 const name='Fictional Example Trading Co';
 await p.getByLabel('Legal business name').fill(name);await p.getByLabel('Category',{exact:true}).fill('Manufacturing');await p.getByLabel('Country',{exact:true}).fill('India');await p.getByLabel('GSTIN / CIN or other identifier').fill('27AAPFU0939F1ZV');
 await p.getByRole('button',{name:/Save supplier/}).click();await heading(name);
 await tab('Risk');await heading('Risk assessment');
 assert.equal(await p.locator('.nav-link.selected').count(),1);
 await p.locator('.investigation-tabs button').filter({hasText:'Evidence'}).click();
 await p.getByLabel('Source URL',{exact:true}).fill('https://example.com/source');await p.getByLabel('Reviewer',{exact:true}).fill('QA reviewer');await p.getByLabel('Reviewer notes').fill('Fictional source for browser regression');await p.getByRole('button',{name:'Save evidence'}).click();
 await p.locator('.source-list button').first().waitFor();await p.locator('.source-detail').getByText('QA reviewer',{exact:true}).waitFor();
 await tab('Performance');await p.getByLabel('Observation date').fill('2026-01-15');await p.getByLabel('Reviewer',{exact:true}).fill('QA reviewer');await p.getByLabel('On-time delivery %').fill('92');await p.getByLabel('Defect rate %').fill('2');await p.getByLabel('Source URL').fill('https://example.com/performance');await p.getByLabel('Notes',{exact:true}).fill('Fictional operational observation');await p.getByRole('button',{name:'Save observation'}).click();await p.getByText('Performance observation recorded',{exact:true}).waitFor();
 await tab('Screening');
 const fixture=p.getByRole('button',{name:'Screen against Synthetic browser fixture'});if(await fixture.count()) {await fixture.click();await p.getByRole('button',{name:'False positive',exact:true}).click();await p.getByLabel('Reviewer',{exact:true}).fill('QA reviewer');await p.getByLabel('Rationale').fill('Fictional fixture workflow');await p.getByRole('button',{name:'Save review'}).click();await p.getByText('false positive',{exact:true}).waitFor()}
 await tab('Activity');await p.getByText('performance observed',{exact:true}).waitFor();
 await tab('Report');await p.getByText('SUPPLIERTRUST — DUE DILIGENCE REPORT',{exact:false}).waitFor();let download=p.waitForEvent('download');await p.getByRole('button',{name:'Download .txt'}).click();assert.match((await download).suggestedFilename(),/supplier-\d+-report\.txt/);
 await tab('Overview');await p.getByRole('button',{name:'Delete supplier',exact:true}).click();await heading('Supplier directory');
 await p.goto(demoBase);await heading('Command Center');await p.getByText('Northstar Components Ltd. (Fictional)',{exact:true}).waitFor();
 await p.getByRole('button',{name:'Supplier Directory',exact:true}).click();await heading('Supplier directory');await p.getByRole('button',{name:/Open investigation/}).click();
 await heading('Northstar Components Ltd. (Fictional)');const profileUrl=p.url();await tab('Risk');await p.goBack();await heading('Northstar Components Ltd. (Fictional)');await p.goForward();await heading('Risk assessment');
 await p.locator('.factor-item summary').first().click();await p.locator('.factor-item[open]').getByText('No direct factor-to-evidence association is supplied by the API.',{exact:false}).waitFor();
 await p.getByRole('button',{name:'Inspect recorded evidence',exact:true}).first().click();await heading('Evidence explorer');
 const entries=p.locator('.source-list button');assert.ok(await entries.count()>0);await entries.last().click();assert.equal(await entries.last().getAttribute('aria-pressed'),'true');
 for(const forbidden of ['Save evidence','Save observation','Delete supplier','False positive','Confirm match','Refresh official OFAC dataset'])assert.equal(await p.getByRole('button',{name:forbidden,exact:true}).count(),0);
 assert.equal(await p.locator('input[type=file],button:has(svg.lucide-info)').count(),0);
 const supplierPath=new URL(profileUrl).pathname;
 const routes=[['command','/'],['directory','/suppliers'],['identity',supplierPath],['risk',supplierPath+'/risk'],['evidence',supplierPath+'/evidence'],['screening',supplierPath+'/screening'],['performance',supplierPath+'/performance'],['activity',supplierPath+'/activity'],['report',supplierPath+'/report'],['help','/about']];
 for(const width of [320,375,390,768,1024,1280,1440,1920]){
  await p.setViewportSize({width,height:900});
  for(const [label,path] of routes){await p.goto(demoBase+path);await p.locator('h1').waitFor();if(!['command','directory','help'].includes(label))await p.locator('.workspace-context').waitFor();await p.waitForTimeout(240);assert.ok(await p.evaluate(()=>document.documentElement.scrollWidth<=innerWidth),`${label} horizontal overflow at ${width}`);await p.screenshot({path:`${out}/v2-${label}-${width}.png`,fullPage:true,animations:'disabled'})}
 }
 await p.setViewportSize({width:375,height:812});await p.goto(demoBase);await heading('Command Center');await p.getByRole('button',{name:'Open navigation'}).click();assert.equal(await p.locator('.main-area').getAttribute('aria-hidden'),'true');await p.keyboard.press('Escape');assert.equal(await p.evaluate(()=>document.activeElement?.getAttribute('aria-label')),'Open navigation');
 const titles=['Welcome to SupplierTrust','Start with what is recorded','Open a supplier investigation','Read the concern index','Trace evidence to its source','Screening requires judgment','Keep observations in context','Take the assessment with you'];
 await p.setViewportSize({width:320,height:480});
 const tourTrigger=p.getByRole('button',{name:'Take product tour',exact:true});
 await tourTrigger.click();
 const tour=p.locator('.tour-card');
 await p.getByRole('dialog',{name:titles[0]}).waitFor();
 await p.locator('.tour-close').click();
 await p.getByRole('dialog').waitFor({state:'detached'});
 await p.waitForTimeout(150);
 assert.equal(await tourTrigger.evaluate(el=>el===document.activeElement),true);
 await tourTrigger.click();
 const close=p.getByRole('button',{name:'Close product tour'});
 await close.focus();await p.keyboard.press('Shift+Tab');
 const next=p.getByRole('button',{name:'Next',exact:true});
 assert.equal(await next.evaluate(el=>el===document.activeElement),true);
 await p.keyboard.press('Tab');
 assert.equal(await close.evaluate(el=>el===document.activeElement),true);
 assert.equal(await close.evaluate(el=>getComputedStyle(el).outlineStyle!=='none'),true);
 await p.keyboard.press('Escape');await p.getByRole('dialog').waitFor({state:'detached'});
 await p.waitForTimeout(150);
 assert.equal(await tourTrigger.evaluate(el=>el===document.activeElement),true);
 await tourTrigger.click();
 for(let i=0;i<titles.length;i++){
  await p.getByRole('dialog',{name:titles[i]}).waitFor();
  await p.locator('.tour-focus').first().waitFor({state:'attached'});
  const layout=await tour.evaluate(card=>{
   const rect=el=>{const r=el.getBoundingClientRect();return {x:r.x,y:r.y,width:r.width,height:r.height,right:r.right,bottom:r.bottom}};
   const header=card.querySelector('.tour-progress'),label=header.querySelector('span:first-child'),count=header.querySelector('.tour-step-count'),close=header.querySelector('.tour-close'),bar=card.querySelector('[role="progressbar"]'),fill=bar.querySelector('i'),action=card.querySelector('.tour-actions .button-primary'),box=rect(card),style=getComputedStyle(card),paddingLeft=parseFloat(style.paddingLeft)+parseFloat(style.borderLeftWidth),paddingRight=parseFloat(style.paddingRight)+parseFloat(style.borderRightWidth);
   return {box,label:rect(label),count:rect(count),close:rect(close),header:rect(header),bar:rect(bar),action:rect(action),stepLabel:count.getAttribute('aria-label'),progressNow:Number(bar.getAttribute('aria-valuenow')),fillWidth:parseFloat(fill.style.width),fits:box.x>=0&&box.y>=0&&box.right<=innerWidth&&box.bottom<=innerHeight,contentFits:card.scrollHeight<=card.clientHeight,noOverlap:label.getBoundingClientRect().right<=count.getBoundingClientRect().left&&count.getBoundingClientRect().right<=close.getBoundingClientRect().left,progressBelowHeader:bar.getBoundingClientRect().top>=header.getBoundingClientRect().bottom,progressAligned:bar.getBoundingClientRect().left>=box.x+paddingLeft-1&&bar.getBoundingClientRect().right<=box.right-paddingRight+1};
  });
  assert.ok(layout.fits,`Tour dialog escapes 320x480 at step ${i+1}`);
  assert.ok(layout.contentFits,`Tour content requires scrolling at step ${i+1}`);
  assert.ok(layout.noOverlap,`Tour header overlaps at step ${i+1}`);
  assert.ok(layout.close.width>=44&&layout.close.height>=44,`Close target is too small at step ${i+1}`);
  assert.ok(layout.progressBelowHeader&&layout.progressAligned,`Progress bar is misaligned at step ${i+1}`);
  assert.equal(layout.stepLabel,`Step ${i+1} of 8`);
  assert.equal(layout.progressNow,i+1);
  assert.equal(layout.fillWidth,(i+1)/8*100);
  assert.ok(layout.action.height>=44,`Tour action target is too small at step ${i+1}`);
  assert.ok(await p.evaluate(()=>document.documentElement.scrollWidth<=innerWidth),`Tour overflow at step ${i+1}`);
  await p.screenshot({path:path.join(out,`v2-tour-step-${i+1}-320.png`),animations:'disabled'});
  if(i<titles.length-1)await next.click();
 }
 await p.getByRole('button',{name:'Finish',exact:true}).click();
 await p.getByRole('dialog').waitFor({state:'detached'});
 await p.waitForTimeout(150);
 assert.equal(await tourTrigger.evaluate(el=>el===document.activeElement),true);
 await heading('Command Center');assert.deepEqual(errors,[]);console.log('SupplierTrust 2.0: local writes, demo investigation, history, evidence, reports, eight tour steps, keyboard focus, and 80 responsive page checks passed.');
}finally{await browser.close()}
