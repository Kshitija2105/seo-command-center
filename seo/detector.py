from __future__ import annotations
import csv, os
from collections import defaultdict

def load_rows(export_dir: str) -> list[dict]:
    path = os.path.join(export_dir, "internal_all.csv")
    with open(path, encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))

def _int(v, default=0):
    try: return int(float(str(v).strip()))
    except: return default

def _float(v, default=0.0):
    try: return float(str(v).strip())
    except: return default

def is_html(r): return "text/html" in (r.get("Content Type","") or "").lower()
def is_200(r): return _int(r.get("Status Code")) == 200
def indexable(r): return (r.get("Indexability","") or "").strip().lower() == "indexable"

def detect(rows):
    issues = []
    def add(t, sev, urls, explanation):
        urls = sorted(set(urls))
        if urls:
            issues.append({"type":t,"severity":sev,"affected_urls":urls,"count":len(urls),"explanation":explanation})
    html=[ r for r in rows if is_html(r)]
    idx200=[r for r in html if is_200(r) and indexable(r)]
    all200=[r for r in rows if is_200(r)]
    add("missing_title","High",[r["Address"] for r in idx200 if not (r.get("Title 1","") or "").strip()],"Indexable pages with no title tag.")
    by_title=defaultdict(list)
    [by_title[(r.get("Title 1","") or "").strip()].append(r["Address"]) for r in idx200 if (r.get("Title 1","") or "").strip()]
    add("duplicate_title","High",[u for urls in by_title.values() if len(urls)>1 for u in urls],"Pages sharing identical title.")
    add("title_too_long","Medium",[r["Address"] for r in idx200 if _int(r.get("Title 1 Pixel Width"))>561 or _int(r.get("Title 1 Length"))>60],"Titles too long.")
    add("title_too_short","Low",[r["Address"] for r in idx200 if (r.get("Title 1","") or "").strip() and _int(r.get("Title 1 Length"))<30],"Titles too short.")
    add("missing_meta","Medium",[r["Address"] for r in idx200 if not (r.get("Meta Description 1","") or "").strip()],"No meta description.")
    by_meta=defaultdict(list)
    [by_meta[(r.get("Meta Description 1","") or "").strip()].append(r["Address"]) for r in idx200 if (r.get("Meta Description 1","") or "").strip()]
    add("duplicate_meta","Medium",[u for urls in by_meta.values() if len(urls)>1 for u in urls],"Pages sharing identical meta.")
    add("meta_too_long","Low",[r["Address"] for r in idx200 if _int(r.get("Meta Description 1 Length"))>155],"Meta too long.")
    add("missing_h1","Medium",[r["Address"] for r in all200 if not (r.get("H1-1","") or "").strip()],"Pages with no H1.")
    by_h1=defaultdict(list)
    [by_h1[(r.get("H1-1","") or "").strip()].append(r["Address"]) for r in all200 if (r.get("H1-1","") or "").strip()]
    add("duplicate_h1","Low",[u for urls in by_h1.values() if len(urls)>1 for u in urls],"Pages sharing identical H1.")
    add("broken_link","High",[r["Address"] for r in rows if 400<=_int(r.get("Status Code"))<=499],"4xx errors.")
    add("server_error","High",[r["Address"] for r in rows if 500<=_int(r.get("Status Code"))<=599],"5xx errors.")
    add("redirect","Medium",[r["Address"] for r in rows if 300<=_int(r.get("Status Code"))<=399],"3xx redirects.")
    rmap={r["Address"]:(r.get("Redirect URL","") or "").strip() for r in rows if 300<=_int(r.get("Status Code"))<=399 and (r.get("Redirect URL","") or "").strip()}
    add("redirect_chain","High",[u for u,d in rmap.items() if d in rmap],"Redirect chains.")
    add("thin_content","Low",[r["Address"] for r in idx200 if _int(r.get("Word Count"))<200],"Under 200 words.")
    add("orphan_page","Medium",[r["Address"] for r in idx200 if _int(r.get("Inlinks"))==0],"Zero inlinks.")
    add("non_indexable_but_linked","Medium",[r["Address"] for r in rows if not indexable(r) and _int(r.get("Inlinks"))>0],"Non-indexable but linked.")
    add("slow_page","Low",[r["Address"] for r in all200 if _float(r.get("Response Time"))>1.0],"Over 1s response.")
    return issues

def summarize(issues):
    by_sev=defaultdict(int)
    for i in issues: by_sev[i["severity"]]+=1
    return {"total_issues":len(issues),"by_severity":{"High":by_sev["High"],"Medium":by_sev["Medium"],"Low":by_sev["Low"]}}

if __name__=="__main__":
    import sys,json
    d=sys.argv[1] if len(sys.argv)>1 else "../sample-export"
    rows=load_rows(d)
    iss=detect(rows)
    print(f"Loaded {len(rows)} rows, detected {len(iss)} issue types.")
    print(json.dumps(summarize(iss),indent=2))
    for i in iss: print(f"  [{i['severity']:<6}] {i['type']:<30} x{i['count']}")
