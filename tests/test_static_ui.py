"""Static UI smoke checks; browser execution is additionally tested by Node tests."""
from html.parser import HTMLParser
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parent.parent


class IDs(HTMLParser):
    def __init__(self):
        super().__init__()
        self.ids = []
        self.scripts = []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if "id" in attrs:
            self.ids.append(attrs["id"])
        if tag == "script":
            self.scripts.append(attrs.get("src"))


def test_ui_has_unique_ids_and_correct_relative_js_paths():
    for directory, script in [(ROOT, "./app.mjs"), (ROOT / "web", "../app.mjs")]:
        html = (directory / "index.html").read_text(encoding="utf-8")
        parser = IDs()
        parser.feed(html)
        assert len(parser.ids) == len(set(parser.ids))
        assert script in parser.scripts
        assert (directory / script).is_file()
        assert "[hidden] { display:none !important; }" in html


def test_static_app_never_fabricates_api_results():
    html = (ROOT / "index.html").read_text(encoding="utf-8")
    app = (ROOT / "app.mjs").read_text(encoding="utf-8")
    assert "DOSSIER-SIM" not in html + app
    assert "HMAC_SHA256_" not in html + app
    assert "fetch('/api/audit'" not in html + app
    assert "document.querySelector('#out-potassium')" in app
    assert 'href="https://doi.org/10.2337/dci24-0032"' in html
