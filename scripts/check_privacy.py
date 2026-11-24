#!/usr/bin/env python3
"""Keep contact surfaces redacted without storing private values."""
from html.parser import HTMLParser
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]


class ContactPage(HTMLParser):
    def __init__(self):
        super().__init__()
        self.errors = []
        self.blocks = []
        self.stack = []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == 'form' or attrs.get('type') == 'submit':
            self.errors.append('Contact messaging must remain disabled.')
        if tag == 'a' and attrs.get('href', '').lower().startswith(('http:', 'https:', 'mailto:', 'tel:')):
            self.errors.append('Contact page must not expose external contact links.')
        if tag == 'script' and any(x in attrs.get('src', '') for x in ('recaptcha', 'maps.googleapis', 'maps-loader', 'maps-config', 'jquery.googlemap')):
            self.errors.append('Contact page must not load location or message services.')
        capture = 'ci-text' in attrs.get('class', '').split() or attrs.get('id') == 'map'
        if capture:
            self.blocks.append([])
        if tag not in ('area', 'base', 'br', 'col', 'embed', 'hr', 'img', 'input', 'link', 'meta', 'param', 'source', 'track', 'wbr'):
            self.stack.append((tag, len(self.blocks) - 1 if capture else None))

    def handle_endtag(self, tag):
        while self.stack:
            current, _ = self.stack.pop()
            if current == tag:
                break

    def handle_data(self, data):
        text = data.strip()
        if not text:
            return
        active = [capture for _, capture in self.stack if capture is not None]
        if active:
            self.blocks[active[-1]].append(text)


def check(contact):
    page = ContactPage()
    page.feed(contact)
    allowed = {'redacted', 'Instagram', 'Discord', 'WeChat', 'Contact details are redacted.'}
    if len(page.blocks) != 7:
        page.errors.append('Expected one redacted location and six redacted contact blocks.')
    for block in page.blocks:
        if 'redacted' not in block or any(value not in allowed for value in block):
            page.errors.append('A contact or location block is not fully redacted.')
    return page.errors


def main():
    if '--staged' in sys.argv:
        contact = subprocess.check_output(['git', 'show', ':contact.html'], cwd=ROOT).decode()
    else:
        contact = (ROOT / 'contact.html').read_text()
    errors = check(contact)
    if errors:
        print('\n'.join(sorted(set(errors))), file=sys.stderr)
        return 1
    print('Contact privacy check passed.')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
