// 泥団子ランキングAPI: GET /api/rank → TOP10 / POST /api/rank → 登録(1人1件・自己ベストのみ)
import { getStore } from "@netlify/blobs";

const RESULTS = ["maboroshi","mirror","black","pika","tsuya","tsuru","normal","zara","crack","mud","drill","fossil"];
const SOILS = ["black","red","sandy"];
const KEEP = 100, TOP = 10, COOLDOWN_MS = 8000;
const NG = ["死ね","殺す","ころす","しね","ちんこ","まんこ","うんこ","fuck","shit","nigger","http","www."];
const recent = new Map(); // 同じ端末・IPからの連投を抑える(ベストエフォート)

const json = (body, status = 200) => new Response(JSON.stringify(body), {
  status, headers: { "content-type": "application/json; charset=utf-8", "cache-control": "no-store" }
});
const pub = (rows) => rows.slice(0, TOP).map(r => ({ id: r.id.slice(0, 8), name: r.name, score: r.score, result: r.result, soil: r.soil }));

export default async (req, context) => {
  const store = getStore({ name: "dorodango", consistency: "strong" });
  let rows = (await store.get("rows", { type: "json" })) || [];

  if (req.method === "GET") return json({ rows: pub(rows) });
  if (req.method !== "POST") return json({ error: "method" }, 405);

  let b; try { b = await req.json(); } catch { return json({ error: "bad json" }, 400); }
  const pid = typeof b.pid === "string" && /^[a-z0-9-]{8,40}$/i.test(b.pid) ? b.pid : null;
  const score = Number(b.score);
  const full = typeof b.name === "string" ? b.name.normalize("NFKC").replace(/[\u0000-\u001f\u007f<>&"'`\\]/g, "").trim() : "";
  const name = full.slice(0, 10);
  if (!pid || !name) return json({ error: "name" }, 400);
  if (!Number.isFinite(score) || score < 0 || score > 1000) return json({ error: "score" }, 400);
  if (!RESULTS.includes(b.result) || !SOILS.includes(b.soil)) return json({ error: "result" }, 400);
  const low = full.toLowerCase();
  if (NG.some(w => low.includes(w))) return json({ error: "ng-name" }, 422);

  const ip = context?.ip || req.headers.get("x-nf-client-connection-ip") || "";
  const now = Date.now();
  for (const k of [pid, ip]) {
    if (!k) continue;
    if (now - (recent.get(k) || 0) < COOLDOWN_MS) return json({ error: "slow" }, 429);
    recent.set(k, now);
  }
  if (recent.size > 5000) recent.clear();

  const sc = Math.round(score * 10) / 10;
  const i = rows.findIndex(r => r.id === pid);
  let updated = false;
  if (i < 0) { rows.push({ id: pid, name, score: sc, result: b.result, soil: b.soil, at: now }); updated = true; }
  else if (sc > rows[i].score) { rows[i] = { id: pid, name, score: sc, result: b.result, soil: b.soil, at: now }; updated = true; }
  else if (rows[i].name !== name) { rows[i].name = name; updated = true; }
  if (updated) {
    rows.sort((a, c) => c.score - a.score || a.at - c.at);
    rows = rows.slice(0, KEEP);
    await store.setJSON("rows", rows);
  }
  const rank = rows.findIndex(r => r.id === pid) + 1;
  const best = (rows.find(r => r.id === pid) || { score: sc }).score;
  return json({ ok: true, rank: rank || null, best, improved: updated && best === sc, rows: pub(rows) });
};

export const config = { path: "/api/rank" };
