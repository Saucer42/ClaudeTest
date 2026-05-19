#!/usr/bin/env python3
"""
Job search dashboard — fetch job listings and review them in an interactive browser UI.

Usage:
    python tools/job_board.py            # fetch fresh results, open dashboard
    python tools/job_board.py --no-fetch # use today's cached results
    python tools/job_board.py --port 8080

In the dashboard you can:
  - Browse job cards (fetched from RemoteOK + any manually added)
  - Click "Add Job Manually" to paste a job from LinkedIn/Indeed/etc.
  - Click "👍 Approve" to add the job to tracker.md with Approved status
      (also saves the JD to applications/jds/ so apply.py can use it)
  - Click "Skip" to hide a card for this session
  - Filter by keyword, source, or status

After approving, run:
    python tools/apply.py    # generate tailored resume + cover letter for each approved job
"""

import argparse
import json
import sys
import threading
import webbrowser
from datetime import datetime
from pathlib import Path

try:
    import requests
    from flask import Flask, jsonify, render_template_string, request as freq
except ImportError:
    sys.exit("Run: pip install flask requests")

REPO_ROOT = Path(__file__).parent.parent
TRACKER_PATH = REPO_ROOT / "applications" / "tracker.md"
JDS_DIR = REPO_ROOT / "applications" / "jds"
SEARCH_DIR = REPO_ROOT / "job-search"

APPROVED_STATUS = "👍 Approved"

# RemoteOK tag searches relevant to Michael's profile
REMOTEOK_TAGS = [
    "data-integration", "sql", "etl", "analytics",
    "data-engineer", "data-architect", "reporting", "business-intelligence",
]

RELEVANCE_KEYWORDS = [
    "data", "sql", "analytics", "reporting", "integration", "etl",
    "bi ", "business intelligence", "data engineer", "data manager",
    "data architect", "solutions architect", "data director", "migration",
]

app = Flask(__name__)
JOBS: list[dict] = []


# ---------------------------------------------------------------------------
# Job fetching
# ---------------------------------------------------------------------------

def fetch_remoteok(tags: list[str]) -> list[dict]:
    jobs = []
    seen_ids: set[str] = set()
    for tag in tags:
        try:
            resp = requests.get(
                f"https://remoteok.com/api?tags={tag}",
                headers={"User-Agent": "JobSearchDashboard/1.0"},
                timeout=10,
            )
            if resp.status_code != 200:
                continue
            for item in resp.json()[1:]:
                if not isinstance(item, dict):
                    continue
                jid = str(item.get("id", ""))
                if jid in seen_ids:
                    continue
                seen_ids.add(jid)
                jobs.append({
                    "id": jid,
                    "title": item.get("position", ""),
                    "company": item.get("company", ""),
                    "location": item.get("location") or "Remote",
                    "url": item.get("url", ""),
                    "description": item.get("description", ""),
                    "tags": item.get("tags", []),
                    "salary": item.get("salary") or "",
                    "date": item.get("date", ""),
                    "source": "RemoteOK",
                    "status": "new",
                })
        except Exception:
            continue
    return jobs


def is_relevant(job: dict) -> bool:
    text = " ".join([
        job.get("title", ""),
        job.get("description", ""),
        *job.get("tags", []),
    ]).lower()
    return any(kw in text for kw in RELEVANCE_KEYWORDS)


def load_or_fetch(force_fetch: bool = True) -> list[dict]:
    SEARCH_DIR.mkdir(parents=True, exist_ok=True)
    cache = SEARCH_DIR / f"results_{datetime.now().strftime('%Y%m%d')}.json"

    if not force_fetch and cache.exists():
        print(f"Using cached results: {cache.name}")
        return json.loads(cache.read_text())

    print("Fetching job listings from RemoteOK...")
    raw = fetch_remoteok(REMOTEOK_TAGS)
    jobs = [j for j in raw if is_relevant(j)]

    # Deduplicate
    seen: set[str] = set()
    unique = []
    for j in jobs:
        if j["id"] not in seen:
            seen.add(j["id"])
            unique.append(j)

    unique.sort(key=lambda x: x.get("date", ""), reverse=True)
    result = unique[:150]
    cache.write_text(json.dumps(result, indent=2))
    print(f"Found {len(result)} relevant jobs → cached to {cache.name}")
    return result


