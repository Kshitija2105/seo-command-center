#!/usr/bin/env python3
from __future__ import annotations
import argparse, os, sys, time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "mcp"))
sys.path.insert(0, HERE)
import server

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("export_dir")
    ap.add_argument("--no-dashboard", action="store_true")
    args = ap.parse_args()

    if not args.no_dashboard:
        try:
            server.start_dashboard()
            print(f"[seo] dashboard: http://localhost:{server.PORT}", flush=True)
            time.sleep(1)
        except OSError:
            print(f"[seo] dashboard already running at http://localhost:{server.PORT}", flush=True)

    t0 = time.time()
    server.seo_load(args.export_dir)
    res = server.seo_detect()

    issues = sorted(server.RUN["issues"], key=lambda x: {"High":0,"Medium":1,"Low":2}.get(x["severity"],3))
    recs = []
    for i in issues[:5]:
        recs.append(f"Fix the {i['count']} {i['severity']}-severity '{i['type']}' issue(s) first.")
    if not recs:
        recs.append("No issues detected on this crawl.")
    server.seo_recommend(recs)
    server.RUN["model_calls"] = 0
    server.RUN["duration_sec"] = round(time.time() - t0, 1)
    server.seo_report()
    server.seo_export()

    s = server.RUN["summary"]
    print("\n=== SEO AUDIT RESULT ===")
    print(f"Site         : {server.RUN['site']}  ({server.RUN['urls']} URLs)")
    print(f"Total issues : {s['total_issues']}  (High {s['by_severity'].get('High',0)} / Medium {s['by_severity'].get('Medium',0)} / Low {s['by_severity'].get('Low',0)})")
    print("Wrote outputs/report.json and outputs/report.html")

if __name__ == "__main__":
    main()
