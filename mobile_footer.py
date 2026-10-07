#!/usr/bin/env python3
"""
Udaan Abacus - NEW MOBILE FOOTER ONLY (phones, screen width <= 640px).

What this changes:
  * Adds a new mobile footer right after the existing footer, plus one <style> block in <head>.
  * On phones the old footer is hidden and the new one is shown.

What this does NOT touch:
  * The existing footer HTML (it stays in the file, byte for byte; it is only hidden on phones).
  * Desktop and tablet (>= 641px): nothing changes.
  * Header, menu, page content, scripts, line endings (CRLF/LF) - all left as they are.

Safe to re-run: the two inserted blocks are wrapped in markers and get replaced, never duplicated.
Every changed file is backed up first (same folder structure) in _backup_mobile_footer_<time>/.

Usage (run from anywhere):
    python mobile_footer.py                      # site folder = the folder this script is in
    python mobile_footer.py "C:\\path\\Udaan Web"  # or give the folder explicitly
    python mobile_footer.py --dry-run            # show what would happen, change nothing
    python mobile_footer.py --restore            # undo: remove the new footer from every page
"""
import argparse
import re
import shutil
import sys
from datetime import datetime
from pathlib import Path

# ----------------------------------------------------------------- settings
MOBILE_MAX = 640  # px. Same breakpoint your site already uses for its single-column footer.

PHONE_TEL = "+918827773391"
PHONE_TEXT = "+91 88277 73391"
EMAIL = "admin@udaanabacus.com"
FACEBOOK = "https://www.facebook.com/udaan.abacus/"
INSTAGRAM = "https://www.instagram.com/udaan.abacus/"
LINKEDIN = "https://www.linkedin.com/company/udaan-abacus"
COPYRIGHT = "&copy; 2026 Udaan Abacus Pvt. Ltd. All Rights Reserved."
# -------------------------------------------------------------------------

CSS_START, CSS_END = "<!-- udaan-mobile-footer:css:start -->", "<!-- udaan-mobile-footer:css:end -->"
HTML_START, HTML_END = "<!-- udaan-mobile-footer:html:start -->", "<!-- udaan-mobile-footer:html:end -->"

SVG_FB = '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M22 12.06C22 6.51 17.52 2 12 2S2 6.51 2 12.06c0 5.02 3.66 9.18 8.44 9.94v-7.03H7.9v-2.91h2.54V9.85c0-2.51 1.49-3.89 3.77-3.89 1.09 0 2.23.2 2.23.2v2.46h-1.26c-1.24 0-1.63.77-1.63 1.56v1.88h2.78l-.44 2.91h-2.34V22c4.78-.76 8.44-4.92 8.44-9.94Z"/></svg>'
SVG_IG = '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M12 2c-2.72 0-3.06.01-4.12.06-1.06.05-1.78.22-2.41.46a4.87 4.87 0 0 0-1.76 1.15A4.87 4.87 0 0 0 2.56 5.43c-.24.63-.41 1.35-.46 2.41C2.05 8.9 2.04 9.24 2.04 12s.01 3.1.06 4.16c.05 1.06.22 1.78.46 2.41.25.65.6 1.2 1.15 1.76.56.55 1.11.9 1.76 1.15.63.24 1.35.41 2.41.46 1.06.05 1.4.06 4.12.06s3.06-.01 4.12-.06c1.06-.05 1.78-.22 2.41-.46a4.87 4.87 0 0 0 1.76-1.15 4.87 4.87 0 0 0 1.15-1.76c.24-.63.41-1.35.46-2.41.05-1.06.06-1.4.06-4.16s-.01-3.1-.06-4.16c-.05-1.06-.22-1.78-.46-2.41a4.87 4.87 0 0 0-1.15-1.76A4.87 4.87 0 0 0 18.53 2.5c-.63-.24-1.35-.41-2.41-.46C15.06 2.01 14.72 2 12 2Zm0 1.8c2.67 0 2.99.01 4.04.06.98.05 1.51.21 1.86.35.47.18.8.4 1.15.75.35.35.57.68.75 1.15.14.35.3.88.35 1.86.05 1.05.06 1.37.06 4.04s-.01 2.99-.06 4.04c-.05.98-.21 1.51-.35 1.86-.18.47-.4.8-.75 1.15-.35.35-.68.57-1.15.75-.35.14-.88.3-1.86.35-1.05.05-1.37.06-4.04.06s-2.99-.01-4.04-.06c-.98-.05-1.51-.21-1.86-.35a3.09 3.09 0 0 1-1.15-.75 3.09 3.09 0 0 1-.75-1.15c-.14-.35-.3-.88-.35-1.86-.05-1.05-.06-1.37-.06-4.04s.01-2.99.06-4.04c.05-.98.21-1.51.35-1.86.18-.47.4-.8.75-1.15.35-.35.68-.57 1.15-.75.35-.14.88-.3 1.86-.35C9.01 3.81 9.33 3.8 12 3.8Zm0 3.06a5.14 5.14 0 1 0 0 10.28 5.14 5.14 0 0 0 0-10.28Zm0 8.48a3.34 3.34 0 1 1 0-6.68 3.34 3.34 0 0 1 0 6.68Zm5.34-8.68a1.2 1.2 0 1 1-2.4 0 1.2 1.2 0 0 1 2.4 0Z"/></svg>'
SVG_LI = '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M20.45 2H3.55A1.55 1.55 0 0 0 2 3.55v16.9A1.55 1.55 0 0 0 3.55 22h16.9A1.55 1.55 0 0 0 22 20.45V3.55A1.55 1.55 0 0 0 20.45 2ZM8.34 18.34H5.67V9.75h2.67v8.59ZM7 8.6a1.55 1.55 0 1 1 0-3.1 1.55 1.55 0 0 1 0 3.1Zm11.34 9.74h-2.67v-4.18c0-1-.02-2.28-1.39-2.28-1.4 0-1.61 1.09-1.61 2.21v4.25H10V9.75h2.56v1.17h.04c.36-.68 1.23-1.39 2.53-1.39 2.7 0 3.21 1.78 3.21 4.09v4.72Z"/></svg>'


