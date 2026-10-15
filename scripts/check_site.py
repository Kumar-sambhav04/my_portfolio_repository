"""Dependency-free checks for the actual files published to the portfolio."""

import argparse
from collections import Counter
from html.parser import HTMLParser
from pathlib import Path
import re
import subprocess
from urllib.parse import unquote, urlsplit


class Page(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.elements = []
        self.text = []
        self.in_title = False
        self.title = []

    def handle_starttag(self, tag, attrs):
        self.elements.append((tag, dict(attrs)))
        if tag == "title":
            self.in_title = True

    handle_startendtag = handle_starttag

    def handle_endtag(self, tag):
        if tag == "title":
            self.in_title = False

    def handle_data(self, data):
        self.text.append(data)
        if self.in_title:
            self.title.append(data)


def validate_site(directory):
    root = Path(directory).resolve()
    errors = []
    if not (root / "index.html").is_file():
        return ["Missing index.html"]
    files = sorted(root.rglob("*"))
    allowed = {".html", ".css", ".js", ".json", ".svg", ".png", ".jpg", ".jpeg",
               ".webp", ".avif", ".ico", ".pdf", ".txt", ".xml", ".woff", ".woff2"}
    for file in files:
        relative = file.relative_to(root)
        if file.is_symlink():
            errors.append(f"Symlink cannot be published: {relative}")
        if file.is_file():
            if any(part.startswith(".") for part in relative.parts) and relative.as_posix() != ".nojekyll":
                errors.append(f"Unexpected hidden file in publish directory: {relative}")
            if file.suffix.lower() not in allowed and file.name != ".nojekyll":
                errors.append(f"Unexpected file type in publish directory: {relative}")
            if file.stat().st_size > 10 * 1024 * 1024:
                errors.append(f"Asset exceeds portfolio's 10 MiB budget: {relative}")

    pages = {}
    for file in files:
        if file.suffix == ".html" and file.is_file() and not file.is_symlink():
            page = Page()
            page.feed(file.read_text(encoding="utf-8"))
            pages[file] = page
            ids = [attrs["id"] for _, attrs in page.elements if attrs.get("id")]
            for identifier, count in Counter(ids).items():
                if count > 1:
                    errors.append(f"{file.name}: duplicate id {identifier!r}")
            if not "".join(page.title).strip():
                errors.append(f"{file.name}: missing or empty page title")
            if sum(tag == "h1" for tag, _ in page.elements) != 1:
                errors.append(f"{file.name}: expected one h1")
            if sum(tag == "main" for tag, _ in page.elements) != 1:
                errors.append(f"{file.name}: expected one main element")
            if not any(tag == "meta" and attrs.get("name") == "description" and
                       attrs.get("content", "").strip() for tag, attrs in page.elements):
                errors.append(f"{file.name}: missing page description")
            for tag, attrs in page.elements:
                if tag == "img" and "alt" not in attrs:
                    errors.append(f"{file.name}: image needs an alt attribute")
                if attrs.get("target") == "_blank" and "noopener" not in attrs.get("rel", "").split():
                    errors.append(f"{file.name}: new-tab link needs rel=noopener")
                for key in ("aria-controls", "aria-labelledby", "aria-describedby"):
                    for identifier in attrs.get(key, "").split():
                        if identifier not in ids:
                            errors.append(f"{file.name}: {key} refers to missing id {identifier!r}")

    def check_reference(source, reference):
        parsed = urlsplit(reference)
        if parsed.scheme in {"https", "http"}:
            if not parsed.netloc or parsed.username or parsed.password:
                errors.append(f"{source.name}: invalid web URL")
            return
        if parsed.scheme in {"mailto", "tel", "data"}:
            return
        if parsed.scheme or parsed.netloc or parsed.path.startswith("/"):
            errors.append(f"{source.name}: unsupported or root-relative URL {reference!r}")
            return
        target = (source.parent / unquote(parsed.path)).resolve() if parsed.path else source
        if not target.is_relative_to(root):
            errors.append(f"{source.name}: reference escapes publish directory: {reference!r}")
            return
        if target.is_dir():
            target = target / "index.html"
        if not target.is_file():
            errors.append(f"{source.name}: missing local target {reference!r}")
            return
        if parsed.fragment and target.suffix == ".html" and target in pages:
            target_ids = {a.get("id") for _, a in pages[target].elements}
            if unquote(parsed.fragment) not in target_ids:
                errors.append(f"{source.name}: missing anchor {reference!r}")

    for file, page in pages.items():
        for _, attrs in page.elements:
            for key in ("href", "src", "poster"):
                if attrs.get(key):
                    check_reference(file, attrs[key])
        # Catch edits that remove markup still needed by the JavaScript.
        page_ids = {attrs.get("id") for _, attrs in page.elements}
        for tag, attrs in page.elements:
            if tag == "script" and attrs.get("src"):
                parsed = urlsplit(attrs["src"])
                script = (file.parent / parsed.path).resolve()
                if not parsed.scheme and script.is_relative_to(root) and script.is_file():
                    for identifier in re.findall(r"getElementById\(['\"]([^'\"]+)['\"]\)", script.read_text()):
                        if identifier not in page_ids:
                            errors.append(f"{file.name}: JavaScript needs missing id {identifier!r}")
    for file in files:
        if file.suffix == ".css" and file.is_file() and not file.is_symlink():
            for match in re.finditer(r"url\(\s*['\"]?([^)'\"\s]+)", file.read_text()):
                if not match[1].startswith("#"):
                    check_reference(file, match[1])
    for file in files:
        if file.suffix == ".pdf" and file.is_file() and not file.is_symlink():
            with file.open("rb") as stream:
                if stream.read(5) != b"%PDF-":
                    errors.append(f"{file.name}: invalid PDF header")
    return errors


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("directory", nargs="?", default="dist")
    parser.add_argument("--javascript", action="store_true", help="Also check every JavaScript file using Node.js")
    args = parser.parse_args()
    errors = validate_site(args.directory)
    if args.javascript:
        for script in sorted(Path(args.directory).rglob("*.js")):
            try:
                result = subprocess.run(["node", "--check", str(script)], capture_output=True, text=True)
            except FileNotFoundError:
                errors.append("Node.js is required for JavaScript syntax checks")
                break
            if result.returncode:
                errors.append(f"{script}: JavaScript syntax check failed\n{result.stderr}")
    if errors:
        for error in errors:
            print(f"FAIL: {error}")
        raise SystemExit(1)
    print(f"PASS: local links, assets, anchors, metadata, and markup references in {args.directory}")


if __name__ == "__main__":
    main()
