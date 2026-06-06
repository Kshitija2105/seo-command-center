"""
fixer.py — generate fix files: titles CSV + redirect map
"""
import csv, os, json
from seo.detector import load_rows, detect, _int

def generate_fixes(export_dir: str, output_dir: str):
    rows = load_rows(export_dir)
    issues = detect(rows)
    
    # Build lookup
    row_by_url = {r["Address"]: r for r in rows}
    
    # --- Titles fix CSV ---
    missing_titles = []
    for issue in issues:
        if issue["type"] in ("missing_title", "title_too_short", "title_too_long"):
            for url in issue["affected_urls"][:20]:  # cap at 20
                r = row_by_url.get(url, {})
                old_title = (r.get("Title 1","") or "").strip()
                h1 = (r.get("H1-1","") or "").strip()
                # Generate new title from H1 or URL slug
                if h1:
                    new_title = h1[:55] + " | NMG Technologies"
                else:
                    slug = url.rstrip("/").split("/")[-1].replace("-"," ").replace("_"," ").title()
                    new_title = (slug[:40] if slug else "Home") + " | NMG Technologies"
                new_title = new_title[:60]
                missing_titles.append({"url": url, "old": old_title, "new": new_title})
    
    os.makedirs(output_dir, exist_ok=True)
    titles_path = os.path.join(output_dir, "fix_titles.csv")
    with open(titles_path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["url","old","new"])
        w.writeheader()
        w.writerows(missing_titles)
    
    # --- Redirect map ---
    redirect_map = []
    for issue in issues:
        if issue["type"] == "broken_link":
            for url in issue["affected_urls"]:
                redirect_map.append({"from": url, "to": url.rstrip("/").rsplit("/",1)[0] + "/", "reason": "404 -> parent path"})
        if issue["type"] == "redirect_chain":
            for url in issue["affected_urls"]:
                r = row_by_url.get(url, {})
                final = (r.get("Redirect URL","") or "").strip()
                if final:
                    redirect_map.append({"from": url, "to": final, "reason": "Flatten redirect chain"})
    
    redirect_path = os.path.join(output_dir, "fix_redirects.csv")
    with open(redirect_path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["from","to","reason"])
        w.writeheader()
        w.writerows(redirect_map)
    
    print(f"Fix files written: {len(missing_titles)} title fixes, {len(redirect_map)} redirect fixes")
    return {"titles": missing_titles, "redirect_map": redirect_map}

if __name__ == "__main__":
    import sys
    d = sys.argv[1] if len(sys.argv) > 1 else "../sample-export"
    generate_fixes(d, "outputs")