def build_css():
    return f"""{CSS_START}
<style id="udaan-mobile-footer-only">
/* Mobile footer (phones only). Hidden everywhere else. */
footer.udaan-mobile-footer{{display:none}}
@media (max-width:{MOBILE_MAX}px){{
  /* hide the existing footer on phones (it is still in the HTML) */
  footer:not(.udaan-mobile-footer){{display:none !important}}

  footer.udaan-mobile-footer{{display:block !important;background:#061b3d;color:#dce8ff;padding:36px 20px 20px;font-family:inherit;box-sizing:border-box;text-align:left}}
  footer.udaan-mobile-footer *,footer.udaan-mobile-footer *::before,footer.udaan-mobile-footer *::after{{box-sizing:border-box}}
  footer.udaan-mobile-footer a{{text-decoration:none}}

  .udaan-mobile-footer .umf-logo{{display:block;width:72px;height:72px;object-fit:contain;background:#fff;border-radius:10px;padding:8px;margin:0 0 14px}}
  .udaan-mobile-footer .umf-tag{{color:#dce8ff;font-weight:700;line-height:1.4;font-size:15px;margin:0 0 16px;max-width:none}}
  .udaan-mobile-footer .umf-social{{display:flex;gap:10px;margin:0 0 28px;padding:0}}
  .udaan-mobile-footer .umf-social a{{width:34px;height:34px;border-radius:50%;background:rgba(255,255,255,.08);display:grid;place-items:center;transform:none}}
  .udaan-mobile-footer .umf-social svg{{width:16px;height:16px;fill:#dce8ff}}

  .udaan-mobile-footer .umf-grid{{display:grid;grid-template-columns:1fr 1fr;gap:18px 14px;margin:0 0 20px}}
  .udaan-mobile-footer .umf-section{{min-width:0}}
  .udaan-mobile-footer .umf-section h3{{color:#f4c85d;margin:0 0 10px;font-size:12px;line-height:1.25;letter-spacing:.04em;text-transform:uppercase;font-weight:800}}
  .udaan-mobile-footer .umf-section h3.umf-h3-gap{{margin-top:14px}}
  .udaan-mobile-footer .umf-section ul{{list-style:none;margin:0;padding:0}}
  .udaan-mobile-footer .umf-section li{{margin:0 0 4px;padding:0;line-height:1.35;font-size:13px;color:#c9d8ec}}
  .udaan-mobile-footer .umf-section li a,.udaan-mobile-footer .umf-section li span{{color:#c9d8ec}}
  .udaan-mobile-footer .umf-section li strong{{display:block;color:#8fa3c4;font-size:10.5px;font-weight:600;margin:0 0 1px;line-height:1.35}}
  .udaan-mobile-footer .umf-nowrap{{white-space:nowrap}}
  .udaan-mobile-footer .umf-nowrap a,.udaan-mobile-footer .umf-nowrap span{{font-size:12.5px}}

  /* Classes accordion inside Quick Links */
  /* (the site has global FAQ styles for details/summary - reset them here so the footer stays clean) */
  .udaan-mobile-footer details.umf-classes{{margin:0 0 4px;padding:0;background:none;border:0;border-radius:0;box-shadow:none}}
  .udaan-mobile-footer details.umf-classes>summary{{list-style:none;position:static;cursor:pointer;color:#c9d8ec;font-size:13px;font-weight:400;line-height:1.35;padding:0;margin:0;background:none;border:0;display:flex;align-items:center;gap:6px}}
  .udaan-mobile-footer details.umf-classes>summary::-webkit-details-marker{{display:none}}
  .udaan-mobile-footer details.umf-classes>summary::marker{{content:""}}
  .udaan-mobile-footer details.umf-classes>summary::after{{content:"\\25BE";position:static;right:auto;top:auto;font-size:10px;font-weight:400;color:#8fa3c4;transition:transform .2s}}
  .udaan-mobile-footer details.umf-classes[open]>summary::after{{transform:rotate(180deg)}}
  .udaan-mobile-footer details.umf-classes ul{{margin:6px 0 0 14px;padding:0;border-left:1px solid rgba(255,255,255,.12)}}
  .udaan-mobile-footer details.umf-classes li{{padding-left:10px}}

  .udaan-mobile-footer .umf-copy{{border-top:1px solid rgba(255,255,255,.12);padding-top:16px;text-align:center}}
  .udaan-mobile-footer .umf-line1{{color:#aebbd0;font-size:12px;line-height:1.5;white-space:nowrap;margin:0}}
  .udaan-mobile-footer .umf-legal{{margin-top:8px;font-size:12px;line-height:1.6}}
  .udaan-mobile-footer .umf-legal a{{color:#9fb3d6;text-decoration:underline;text-underline-offset:2px}}
  .udaan-mobile-footer .umf-dot{{color:#5a6c8c;margin:0 7px}}
}}
@media (max-width:360px){{
  .udaan-mobile-footer .umf-line1{{white-space:normal}}
  .udaan-mobile-footer .umf-legal .umf-dot{{margin:0 4px}}
}}
</style>
{CSS_END}"""


