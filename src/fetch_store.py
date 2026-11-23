#!/usr/bin/env python3
"""Refreshes src/store.json with each app's current version and last-update month from Google Play.

Never fails the job: if a page cannot be fetched or parsed, the previous values are kept.
"""
import json
import pathlib
import re
import urllib.request

PATH = pathlib.Path(__file__).resolve().parent / "store.json"
data = json.loads(PATH.read_text())

for key, app in data.items():
    url = f"https://play.google.com/store/apps/details?id={app['play']}&hl=en&gl=US"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        html = urllib.request.urlopen(req, timeout=30).read().decode("utf8", "ignore")
    except Exception as exc:  # network errors keep the old values
        print(f"{key}: fetch failed ({exc}); keeping {app['version']} / {app['updated']}")
        continue
    updated = re.search(r"Updated on</div><div[^>]*>([A-Z][a-z]{2}) \d{1,2}, (\d{4})<", html)
    version = re.search(r'\[\[\["(\d+(?:\.\d+){1,3})"\]\]', html)
    if updated:
        app["updated"] = f"{updated.group(1)} {updated.group(2)}"
    if version:
        app["version"] = version.group(1)
    print(f"{key}: v{app['version']}, updated {app['updated']}" + ("" if updated and version else "  (partly kept)"))

PATH.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n")