# ---------------------------------------------------------------------------
# Tracker update
# ---------------------------------------------------------------------------

def save_to_tracker(company: str, role: str, url: str, jd: str) -> None:
    today = datetime.now().strftime("%Y-%m-%d")
    slug = company.lower().replace(" ", "_")

    JDS_DIR.mkdir(parents=True, exist_ok=True)
    jd_path = JDS_DIR / f"{slug}_{today}.txt"
    jd_path.write_text(jd)

    tracker = TRACKER_PATH.read_text()
    new_row = f"| {today} | {company} | {role} | {url} | {APPROVED_STATUS} | — | — | — |"

    lines = tracker.splitlines()
    updated = []
    inserted = False
    for line in lines:
        updated.append(line)
        if not inserted and re.search(r"\|---.*---.*---", line):
            updated.append(new_row)
            inserted = True

    if not inserted:
        updated.append(new_row)

    TRACKER_PATH.write_text("\n".join(updated))


import re  # noqa: E402 — used in save_to_tracker above


# ---------------------------------------------------------------------------
# Flask routes
# ---------------------------------------------------------------------------

@app.route("/")
def index():
    return render_template_string(HTML_TEMPLATE)


@app.route("/api/jobs")
def api_jobs():
    return jsonify({"jobs": JOBS, "fetch_date": datetime.now().strftime("%Y-%m-%d")})


@app.route("/api/approve", methods=["POST"])
def api_approve():
    data = freq.json
    try:
        save_to_tracker(
            company=data["company"],
            role=data["role"],
            url=data.get("url", ""),
            jd=data.get("description", ""),
        )
        for j in JOBS:
            if j["id"] == data["id"]:
                j["status"] = "approved"
        return jsonify({"ok": True})
    except Exception as exc:
        return jsonify({"ok": False, "error": str(exc)}), 500


@app.route("/api/add", methods=["POST"])
def api_add():
    data = freq.json
    try:
        job_id = f"manual_{datetime.now().strftime('%Y%m%d%H%M%S%f')}"
        job = {
            "id": job_id,
            "title": data["role"],
            "company": data["company"],
            "location": data.get("location", ""),
            "url": data.get("url", ""),
            "description": data.get("description", ""),
            "tags": [],
            "salary": data.get("salary", ""),
            "date": datetime.now().isoformat(),
            "source": "Manual",
            "status": "new",
        }
        JOBS.insert(0, job)

        if data.get("autoApprove"):
            save_to_tracker(
                company=data["company"],
                role=data["role"],
                url=data.get("url", ""),
                jd=data.get("description", ""),
            )
            job["status"] = "approved"
        else:
            slug = data["company"].lower().replace(" ", "_")
            today = datetime.now().strftime("%Y-%m-%d")
            jd_path = JDS_DIR / f"{slug}_{today}.txt"
            JDS_DIR.mkdir(parents=True, exist_ok=True)
            jd_path.write_text(data.get("description", ""))

        return jsonify({"ok": True, "id": job_id})
    except Exception as exc:
        return jsonify({"ok": False, "error": str(exc)}), 500


# ---------------------------------------------------------------------------
# HTML template
# ---------------------------------------------------------------------------

HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Job Board — Michael Marchese</title>
<style>
*{box-sizing:border-box;margin:0;padding:0}
body{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;background:#f5f5f7;color:#222}
.header{background:#1a1a2e;color:#fff;padding:18px 32px;display:flex;align-items:center;justify-content:space-between}
.header h1{font-size:1.3rem;font-weight:600}
.header .sub{font-size:.8rem;opacity:.6;margin-top:2px}
.toolbar{background:#fff;border-bottom:1px solid #e0e0e0;padding:12px 32px;display:flex;gap:10px;align-items:center;flex-wrap:wrap;position:sticky;top:0;z-index:10}
.toolbar input{padding:8px 12px;border:1px solid #ddd;border-radius:6px;font-size:.9rem;width:240px;outline:none}
.toolbar input:focus{border-color:#4f46e5}
.toolbar select{padding:8px 10px;border:1px solid #ddd;border-radius:6px;font-size:.85rem;outline:none}
.btn{padding:8px 16px;border:none;border-radius:6px;font-size:.85rem;cursor:pointer;font-weight:500;transition:background .15s}
.btn-primary{background:#4f46e5;color:#fff}.btn-primary:hover{background:#4338ca}
.btn-approve{background:#16a34a;color:#fff}.btn-approve:hover{background:#15803d}
.btn-skip{background:#f3f4f6;color:#555;border:1px solid #ddd}.btn-skip:hover{background:#e5e7eb}
.btn-add{background:#0891b2;color:#fff}.btn-add:hover{background:#0e7490}
.stats{font-size:.82rem;color:#888;margin-left:auto;white-space:nowrap}
.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(360px,1fr));gap:16px;padding:24px 32px}
.card{background:#fff;border-radius:10px;border:1px solid #e5e7eb;overflow:hidden;display:flex;flex-direction:column;transition:box-shadow .15s}
.card:hover{box-shadow:0 4px 14px rgba(0,0,0,.07)}
.card.approved{border-color:#16a34a;background:#f0fdf4}
.card.skipped{opacity:.35;pointer-events:none}
.ch{padding:16px 16px 10px}
.ct{font-size:.98rem;font-weight:600;color:#111;margin-bottom:3px}
.cc{font-size:.88rem;color:#4f46e5;font-weight:500}
.cm{display:flex;gap:6px;flex-wrap:wrap;margin-top:8px}
.badge{font-size:.72rem;padding:2px 8px;border-radius:999px;font-weight:500}
.bl{background:#eff6ff;color:#1d4ed8}
.bs{background:#f3f4f6;color:#555}
.bm{background:#f0fdf4;color:#15803d}
.bt{background:#faf5ff;color:#7c3aed}
.desc{padding:0 16px 10px;font-size:.83rem;color:#444;line-height:1.55;flex:1}
.desc.col{max-height:72px;overflow:hidden;position:relative}
.desc.col::after{content:'';position:absolute;bottom:0;left:0;right:0;height:28px;background:linear-gradient(transparent,#fff)}
.card.approved .desc.col::after{background:linear-gradient(transparent,#f0fdf4)}
.xbtn{background:none;border:none;color:#4f46e5;font-size:.78rem;cursor:pointer;padding:0 16px 8px;text-align:left}
.ca{padding:10px 16px;border-top:1px solid #f3f4f6;display:flex;gap:8px;align-items:center}
.app-badge{font-size:.82rem;color:#16a34a;font-weight:600;margin-left:auto}
.overlay{display:none;position:fixed;inset:0;background:rgba(0,0,0,.5);z-index:100;align-items:center;justify-content:center}
.overlay.on{display:flex}
.modal{background:#fff;border-radius:12px;width:580px;max-width:95vw;max-height:90vh;overflow-y:auto;display:flex;flex-direction:column}
.mh{padding:18px 24px;border-bottom:1px solid #e5e7eb;font-size:1rem;font-weight:600;display:flex;justify-content:space-between;align-items:center}
.mh button{background:none;border:none;font-size:1.3rem;cursor:pointer;color:#888}
.mb{padding:18px 24px;display:flex;flex-direction:column;gap:12px}
.mf{padding:14px 24px;border-top:1px solid #e5e7eb;display:flex;justify-content:flex-end;gap:10px}
label{font-size:.82rem;font-weight:500;color:#555;margin-bottom:3px;display:block}
input[type=text],textarea{width:100%;padding:8px 12px;border:1px solid #ddd;border-radius:6px;font-size:.88rem;font-family:inherit;outline:none}
input[type=text]:focus,textarea:focus{border-color:#4f46e5}
textarea{min-height:130px;resize:vertical}
.toast{position:fixed;bottom:24px;right:24px;background:#1a1a2e;color:#fff;padding:11px 18px;border-radius:8px;font-size:.88rem;z-index:200;opacity:0;transition:opacity .25s;pointer-events:none}
.toast.on{opacity:1}
.empty{text-align:center;padding:80px 32px;color:#aaa}
.empty h2{font-size:1rem;margin-bottom:6px}
</style>
</head>
<body>
<div class="header">
  <div><h1>Job Board</h1><div class="sub">Michael Marchese &middot; Data Integration &amp; Analytics Leader</div></div>
  <div style="font-size:.8rem;opacity:.6" id="fetchDate"></div>
</div>
<div class="toolbar">
  <input id="fi" placeholder="Filter by title, company, skill…" oninput="render()">
  <select id="fs" onchange="render()"><option value="">All sources</option></select>
  <select id="fst" onchange="render()">
    <option value="new">New</option>
    <option value="">All</option>
    <option value="approved">Approved</option>
    <option value="skipped">Skipped</option>
  </select>
  <button class="btn btn-add" onclick="openModal()">+ Add Job Manually</button>
  <div class="stats" id="stats"></div>
</div>
<div class="grid" id="grid"></div>
<div class="empty" id="empty" style="display:none"><h2>No jobs match your filters</h2><p>Try clearing the search or changing the status filter.</p></div>

<div class="overlay" id="modal">
  <div class="modal">
    <div class="mh">Add Job Manually <button onclick="closeModal()">✕</button></div>
    <div class="mb">
      <div><label>Company *</label><input type="text" id="mc" placeholder="e.g. CIBC"></div>
      <div><label>Role / Job Title *</label><input type="text" id="mr" placeholder="e.g. Manager, Data Integration"></div>
      <div><label>Job URL</label><input type="text" id="mu" placeholder="https://…"></div>
      <div><label>Location</label><input type="text" id="ml" placeholder="Toronto, ON / Remote / Hybrid"></div>
      <div><label>Salary (optional)</label><input type="text" id="ms" placeholder="e.g. $120,000 – $155,000"></div>
      <div><label>Job Description — paste the full text *</label><textarea id="md" placeholder="Paste the full job description here…"></textarea></div>
    </div>
    <div class="mf">
      <button class="btn btn-skip" onclick="closeModal()">Cancel</button>
      <button class="btn btn-primary" onclick="addJob(false)">Add to Review</button>
      <button class="btn btn-approve" onclick="addJob(true)">Add &amp; Approve</button>
    </div>
  </div>
</div>
<div class="toast" id="toast"></div>

<script>
let jobs=[], state={};
async function init(){
  const r=await fetch('/api/jobs'), d=await r.json();
  jobs=d.jobs;
  document.getElementById('fetchDate').textContent='Fetched: '+d.fetch_date;
  const srcs=[...new Set(jobs.map(j=>j.source).filter(Boolean))];
  const sel=document.getElementById('fs');
  srcs.forEach(s=>{const o=document.createElement('option');o.value=s;o.textContent=s;sel.appendChild(o);});
  render();
}
function render(){
  const q=document.getElementById('fi').value.toLowerCase();
  const src=document.getElementById('fs').value.toLowerCase();
  const st=document.getElementById('fst').value;
  const grid=document.getElementById('grid');
  grid.innerHTML='';
  let n=0;
  jobs.forEach(j=>{
    const s=state[j.id]||j.status||'new';
    if(st&&s!==st)return;
    const txt=[j.title,j.company,j.description,...(j.tags||[])].join(' ').toLowerCase();
    if(q&&!txt.includes(q))return;
    if(src&&(j.source||'').toLowerCase()!==src)return;
    n++;grid.appendChild(card(j,s));
  });
  document.getElementById('empty').style.display=n?'none':'block';
  document.getElementById('stats').textContent=n+' of '+jobs.length+' jobs';
}
function card(j,s){
  const d=document.createElement('div');
  d.className='card'+(s==='approved'?' approved':s==='skipped'?' skipped':'');
  d.dataset.id=j.id;
  const tags=(j.tags||[]).slice(0,4).map(t=>`<span class="badge bt">${e(t)}</span>`).join('');
  const sal=j.salary?`<span class="badge bm">${e(j.salary)}</span>`:'';
  const desc=(j.description||'').replace(/<[^>]+>/g,'').trim();
  const actions=s==='approved'
    ?`<span class="app-badge">✓ Approved</span>`
    :`<button class="btn btn-approve" onclick="approve('${j.id}')">👍 Approve</button>
      <button class="btn btn-skip" onclick="skip('${j.id}')">Skip</button>`;
  const link=j.url?`<a href="${e(j.url)}" target="_blank" style="font-size:.78rem;color:#4f46e5;margin-left:auto">View ↗</a>`:'';
  d.innerHTML=`
    <div class="ch">
      <div class="ct">${e(j.title)}</div>
      <div class="cc">${e(j.company)}</div>
      <div class="cm"><span class="badge bl">${e(j.location||'Remote')}</span><span class="badge bs">${e(j.source||'')}</span>${sal}${tags}</div>
    </div>
    <div class="desc col" id="d${j.id}">${e(desc)}</div>
    <button class="xbtn" onclick="xpand('${j.id}')">Show more ↓</button>
    <div class="ca">${actions}${link}</div>`;
  return d;
}
function e(s){return String(s||'').replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');}
function xpand(id){
  const el=document.getElementById('d'+id),btn=el.nextElementSibling;
  el.classList.toggle('col');btn.textContent=el.classList.contains('col')?'Show more ↓':'Show less ↑';
}
async function approve(id){
  const j=jobs.find(x=>x.id===id);if(!j)return;
  const r=await fetch('/api/approve',{method:'POST',headers:{'Content-Type':'application/json'},
    body:JSON.stringify({id,company:j.company,role:j.title,url:j.url,description:j.description})});
  const d=await r.json();
  if(d.ok){state[id]='approved';render();toast(`✓ "${j.title}" at ${j.company} added to tracker`);}
  else toast('Error: '+d.error);
}
function skip(id){state[id]='skipped';render();}
function openModal(){document.getElementById('modal').classList.add('on');}
function closeModal(){document.getElementById('modal').classList.remove('on');}
async function addJob(auto){
  const c=document.getElementById('mc').value.trim(),r=document.getElementById('mr').value.trim(),
        u=document.getElementById('mu').value.trim(),l=document.getElementById('ml').value.trim(),
        s=document.getElementById('ms').value.trim(),desc=document.getElementById('md').value.trim();
  if(!c||!r||!desc){toast('Company, role, and description are required.');return;}
  const res=await fetch('/api/add',{method:'POST',headers:{'Content-Type':'application/json'},
    body:JSON.stringify({company:c,role:r,url:u,location:l,salary:s,description:desc,autoApprove:auto})});
  const d=await res.json();
  if(d.ok){
    closeModal();
    jobs.unshift({id:d.id,title:r,company:c,url:u,location:l,salary:s,description:desc,tags:[],source:'Manual',status:auto?'approved':'new'});
    if(auto)state[d.id]='approved';
    render();
    toast(auto?`✓ Added & approved "${r}" at ${c}`:`Added "${r}" at ${c} to review`);
    ['mc','mr','mu','ml','ms','md'].forEach(x=>document.getElementById(x).value='');
  }else toast('Error: '+d.error);
}
function toast(msg){const t=document.getElementById('toast');t.textContent=msg;t.classList.add('on');setTimeout(()=>t.classList.remove('on'),3000);}
window.addEventListener('keydown',e=>{if(e.key==='Escape')closeModal();});
init();
</script>
</body>
</html>"""


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    global JOBS
    parser = argparse.ArgumentParser(description="Job search dashboard")
    parser.add_argument("--no-fetch", action="store_true", help="Use cached results")
    parser.add_argument("--port", type=int, default=5000)
    args = parser.parse_args()

    JOBS = load_or_fetch(force_fetch=not args.no_fetch)

    url = f"http://localhost:{args.port}"
    print(f"\nDashboard: {url}")
    print("Ctrl+C to stop.\n")
    threading.Timer(1.2, lambda: webbrowser.open(url)).start()
    app.run(port=args.port, debug=False, use_reloader=False)


if __name__ == "__main__":
    main()