def build_html(prefix):
    p = prefix
    return f"""{HTML_START}
<footer class="udaan-mobile-footer" aria-label="Site footer">
  <img class="umf-logo" src="{p}assets/udaan-logo-full.jpeg" alt="Udaan Abacus Academy logo" width="72" height="72" loading="lazy">
  <p class="umf-tag">Helping Children Build the Ability to Think.</p>
  <div class="umf-social">
    <a href="{FACEBOOK}" target="_blank" rel="noopener" aria-label="Udaan Abacus on Facebook">{SVG_FB}</a>
    <a href="{INSTAGRAM}" target="_blank" rel="noopener" aria-label="Udaan Abacus on Instagram">{SVG_IG}</a>
    <a href="{LINKEDIN}" target="_blank" rel="noopener" aria-label="Udaan Abacus on LinkedIn">{SVG_LI}</a>
  </div>

  <div class="umf-grid">
    <div class="umf-section">
      <h3>Quick Links</h3>
      <ul>
        <li>
          <details class="umf-classes">
            <summary>Classes</summary>
            <ul>
              <li><a href="{p}online-abacus-classes.html">Online (Live)</a></li>
              <li><a href="{p}abacus-classes-indore.html">Indore Centre</a></li>
              <li><a href="{p}abacus-classes-jodhpur.html">Jodhpur Centre</a></li>
            </ul>
          </details>
        </li>
        <li><a href="{p}about.html">About Us</a></li>
        <li><a href="{p}studio.html">Udaan Studio</a></li>
        <li><a href="{p}insights.html">Insights</a></li>
        <li><a href="{p}programs.html">Partner With Us</a></li>
        <li><a href="{p}contact.html">Contact Us</a></li>
      </ul>
    </div>

    <div class="umf-section">
      <h3>Contact</h3>
      <ul>
        <li class="umf-nowrap"><strong>Phone</strong><a href="tel:{PHONE_TEL}">{PHONE_TEXT}</a></li>
        <li class="umf-nowrap"><strong>Email</strong><a href="mailto:{EMAIL}">{EMAIL}</a></li>
      </ul>
      <h3 class="umf-h3-gap">Locations</h3>
      <ul>
        <li><strong>Flagship Centre</strong><span>Tower Square, Khatiwala Tank, Indore - 452014</span></li>
        <li><strong>Corporate Office</strong><span>Chhatarpur Pahari, New Delhi - 110074</span></li>
      </ul>
    </div>
  </div>

  <div class="umf-copy">
    <div class="umf-line1">{COPYRIGHT}</div>
    <div class="umf-legal">
      <a href="{p}privacy-policy.html">Privacy Policy</a><span class="umf-dot">&bull;</span><a href="{p}terms-and-conditions.html">Terms &amp; Conditions</a><span class="umf-dot">&bull;</span><a href="{p}refund-policy.html">Refund Policy</a>
    </div>
  </div>
</footer>
{HTML_END}"""


