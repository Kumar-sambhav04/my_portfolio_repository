"""Exercise failures that must prevent a broken portfolio from publishing."""

import hashlib
import json
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from build_site import build_site, normalize_url
from check_site import validate_site
from verify_deployment import verify


HTML = '''<!doctype html><html lang="en"><head><title>Portfolio</title>
<meta name="description" content="AI portfolio"><meta property="og:url" content="https://old.example/">
<link href="styles.css" rel="stylesheet"><script src="app.js" defer></script></head>
<body><main id="main"><h1>AI engineering</h1><a href="#work">Work</a>
<section id="work"><img src="photo.jpg" alt="Portrait"><a href="resume.pdf" download>Resume</a>
<a href="https://github.com/example" target="_blank" rel="noopener">GitHub</a></section>
</main></body></html>'''
SHA = "a" * 40


class PublishingTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.source = self.root / "dist"
        self.source.mkdir()
        (self.source / "index.html").write_text(HTML)
        (self.source / "styles.css").write_text("body { color: #222; }")
        (self.source / "app.js").write_text("document.getElementById('work');")
        (self.source / "photo.jpg").write_bytes(b"fixture image")
        (self.source / "resume.pdf").write_bytes(b"%PDF-1.7\nfixture")

    def tearDown(self):
        self.temp.cleanup()

    def change_html(self, old, new):
        file = self.source / "index.html"
        file.write_text(file.read_text().replace(old, new))

    def test_complete_site_passes(self):
        self.assertEqual(validate_site(self.source), [])

    def test_missing_download_blocks_publishing(self):
        (self.source / "resume.pdf").unlink()
        self.assertTrue(any("missing local target" in e for e in validate_site(self.source)))

    def test_broken_navigation_blocks_publishing(self):
        self.change_html('href="#work"', 'href="#deleted-section"')
        self.assertTrue(any("missing anchor" in e for e in validate_site(self.source)))

    def test_removing_markup_needed_by_javascript_is_detected(self):
        self.change_html('id="work"', 'id="new-work"')
        self.assertTrue(any("JavaScript needs missing id" in e for e in validate_site(self.source)))

    def test_accessibility_regressions_are_detected(self):
        self.change_html(' alt="Portrait"', '')
        self.change_html('id="work"', 'id="main"')
        errors = validate_site(self.source)
        self.assertTrue(any("alt attribute" in e for e in errors))
        self.assertTrue(any("duplicate id" in e for e in errors))

    def test_hidden_files_and_symlinks_are_rejected(self):
        (self.source / ".env").write_text("PUBLICATION_MUST_FAIL=true")
        (self.root / "private.txt").write_text("not public")
        (self.source / "leak.txt").symlink_to(self.root / "private.txt")
        errors = validate_site(self.source)
        self.assertTrue(any("hidden file" in e for e in errors))
        self.assertTrue(any("Symlink" in e for e in errors))

    def test_directory_traversal_and_root_relative_paths_are_rejected(self):
        self.change_html('href="styles.css"', 'href="../private.css"')
        self.change_html('src="photo.jpg"', 'src="/photo.jpg"')
        errors = validate_site(self.source)
        self.assertTrue(any("escapes publish directory" in e for e in errors))
        self.assertTrue(any("root-relative" in e for e in errors))

    def test_bad_pdf_blocks_publishing(self):
        (self.source / "resume.pdf").write_bytes(b"not a pdf")
        self.assertTrue(any("invalid PDF" in e for e in validate_site(self.source)))

    def test_build_sets_hosting_metadata_and_preserves_assets(self):
        output = self.root / "_site"
        manifest = build_site(self.source, output, "https://example.github.io/portfolio", SHA)
        html = (output / "index.html").read_text()
        self.assertNotIn("https://old.example/", html)
        self.assertIn('rel="canonical" href="https://example.github.io/portfolio/"', html)
        self.assertIn("https://example.github.io/portfolio/sitemap.xml", (output / "robots.txt").read_text())
        self.assertEqual((output / "resume.pdf").read_bytes(), (self.source / "resume.pdf").read_bytes())
        self.assertEqual(manifest["commit"], SHA)
        self.assertTrue((output / ".nojekyll").is_file())
        self.assertNotIn(".nojekyll", manifest["files"])
        for name, digest in manifest["files"].items():
            self.assertEqual(hashlib.sha256((output / name).read_bytes()).hexdigest(), digest)
        self.assertEqual(validate_site(output), [])

    def test_output_cannot_overwrite_unrelated_files(self):
        output = self.root / "important"
        output.mkdir()
        (output / "keep.txt").write_text("keep")
        with self.assertRaises(ValueError):
            build_site(self.source, output, "https://example.github.io/", SHA)
        self.assertTrue((output / "keep.txt").exists())

    def test_invalid_production_urls_are_rejected(self):
        for url in ["http://example.com", "https://user:pass@example.com", "https://example.com/?secret=x", "https://example.com/#part"]:
            with self.subTest(url=url), self.assertRaises(ValueError):
                normalize_url(url)

    def test_live_check_rejects_stale_commit_and_changed_asset(self):
        output = self.root / "_site"
        manifest = build_site(self.source, output, "https://example.github.io/", SHA)
        responses = {f"https://example.github.io/{name}?deployment={SHA}": (output / name).read_bytes()
                     for name in manifest["files"]}
        key = f"https://example.github.io/build-info.json?deployment={SHA}"
        responses[key] = (output / "build-info.json").read_bytes()
        self.assertEqual(verify("https://example.github.io/", SHA, responses.__getitem__), len(manifest["files"]))
        responses[f"https://example.github.io/styles.css?deployment={SHA}"] = b"outdated styles"
        with self.assertRaisesRegex(ValueError, "differs"):
            verify("https://example.github.io/", SHA, responses.__getitem__)
        manifest["commit"] = "b" * 40
        responses[key] = json.dumps(manifest).encode()
        with self.assertRaisesRegex(ValueError, "requested commit"):
            verify("https://example.github.io/", SHA, responses.__getitem__)


if __name__ == "__main__":
    unittest.main()
