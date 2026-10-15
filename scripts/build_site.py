"""Package only public files and set metadata for the actual hosting address."""

import argparse
import hashlib
from html import escape
import json
from pathlib import Path
import re
import shutil
from urllib.parse import urlsplit
from check_site import validate_site


ROOT = Path(__file__).resolve().parents[1]


def normalize_url(value):
    parsed = urlsplit(value)
    if (parsed.scheme != "https" or not parsed.hostname or parsed.username or
            parsed.password or parsed.query or parsed.fragment or
            any(c.isspace() for c in value) or ".." in parsed.path.split("/")):
        raise ValueError("Production URL must be an absolute HTTPS address without credentials, query, or fragment")
    return value.rstrip("/") + "/"


def build_site(source, output, url, commit="local"):
    source, output = Path(source).resolve(), Path(output).resolve()
    # Never recursively remove an arbitrary caller-supplied location.
    if output != source.parent / "_site" or source == output:
        raise ValueError("Build output must be the _site directory beside the source directory")
    url = normalize_url(url)
    if commit != "local" and not re.fullmatch(r"[0-9a-f]{40}", commit):
        raise ValueError("Commit must be a full Git SHA or 'local'")
    errors = validate_site(source)
    if errors:
        raise ValueError("Source checks failed: " + "; ".join(errors))
    if output.is_symlink():
        raise ValueError("Refusing a symlink build directory")
    if output.exists():
        shutil.rmtree(output)
    shutil.copytree(source, output)
    index = output / "index.html"
    html = index.read_text(encoding="utf-8")
    html = re.sub(r'<link\b(?=[^>]*\brel=[\"\']canonical[\"\'])[^>]*>\s*', '', html, flags=re.I)
    html = re.sub(r'<meta\b(?=[^>]*\bproperty=[\"\']og:url[\"\'])[^>]*>\s*', '', html, flags=re.I)
    metadata = (f'  <link rel="canonical" href="{escape(url, quote=True)}">\n'
                f'  <meta property="og:url" content="{escape(url, quote=True)}">\n')
    html = html.replace("</head>", metadata + "</head>", 1)
    index.write_text(html, encoding="utf-8")
    (output / ".nojekyll").touch()
    (output / "robots.txt").write_text(f"User-agent: *\nAllow: /\nSitemap: {url}sitemap.xml\n")
    (output / "sitemap.xml").write_text(
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
        f'<url><loc>{escape(url)}</loc></url></urlset>\n')
    # GitHub uses .nojekyll as a publishing marker but does not serve it as a public asset.
    hashes = {p.relative_to(output).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
              for p in sorted(output.rglob("*")) if p.is_file() and p.name not in {"build-info.json", ".nojekyll"}}
    manifest = {"generator": "kumar-portfolio", "commit": commit, "url": url, "files": hashes}
    (output / "build-info.json").write_text(json.dumps(manifest, indent=2) + "\n")
    errors = validate_site(output)
    if errors:
        raise ValueError("Packaged site checks failed: " + "; ".join(errors))
    return manifest


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--url", default="")
    parser.add_argument("--commit", default="local")
    args = parser.parse_args()
    configured = json.loads((ROOT / "site.json").read_text())["production_url"]
    manifest = build_site(ROOT / "dist", ROOT / "_site", args.url or configured, args.commit)
    print(f"PASS: packaged {len(manifest['files'])} public files for {manifest['url']}")


if __name__ == "__main__":
    main()