RE_CSS = re.compile(re.escape(CSS_START) + r".*?" + re.escape(CSS_END) + r"(\r?\n)?", re.S)
RE_HTML = re.compile(r"(\r?\n)?" + re.escape(HTML_START) + r".*?" + re.escape(HTML_END), re.S)
RE_FOOTER_OPEN = re.compile(r"<footer\b[^>]*>", re.I)


def strip_ours(text):
    return RE_HTML.sub("", RE_CSS.sub("", text))


def transform(rel, text, restore=False):
    """Returns (new_text, status). Only the two marked blocks are ever added/removed."""
    nl = "\r\n" if "\r\n" in text else "\n"
    clean = strip_ours(text)
    if restore:
        return clean, ("removed" if clean != text else "nothing to remove")

    footers = RE_FOOTER_OPEN.findall(clean)
    if len(footers) != 1:
        return text, f"SKIPPED: expected exactly 1 <footer>, found {len(footers)}"
    if "</head>" not in clean:
        return text, "SKIPPED: no </head>"
    m = RE_FOOTER_OPEN.search(clean)
    end = clean.find("</footer>", m.end())
    if end == -1:
        return text, "SKIPPED: footer is not closed"
    end += len("</footer>")

    prefix = "../" * rel.count("/")
    html_block = nl + build_html(prefix).replace("\n", nl)
    css_block = build_css().replace("\n", nl) + nl

    out = clean[:end] + html_block + clean[end:]
    i = out.find("</head>")
    out = out[:i] + css_block + out[i:]
    return out, ("updated" if out != text else "already up to date")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("root", nargs="?", default=None, help="site folder (default: folder of this script)")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--restore", action="store_true", help="remove the mobile footer from all pages")
    a = ap.parse_args()

    root = Path(a.root).resolve() if a.root else Path(__file__).resolve().parent
    if not (root / "index.html").exists():
        sys.exit(f"ERROR: index.html not found in:\n  {root}\nPut this script in the site folder, or pass the folder path.")

    backup = root / f"_backup_mobile_footer_{datetime.now():%Y%m%d_%H%M%S}"
    changed = skipped = 0
    for f in sorted(root.rglob("*.html")):
        rel = f.relative_to(root).as_posix()
        if rel.split("/")[0].startswith("_backup") or f.name == "footer_mockup.html":
            continue
        raw = f.read_bytes()
        try:
            text = raw.decode("utf-8")
        except UnicodeDecodeError:
            print(f"!! {rel}: not valid UTF-8, left untouched")
            skipped += 1
            continue
        new, status = transform(rel, text, a.restore)
        flag = "!!" if status.startswith("SKIPPED") else "OK"
        print(f"{flag} {rel}: {status}")
        if status.startswith("SKIPPED"):
            skipped += 1
        if new != text and not a.dry_run:
            dest = backup / rel
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(f, dest)
            f.write_bytes(new.encode("utf-8"))
            changed += 1

    print()
    if a.dry_run:
        print("Dry run - nothing was written.")
    else:
        print(f"Done. {changed} page(s) changed" + (f", backups in {backup.name}" if changed else "") + ".")
    if skipped:
        print(f"{skipped} page(s) skipped - see '!!' lines above.")


if __name__ == "__main__":
    main()