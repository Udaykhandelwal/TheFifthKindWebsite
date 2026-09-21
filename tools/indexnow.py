#!/usr/bin/env python3
"""Ping Bing/Yandex/Seznam (IndexNow) with every URL in urls.txt.
Run after `python3 tools/build.py` + git push, once the deploy is live."""
import json, pathlib, urllib.request
root = pathlib.Path(__file__).resolve().parent.parent
key = (root / ".indexnow-key").read_text().strip()
urls = [u.strip() for u in (root / "urls.txt").read_text().splitlines() if u.strip()]
body = json.dumps({"host": "www.the5thkind.in", "key": key,
                   "keyLocation": f"https://www.the5thkind.in/{key}.txt", "urlList": urls}).encode()
req = urllib.request.Request("https://api.indexnow.org/indexnow", data=body,
                             headers={"Content-Type": "application/json; charset=utf-8"})
print("IndexNow:", urllib.request.urlopen(req, timeout=30).status, f"({len(urls)} urls)")
