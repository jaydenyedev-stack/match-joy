#!/usr/bin/env bash
set -e
rm -rf build/web build/web-cache
mkdir -p build/web build/web-cache
python -m pip install pygbag
pygbag --build --template default.tmpl --icon images/red.png --ume_block 0 test.py
python - <<'PY'
from pathlib import Path
import shutil
import re
import pygbag

src = Path(pygbag.__file__).resolve().parent / "support" / "cpythonrc.py"
dst = Path("build/web/pythonrc.py")
dst.parent.mkdir(parents=True, exist_ok=True)
shutil.copyfile(src, dst)

pythonrc = dst
if pythonrc.is_file():
    pr = pythonrc.read_text(encoding="utf-8")
    pr = pr.replace(
        "import os, sys, json, builtins\n",
        'import os, sys, json, builtins\nos.environ["PYGPI"] = "https://pygame-web.github.io/archives/repo/"\n',
        1,
    )
    pr = pr.replace(
        '        elif platform.window.location.href.startswith("http://localhost:8"):\n            rewritecdn = "http://localhost:8000/archives/repo/"\n',
        '        elif False:\n            rewritecdn = ""\n',
    )
    pr = re.sub(
        r'PYCONFIG_PKG_INDEXES_DEV\s*=\s*\[[^\]]*\]',
        'PYCONFIG_PKG_INDEXES_DEV = ["https://pygame-web.github.io/archives/repo/"]',
        pr,
        count=1,
    )
    pythonrc.write_text(pr, encoding="utf-8")

index = Path("build/web/index.html")
if index.is_file():
    text = index.read_text(encoding="utf-8")
    text = text.replace("https://pygame-web.github.io/archives/0.9/pythonrc.py", "pythonrc.py")
    text = re.sub(r"https://pygame-web.github.io/[^\"']+/pythonrc\\.py", "pythonrc.py", text)
    text = text.replace("https://pygame-web.github.io/archives/0.9/pythons.js", "pythons.js")
    text = text.replace("data-os=vtx,fs,snd,gui", "data-os=vt,fs,snd,gui")
    text = text.replace("if not platform.window.MM.UME:", "if False:")
    text = text.replace("    import platform\n    import json\n    from pathlib import Path\n", "    import platform\n    import json\n    import time\n    from pathlib import Path\n")
    text = text.replace(
        "    while not track.ready:\n        pg_bar(track.pos)\n        compose()\n        await asyncio.sleep(.1)\n",
        "    start_wait = time.time()\n    while not track.ready:\n        pg_bar(track.pos)\n        compose()\n        await asyncio.sleep(.1)\n        if time.time() - start_wait > 20:\n            break\n",
    )
    text = text.replace(
        "    while embed.counter()<0:\n        await asyncio.sleep(.1)\n",
        "    start_embed = time.time()\n    while embed.counter()<0:\n        await asyncio.sleep(.1)\n        if time.time() - start_embed > 20:\n            break\n",
    )
    index.write_text(text, encoding="utf-8")

pythons_url = "https://pygame-web.github.io/archives/0.9/pythons.js"
pythons_path = Path("build/web/pythons.js")
if not pythons_path.is_file():
    import urllib.request
    urllib.request.urlretrieve(pythons_url, pythons_path.as_posix())
if pythons_path.is_file():
    pj = pythons_path.read_text(encoding="utf-8")
    pj = pj.replace(
        "    if ( (location.hostname === \"localhost\") || cfg.module) {\n        config.cdn = url.split(\"?\",1)[0].replace(module_name, \"\")\n    }\n\n    config.cdn     = config.cdn || url.split(module_name, 1)[0]  //??=\n",
        "    if ( (location.hostname === \"localhost\") || cfg.module) {\n        if (!config.cdn) {\n            config.cdn = url.split(\"?\",1)[0].replace(module_name, \"\")\n        }\n    }\n\n    config.cdn     = config.cdn || url.split(module_name, 1)[0]  //??=\n",
    )
    pythons_path.write_text(pj, encoding="utf-8")

for name in ("vt.js", "vtx.js"):
    url = f"https://pygame-web.github.io/archives/0.9/{name}"
    path = Path("build/web") / name
    if not path.is_file():
        import urllib.request
        urllib.request.urlretrieve(url, path.as_posix())

vt_dir = Path("build/web/vt")
vt_dir.mkdir(parents=True, exist_ok=True)
vt_assets = [
    "xterm.js",
    "xterm-addon-image.js",
    "xterm.css",
]
import urllib.request
def try_download(urls, path):
    if path.is_file():
        return True
    for url in urls:
        try:
            urllib.request.urlretrieve(url, path.as_posix())
            return True
        except Exception:
            continue
    return False

vt_ok = True
for name in vt_assets:
    urls = [
        f"https://pygame-web.github.io/archives/0.9/vt/{name}",
        f"https://pygame-web.github.io/archives/vt/{name}",
    ]
    path = vt_dir / name
    if not try_download(urls, path):
        vt_ok = False

vtx_path = Path("build/web/vtx.js")
if vtx_path.is_file() and vt_ok:
    vtx = vtx_path.read_text(encoding="utf-8")
    vtx = vtx.replace(
        '        xterm_cdn = window.Module.config.cdn+"vt/"\n        console.log("Terminal+ImageAddon importing from CDN :", xterm_cdn)\n',
        '        xterm_cdn = "./vt/"\n        console.log("Terminal+ImageAddon importing from local :", xterm_cdn)\n',
    )
    vtx = vtx.replace(
        '        xterm_cdn = xterm_cdn || "https://pygame-web.github.io/archives/vt/"\n        console.warn("Terminal+ImageAddon importing from fallback ", xterm_cdn)\n',
        '        xterm_cdn = "./vt/"\n        console.warn("Terminal+ImageAddon importing from local ", xterm_cdn)\n',
    )
    vtx_path.write_text(vtx, encoding="utf-8")

repo_dir = Path("build/web/archives/repo/cp312")
repo_dir.mkdir(parents=True, exist_ok=True)
wheel_name = "pygame_static-1.0-cp312-cp312-wasm32_bi_emscripten.whl"
wheel_url = f"https://pygame-web.github.io/archives/repo/cp312/{wheel_name}"
wheel_path = repo_dir / wheel_name
if not wheel_path.is_file():
    import urllib.request
    urllib.request.urlretrieve(wheel_url, wheel_path.as_posix())
PY
