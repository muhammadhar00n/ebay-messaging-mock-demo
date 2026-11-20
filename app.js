// app.js — mock demo logic (no eBay calls)
const samplePage = `
<!-- Sample listings HTML (simulated) -->
<div class="item"><a href="/itm/123">Item A</a><span class="seller">Seller: best_seller_123</span></div>
<div class="item"><a href="/itm/456">Item B</a><span class="seller">Seller: coolstore_88</span></div>
<div class="item"><a href="/itm/789">Item C</a><span class="seller">Seller: vintage-hub</span></div>
<div class="item"><a href="/itm/111">Item D</a><span class="seller">Seller: ali_seller</span></div>
`;

function log(msg){
  const el = document.getElementById('logArea');
  const ts = new Date().toLocaleTimeString();
  el.textContent = `[${ts}] ${msg}\n` + el.textContent;
}

function extractSellersFromHtml(html){
  const sellers = new Set();
  const re1 = /Seller:\s*([A-Za-z0-9_\-\.]+)/gi;
  let m;
  while((m = re1.exec(html)) !== null) sellers.add(m[1]);
  const re2 = /data-seller=["']([A-Za-z0-9_\-\.]+)["']/gi;
  while((m = re2.exec(html)) !== null) sellers.add(m[1]);
  const re3 = /\/usr\/([A-Za-z0-9_\-\.]+)/gi;
  while((m = re3.exec(html)) !== null) sellers.add(m[1]);
  const re4 = /seller[\s'">:=]+([A-Za-z0-9_\-\.]+)/gi;
  while((m = re4.exec(html)) !== null) sellers.add(m[1]);
  return Array.from(sellers);
}

document.getElementById('loadSample').addEventListener('click', ()=>{
  document.getElementById('rawHtml').value = samplePage;
  log('Loaded sample listings HTML into the raw HTML area.');
});

document.getElementById('scanBtn').addEventListener('click', ()=>{
  let raw = document.getElementById('rawHtml').value.trim();
  if(!raw) raw = samplePage;
  const sellers = extractSellersFromHtml(raw);
  const list = document.getElementById('sellersList');
  list.innerHTML = '';
  sellers.forEach(s => {
    const div = document.createElement('div');
    div.className = 'seller';
    div.innerHTML = `<div><strong>${s}</strong><div style="font-size:12px;color:#64748b;">Sample item found</div></div>
                     <div><button class="ghost small" onclick="addToQueue('${s}')">Add</button></div>`;
    list.appendChild(div);
  });
  document.getElementById('countBadge').textContent = sellers.length + ' sellers';
  log('Scan complete — ' + sellers.length + ' sellers found.');
});

window.addToQueue = function(seller){
  const q = document.getElementById('queueArea');
  const id = 'q-'+seller;
  if(document.getElementById(id)){ log('Seller ' + seller + ' already in queue.'); return; }
  const el = document.createElement('div');
  el.id = id;
  el.className = 'seller';
  el.innerHTML = `<div>${seller}</div>
    <div>
      <button class="ghost" onclick="previewMessage('${seller}')">Preview</button>
      <button onclick="removeFromQueue('${seller}')" class="ghost">Remove</button>
    </div>`;
  q.appendChild(el);
  log('Added ' + seller + ' to queue.');
};

window.removeFromQueue = function(seller){
  const id = 'q-'+seller;
  const el = document.getElementById(id);
  if(el) el.remove();
  log('Removed ' + seller + ' from queue.');
};

function buildMessageForSeller(seller){
  const tmpl = document.getElementById('template').value;
  const name = document.getElementById('yourName').value || 'You';
  return tmpl.replace(/{{seller}}/g, seller).replace(/{{yourName}}/g, name);
}

window.previewMessage = function(seller){
  const msg = buildMessageForSeller(seller);
  showModal(seller, msg, false);
};

document.getElementById('queueBtn').addEventListener('click', ()=>{
  const q = document.getElementById('queueArea');
  const first = q.querySelector('.seller');
  if(!first){ alert('Queue is empty — add sellers first.'); return; }
  const seller = first.firstChild.textContent.trim();
  const msg = buildMessageForSeller(seller);
  showModal(seller, msg, true);
});

document.getElementById('autoBtn').addEventListener('click', async ()=>{
  const q = document.getElementById('queueArea');
  const items = Array.from(q.querySelectorAll('.seller')).map(e => e.firstChild.textContent.trim());
  if(items.length===0){ alert('Queue empty — add sellers first.'); return; }
  log('Starting simulated auto-send for ' + items.length + ' sellers (demo only).');
  for(let i=0;i<items.length;i++){
    const s = items[i];
    const m = buildMessageForSeller(s);
    log(`(AUTO) Simulated send to ${s}: "${m.slice(0,60)}${m.length>60?'...':''}"`);
    const el = document.getElementById('q-'+s);
    if(el) el.style.opacity = 0.6;
    await new Promise(r => setTimeout(r, 900 + Math.random()*700));
  }
  log('Auto-send simulation complete.');
});

function showModal(seller, message, semiAuto){
  const root = document.getElementById('modalRoot');
  root.style.display = 'block';
  root.innerHTML = `<div class="modal">
    <div class="modal-card">
      <h3>Message preview — ${seller}</h3>
      <div style="margin:8px 0 12px;padding:12px;border-radius:8px;border:1px solid #eef2ff;background:#fbfdff;">${escapeHtml(message)}</div>
      <div style="display:flex;gap:8px;justify-content:flex-end;">
        ${semiAuto?'<button id="sendBtn">Send</button>':''}
        <button id="cancelBtn" class="ghost">Cancel</button>
      </div>
    </div>
  </div>`;
  document.getElementById('cancelBtn').onclick = ()=>{ root.style.display='none'; log('Modal closed (no send).'); };
  if(semiAuto){
    document.getElementById('sendBtn').onclick = ()=>{
      root.style.display='none';
      log(`(SEMI) Simulated send to ${seller}: "${message.replace(/\n/g,' ')}"`);
      const el = document.getElementById('q-'+seller);
      if(el) el.remove();
    };
  }
}

function escapeHtml(str){ return str.replace(/[&<>"']/g, function(m){ return {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[m]; }); }

document.getElementById('clearLog').addEventListener('click', ()=>{
  document.getElementById('logArea').textContent = 'Log cleared.';
  log('User cleared the activity log.');
});

// initial populate
document.getElementById('rawHtml').value = samplePage;
document.getElementById('scanBtn').click();
