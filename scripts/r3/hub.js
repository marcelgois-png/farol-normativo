// Farol Normativo — Rodada 3: hub de gravação (File System Access API)
(() => {
  if (window.__farol) return 'já instalado';
  const F = window.__farol = { dir: null, log: [] };
  F.sha256 = async (buf) => [...new Uint8Array(await crypto.subtle.digest('SHA-256', buf))].map(b => b.toString(16).padStart(2, '0')).join('');
  F.escolher = async () => { F.dir = await window.showDirectoryPicker({ mode: 'readwrite', id: 'farol-r3' }); document.getElementById('farol-ov')?.remove(); return F.dir.name; };
  F.salvar = async (url, subdir, nome, opts = {}) => {
    const t0 = Date.now();
    try {
      const r = await fetch(url, { credentials: 'omit', redirect: 'follow', ...opts });
      const buf = await r.arrayBuffer();
      const ct = r.headers.get('content-type') || '';
      if (!r.ok) return { nome, st: 'HTTP ' + r.status, url: r.url };
      if (buf.byteLength < 200) return { nome, st: 'vazio', bytes: buf.byteLength };
      const sha = await F.sha256(buf);
      let d = F.dir; for (const p of subdir.split('/').filter(Boolean)) d = await d.getDirectoryHandle(p, { create: true });
      const fh = await d.getFileHandle(nome, { create: true }); const w = await fh.createWritable(); await w.write(buf); await w.close();
      const row = { nome, st: 'ok', bytes: buf.byteLength, sha, ct: ct.split(';')[0], url: r.url, ms: Date.now() - t0 };
      F.log.push(row); return row;
    } catch (e) { return { nome, st: 'erro', e: String(e).slice(0, 120) }; }
  };
  const ov = document.createElement('div'); ov.id = 'farol-ov';
  ov.style.cssText = 'position:fixed;inset:0;z-index:2147483647;background:rgba(30,55,102,.92);color:#fff;display:flex;flex-direction:column;align-items:center;justify-content:center;font:18px IBM Plex Sans,Arial';
  ov.innerHTML = '<div style="font-size:26px;margin-bottom:12px">Farol Normativo · Rodada 3</div><div style="margin-bottom:24px">Escolha a pasta <b>Documents\\Oraculovski\\originais_r3</b> para gravar os originais deste site.</div><button id="farol-btn" style="font:20px Arial;padding:14px 36px;background:#ffc636;border:0;border-radius:8px;cursor:pointer">Escolher pasta</button>';
  document.documentElement.appendChild(ov);
  document.getElementById('farol-btn').onclick = () => F.escolher().catch(e => { F.erro = String(e); console.log('[farol]', e); });
  return 'overlay pronto';
})();
