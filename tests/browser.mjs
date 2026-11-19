import assert from 'node:assert/strict';
import {mkdir} from 'node:fs/promises';
import {chromium} from '../frontend/node_modules/playwright/index.mjs';
const base=process.env.SUPPLIERTRUST_FRONTEND_URL||'http://127.0.0.1:5173';
const demoBase=process.env.SUPPLIERTRUST_DEMO_URL||'http://127.0.0.1:5174';
const out='output/playwright';await mkdir(out,{recursive:true});
const browser=await chromium.launch({headless:true,...(process.env.PW_CHANNEL?{channel:process.env.PW_CHANNEL}:{})});
const errors=[];const p=await browser.newPage({viewport:{width:1440,height:1000},acceptDownloads:true});
p.on('pageerror',e=>errors.push(e.message));p.on('console',m=>{if(m.type()==='error')errors.push(m.text())});p.on('dialog',d=>d.accept());
const tab=async(name)=>{await p.locator('.investigation-tabs').getByRole('button',{name,exact:true}).click()};
const heading=async(name)=>p.getByRole('heading',{level:1,name,exact:true}).waitFor();
try{
 await p.goto(base);await heading('Command Center');
 await p.getByRole('button',{name:'Supplier Directory',exact:true}).click();await heading('Supplier directory');
 await p.getByRole('button',{name:/Add supplier/}).first().click();
 const name=`V2 Workflow ${Date.now()}`;
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
 for(const width of [375,390,768,1024,1280,1440]){
  await p.setViewportSize({width,height:900});
  for(const [label,path] of routes){await p.goto(demoBase+path);await p.locator('h1').waitFor();if(!['command','directory','help'].includes(label))await p.locator('.workspace-context').waitFor();await p.waitForTimeout(240);assert.ok(await p.evaluate(()=>document.documentElement.scrollWidth<=innerWidth),`${label} horizontal overflow at ${width}`);await p.screenshot({path:`${out}/v2-${label}-${width}.png`,fullPage:true,animations:'disabled'})}
 }
 await p.setViewportSize({width:375,height:812});await p.goto(demoBase);await heading('Command Center');await p.getByRole('button',{name:'Open navigation'}).click();assert.equal(await p.locator('.main-area').getAttribute('aria-hidden'),'true');await p.keyboard.press('Escape');assert.equal(await p.evaluate(()=>document.activeElement?.getAttribute('aria-label')),'Open navigation');
 await p.getByRole('button',{name:'Take product tour',exact:true}).click();
 const titles=['Welcome to SupplierTrust','Start with what is recorded','Open a supplier investigation','Read the concern index','Trace evidence to its source','Screening requires judgment','Keep observations in context','Take the assessment with you'];
 for(let i=0;i<titles.length;i++){await p.getByRole('dialog',{name:titles[i]}).waitFor();await p.locator('.tour-focus').first().waitFor({state:'attached'});await p.getByRole('button',{name:i===titles.length-1?'Finish':'Next',exact:true}).click()}
 await heading('Command Center');assert.deepEqual(errors,[]);console.log('SupplierTrust 2.0: local writes, demo investigation, history, evidence, reports, tour, keyboard drawer and 60 responsive page checks passed.');
}finally{await browser.close()}
