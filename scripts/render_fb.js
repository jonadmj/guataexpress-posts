// Renderiza la versión para Facebook de un carrusel HTML: quita "Desliza →" y los contadores de página (1/4…).
// Uso: node scripts/render_fb.js <archivo.html> <prefijo_salida>   → <prefijo>-1.png, -2.png…
const {chromium}=require('playwright');const path=require('path');
(async()=>{const [html,out]=process.argv.slice(2);
const b=await chromium.launch();const p=await b.newPage({viewport:{width:1080,height:1350}});
await p.goto('file://'+path.resolve(html));await p.evaluate(()=>document.fonts.ready);
await p.evaluate(()=>{
  document.querySelectorAll('.pg').forEach(e=>e.remove());
  const w=document.createTreeWalker(document.body,NodeFilter.SHOW_TEXT);const hits=[];
  while(w.nextNode()){if(/desliza/i.test(w.currentNode.textContent))hits.push(w.currentNode);}
  for(const t of hits){
    const sw=t.parentElement.closest('.swipe');
    if(sw){sw.remove();continue;}
    let prev=t.previousSibling; if(prev&&prev.nodeName==='BR')prev.remove();
    t.textContent=t.textContent.replace(/desliza\s*→?/i,'');
  }
});
await p.waitForTimeout(400);
const n=await p.locator('section').count();
for(let i=1;i<=n;i++){await p.locator('#s'+i).screenshot({path:`${out}-${i}.png`});}
await b.close();console.log(n+' diapositivas');})();
