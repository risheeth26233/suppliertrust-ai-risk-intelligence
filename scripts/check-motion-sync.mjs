import assert from 'node:assert/strict';
import {readFile} from 'node:fs/promises';
import path from 'node:path';
import {fileURLToPath} from 'node:url';

const root=fileURLToPath(new URL('..',import.meta.url));
for(const name of ['spring.mjs','hooks.js','components.jsx','motion.css']){
 const app=await readFile(path.join(root,'frontend','src','motion',name));
 const skill=await readFile(path.join(root,'skills','effects-only-motion','assets','react',name));
 assert.deepEqual(skill,app,`${name} differs between the reusable skill and the app`);
}
console.log('Reusable motion skill assets match the SupplierTrust library.');
