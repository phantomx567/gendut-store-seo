#!/usr/bin/env python3
"""Build the public website with the host's actual address. No account access."""
import argparse
from html import escape, unescape
from html.parser import HTMLParser
import json
import os
from pathlib import Path
import re
import shutil
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[1]


def validate_origin(value):
    parsed = urlsplit(value or '')
    host = parsed.hostname or ''
    if (parsed.scheme != 'https' or not host or '.' not in host
            or parsed.username or parsed.password or parsed.port
            or parsed.path not in ('', '/') or parsed.query or parsed.fragment
            or host.endswith('.chatgpt.site') or host == 'gendutstore.com'):
        raise ValueError('Alamat HTTPS hosting publik belum tersedia atau tidak sesuai.')
    return 'https://' + host.lower()


class Page(HTMLParser):
    def __init__(self):
        super().__init__()
        self.assets = []
        self.headings = 0

    def handle_starttag(self, tag, pairs):
        attrs = dict(pairs)
        if tag == 'h1':
            self.headings += 1
        if attrs.get('src'):
            self.assets.append(attrs['src'])
        if tag == 'link' and attrs.get('rel') in ('stylesheet', 'icon', 'apple-touch-icon'):
            self.assets.append(attrs['href'])


def build(address, output):
    address = validate_origin(address)
    source = ROOT / 'dist'
    if output.exists() and any(output.iterdir()):
        raise ValueError('Direktori output harus kosong; hasil lama tidak ditimpa.')
    html = (source / 'index.html').read_text()
    title = unescape(re.search(r'<title>(.*?)</title>', html, re.S).group(1))
    description = unescape(re.search(r'<meta name="description" content="([^"]+)"', html).group(1))
    html = re.sub(r'\s*<link rel="canonical"[^>]*>', '', html)
    html = re.sub(r'\s*<meta property="og:(?:url|image(?::[a-z]+)?)"[^>]*>', '', html)
    html = re.sub(r'\s*<script type="application/ld\+json">[\s\S]*?</script>', '', html)
    metadata = '\n'.join([
        '<link rel="canonical" href="' + escape(address + '/', quote=True) + '">',
        '<meta property="og:url" content="' + escape(address + '/', quote=True) + '">',
        '<meta property="og:image" content="' + escape(address + '/assets/gendut-store-social.png', quote=True) + '">',
        '<meta property="og:image:width" content="1080">',
        '<meta property="og:image:height" content="1080">',
        '<meta property="og:image:alt" content="Logo Gendut Store">',
        '<script type="application/ld+json">' + json.dumps({
            '@context': 'https://schema.org', '@graph': [
                {'@type': 'WebSite', '@id': address + '/#website', 'url': address + '/',
                 'name': 'Panduan Gendut Store', 'inLanguage': 'id'},
                {'@type': 'WebPage', '@id': address + '/#webpage', 'url': address + '/',
                 'name': title, 'description': description, 'inLanguage': 'id',
                 'isPartOf': {'@id': address + '/#website'}}
            ]}, ensure_ascii=False).replace('</', '<\\/') + '</script>'
    ])
    html = html.replace('</head>', metadata + '\n</head>')
    html = re.sub(r'(\b(?:src|href)=")/(?!/)', r'\1', html)
    if '.chatgpt.site' in html:
        raise ValueError('Masih ada alamat hosting lama pada website publik.')
    page = Page()
    page.feed(html)
    if page.headings != 1 or not title or not description:
        raise ValueError('Judul, deskripsi, dan satu H1 diperlukan.')
    for asset in page.assets:
        path = source / asset
        if not path.is_file() or not path.resolve().is_relative_to(source.resolve()):
            raise ValueError('Aset lokal tidak valid: ' + asset)
    output.mkdir(parents=True, exist_ok=True)
    allowed = {'.html', '.css', '.js', '.png', '.webp', '.svg', '.ico', '.xml', '.txt'}
    for path in sorted(source.rglob('*')):
        if not path.is_file() or path.name in ('index.html', 'robots.txt', 'sitemap.xml'):
            continue
        if path.is_symlink() or path.suffix not in allowed or any(part.startswith('.') for part in path.relative_to(source).parts):
            raise ValueError('Berkas yang bukan aset publik ditolak.')
        target = output / path.relative_to(source)
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(path, target)
    (output / 'index.html').write_text(html)
    (output / 'robots.txt').write_text('User-agent: *\nAllow: /\n\nSitemap: ' + address + '/sitemap.xml\n')
    (output / 'sitemap.xml').write_text('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"><url><loc>' + escape(address + '/') + '</loc></url></urlset>\n')
    return {'output': str(output), 'origin': address, 'files': sum(p.is_file() for p in output.rglob('*')), 'published': False}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--origin', default=os.environ.get('SITE_ORIGIN') or os.environ.get('RENDER_EXTERNAL_URL'))
    parser.add_argument('--output', type=Path, default=ROOT / 'public')
    args = parser.parse_args()
    try:
        print(json.dumps(build(args.origin, args.output)))
    except (ValueError, OSError) as error:
        parser.exit(1, str(error) + '\n')
