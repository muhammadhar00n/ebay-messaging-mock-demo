# Creating a simple mock demo HTML file that simulates the browser extension flow.
html_content = r"""
<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8"/>
<meta name="viewport" content="width=device-width,initial-scale=1"/>
<title>eBay Bulk Messaging — Mock Demo</title>
<style>
  body { font-family: Inter, system-ui, -apple-system, "Segoe UI", Roboto, "Helvetica Neue", Arial; background:#f6f8fa; color:#0f172a; padding:20px; }
  .card{background:white;border-radius:12px;padding:18px;box-shadow:0 6px 18px rgba(15,23,42,0.06);max-width:900px;margin:0 auto;}
  h1{margin:0 0 8px;font-size:20px;}
  .row{display:flex;gap:12px;align-items:center;margin:8px 0;}
  textarea{width:100%;height:90px;padding:10px;border-radius:8px;border:1px solid #e6eef6;resize:vertical;}
  input[type=text]{width:100%;padding:10px;border-radius:8px;border:1px solid #e6eef6;}
  button{background:#2563eb;color:white;padding:10px 14px;border-radius:8px;border:0;cursor:pointer;}
  button.ghost{background:transparent;border:1px solid #cbd5e1;color:#0f172a;}
  ul{padding-left:18px;}
  .seller{display:flex;justify-content:space-between;align-items:center;padding:8px;border-radius:8px;border:1px solid #f1f5f9;margin-bottom:8px;background:#fff;}
  .log{font-family:monospace;white-space:pre-wrap;background:#0f172a;color:#e6eef6;padding:10px;border-radius:8px;height:140px;overflow:auto;}
  .badge{background:#eef2ff;color:#3730a3;padding:6px 8px;border-radius:999px;font-weight:600;font-size:12px;}
  .modal{position:fixed;inset:0;background:rgba(2,6,23,0.45);display:flex;align-items:center;justify-content:center;}
  .modal-card{background:white;padding:16px;border-radius:10px;width:480px;box-shadow:0 10px 30px rgba(2,6,23,0.2);}
</style>
</head>
<body>
<div class="card">
  <h1>eBay Bulk Messaging — Mock Demo</h1>
  <div style="color:#475569;margin-bottom:12px;">This is a **mock demo**. It simulates extracting sellers from a listings page and the semi-automatic / automatic send flows — it will not contact eBay.</div>

  <label><strong>Step 1 — Paste your listings page URL (or use sample)</strong></label>
  <div class="row"><input id="urlInput" type="text" placeholder="https://www.ebay.com/itm/.... or paste a saved page URL" value="sample://listings-page"/></div>

  <label><strong>Step 2 — (Optional) Paste raw HTML of the listings page</strong></label>
  <div style="color:#94a3b8;margin-bottom:6px;">If you have a saved page, paste it here. Otherwise the demo uses an embedded sample page.</div>
  <textarea id="rawHtml" placeholder="Paste saved listings page HTML here (optional)"></textarea>

  <div class="row">
    <button id="scanBtn">Scan page and extract sellers</button>
    <button class="ghost" id="loadSample">Load sample page (demo)</button>
    <div style="margin-left:auto;"><span class="badge" id="countBadge">0 sellers</span></div>
  </div>

  <hr/>

  <label><strong>Extracted sellers</strong></label>
  <div id="sellersList" style="margin:8px 0 12px;"></div>

  <label><strong>Message template</strong></label>
  <textarea id="template">Hi {{seller}}, I’m interested in your listing. Is this item still available? Thanks — {{yourName}}</textarea>
  <div class="row">
    <input id="yourName" type="text" placeholder="Your name" value="Ali"/>
    <button id="queueBtn">Queue sellers for semi-auto send</button>
    <button id="autoBtn">Simulate Auto-send (demo)</button>
    <button class="ghost" id="clearLog">Clear log</button>
  </div>

  <h3>Queue</h3>
  <div id="queueArea"></div>

  <h3>Activity log</h3>
  <div class="log" id="logArea">Demo started — no messages sent yet.</div>
</div>

<!-- Modal for semi-auto send -->
<div id="modalRoot" style="display:none;"></div>

<script>
const samplePage = `
<!-- Sample listings HTML (simulated) -->
<div class="item"><a href="/itm/123">Item A</a><span class="seller">Seller: best_seller_123</span></div>
<div class="item"><a href="/itm/456">Item B</a><span class="seller">Seller: coolstore_88</span></div>
<div class="item"><a href="/itm/789">Item C</a><span class="seller">Seller: vintage-hub</span></div>
<div class="item"><a href="/itm/111">Item D</a><span class="seller">Seller: ali_seller</span></div>
`;

function log(msg) {
  const el = document.getElementById('logArea');
  const ts = new Date().toLocaleTimeString();
  el.textContent = `[${ts}] ` + msg + "\\n" + el.textContent;
}

function extractSellersFromHtml(html) {
  // Simple regex to capture seller names in patterns like "Seller: name" or data-seller="name"
  const sellers = new Set();
  // pattern 1: Seller: name
  const re1 = /Seller:\\s*([A-Za-z0-9_\\-\\.]+)/gi;
  let m;
  while ((m = re1.exec(html)) !== null) sellers.add(m[1]);

  // pattern 2: data-seller="name"
  const re2 = /data-seller=["']([A-Za-z0-9_\\-\\.]+)["']/gi;
  while ((m = re2.exec(html)) !== null) sellers.add(m[1]);

  // pattern 3: links to user profiles or /usr/username
  const re3 = /\\/usr\\/([A-Za-z0-9_\\-\\.]+)/gi;
  while ((m = re3.exec(html)) !== null) sellers.add(m[1]);

  // pattern 4: common ebayseller display like "by <span class='sellername'>name</span>"
  const re4 = /seller[\\s'\\">:\\=]+([A-Za-z0-9_\\-\\.]+)/gi;
  while ((m = re4.exec(html)) !== null) sellers.add(m[1]);

  return Array.from(sellers);
}

document.getElementById('loadSample').addEventListener('click', ()=>{
  document.getElementById('rawHtml').value = samplePage;
  log('Loaded sample listings HTML into the raw HTML area.');
});

document.getElementById('scanBtn').addEventListener('click', ()=>{
  let raw = document.getElementById('rawHtml').value.trim();
  if(!raw) raw = samplePage; // use embedded sample
  const sellers = extractSellersFromHtml(raw);
  const list = document.getElementById('sellersList');
  list.innerHTML = '';
  sellers.forEach(s=>{
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
  if(document.getElementById(id)) { log('Seller ' + seller + ' already in queue.'); return; }
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
  return tmpl.replace(/\\{\\{seller\\}\\}/g, seller).replace(/\\{\\{yourName\\}\\}/g, name);
}

window.previewMessage = function(seller){
  const msg = buildMessageForSeller(seller);
  showModal(seller, msg, false);
};

document.getElementById('queueBtn').addEventListener('click', ()=>{
  // start semi-auto: open first queued message modal
  const q = document.getElementById('queueArea');
  const first = q.querySelector('.seller');
  if(!first){ alert('Queue is empty — add sellers first.'); return; }
  const seller = first.firstChild.textContent.trim();
  const msg = buildMessageForSeller(seller);
  showModal(seller, msg, true);
});

document.getElementById('autoBtn').addEventListener('click', async ()=>{
  // simulate auto send with delays -> safe simulation only
  const q = document.getElementById('queueArea');
  const items = Array.from(q.querySelectorAll('.seller')).map(e => e.firstChild.textContent.trim());
  if(items.length===0){ alert('Queue empty — add sellers first.'); return; }
  log('Starting simulated auto-send for ' + items.length + ' sellers (demo only).');
  for(let i=0;i<items.length;i++){
    const s = items[i];
    const m = buildMessageForSeller(s);
    log(`(AUTO) Simulated send to ${s}: "${m.slice(0,60)}${m.length>60?'...':''}"`);
    // visually mark sent in queue
    const el = document.getElementById('q-'+s);
    if(el) el.style.opacity=0.6;
    await new Promise(r=>setTimeout(r, 900 + Math.random()*700)); // random delay
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
      // Simulate sending
      root.style.display='none';
      log(`(SEMI) Simulated send to ${seller}: "${message.replace(/\\n/g,' ')}"`);
      // remove from queue visually
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

// initial populate sample
document.getElementById('rawHtml').value = samplePage;
document.getElementById('scanBtn').click();
</script>
</body>
</html>
"""

# write to file
path = "/ebay_messaging_demo.html"
with open(path, "w", encoding="utf-8") as f:
    f.write(html_content)

path

