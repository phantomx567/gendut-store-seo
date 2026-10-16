#!/usr/bin/env python3
"""Validate and build public pages with host-specific SEO and release evidence."""
import argparse
from datetime import datetime, timezone
from html import escape, unescape
from html.parser import HTMLParser
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import importlib.util
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
        super().__init__(); self.assets = []; self.links = []; self.headings = 0; self.in_h1=False; self.heading_text=[]; self.ids=set()
    def handle_starttag(self, tag, pairs):
        attrs = dict(pairs)
        if tag == 'h1': self.headings += 1; self.in_h1=True
        if attrs.get('id'): self.ids.add(attrs['id'])
        if attrs.get('src'): self.assets.append(attrs['src'])
        if tag == 'link' and attrs.get('rel') in ('stylesheet', 'icon', 'apple-touch-icon'): self.assets.append(attrs['href'])
        if tag == 'a' and attrs.get('href'): self.links.append(attrs['href'])

    def handle_endtag(self, tag):
        if tag=='h1': self.in_h1=False
    def handle_data(self, value):
        if self.in_h1: self.heading_text.append(value)

def build(address, output):
    address = validate_origin(address)
    source = ROOT / 'dist'
    site = json.loads((ROOT / 'content/site.json').read_text())
    if output.resolve() == source.resolve() or output.resolve().is_relative_to(source.resolve()): raise ValueError('Output harus di luar sumber dist.')
    if output.exists() and any(output.iterdir()): raise ValueError('Direktori output harus kosong; hasil lama tidak ditimpa.')
    verification_spec=importlib.util.spec_from_file_location('google_verification',ROOT/'scripts/google-verification.py'); verification=importlib.util.module_from_spec(verification_spec); verification_spec.loader.exec_module(verification)
    google_meta=verification.load_public(ROOT/'content/google-verification.json')
    pages = site['pages']; approval_proofs={}
    if len(pages)>200: raise ValueError('Maksimum200 halaman per rilis.')
    for page in pages:
        words=page.get('target_keywords')
        if not isinstance(words,list) or len(words)>12 or any(not isinstance(w,str) or not 1<=len(w)<=100 for w in words): raise ValueError('Target keyword harus ringkas dan sesuai kontrak publik.')
    approval_spec=importlib.util.spec_from_file_location('approved_pages',ROOT/'scripts/approved-pages.py'); approvals=importlib.util.module_from_spec(approval_spec); approval_spec.loader.exec_module(approvals)
    for page in pages:
        if page.get('approval_export'):
            export_path=ROOT/page['approval_export']
            if not export_path.resolve().is_relative_to((ROOT/'content/approved').resolve()) or export_path.is_symlink(): raise ValueError('Path export tidak valid.')
            document,proof=approvals.public_snapshot(export_path,page['path'])
            if any(page[key]!=document[key] for key in ['title','description','target_keywords']) or page['h1']!=document['title']: raise ValueError('Metadata tidak sesuai snapshot yang disetujui.')
            if page.get('page_type') not in (None,document.get('page_type')): raise ValueError('Tipe halaman berbeda dari snapshot approved.')
            page['approved_document']=document;approval_proofs[page['path']]=proof
            if document.get('page_type')=='article':
                page['page_type']='article';page['jsonLd']=approvals.articles.metadata(document,site['origin'])
        elif page.get('page_type')=='article' or page['path'].startswith('/artikel/'):
            raise ValueError('Artikel memerlukan snapshot approved; draft tidak boleh dibangun.')
    article_pages=[p for p in pages if p.get('page_type')=='article']
    banner_paths=set()
    for page in article_pages:
        banner=page['approved_document'].get('banner')
        if banner:
            banner_file=source/banner['path'].lstrip('/')
            if not banner_file.resolve().is_relative_to(source.resolve()) or any(p.is_symlink() for p in [banner_file,*banner_file.parents] if p!=source and source in p.parents): raise ValueError('Path asset banner publik tidak aman.')
            approvals.articles.banners.local_bytes(banner_file,banner);banner_paths.add(banner['path'].lstrip('/'))
    if article_pages:
        derived=[approval_proofs[p['path']] for p in sorted(article_pages,key=lambda p:p['path'])]
        hub={'path':'/artikel/','page_type':'article_index','title':'Artikel dan panduan bermain','description':'Penjelasan dan langkah praktis berdasarkan sumber yang dicantumkan pada setiap artikel Gendut Store.','h1':'Artikel dan panduan bermain','target_keywords':['artikel game'],'derived_from':derived,'openGraph':pages[0]['openGraph'],'jsonLd':{'@context':'https://schema.org','@type':'CollectionPage','name':'Artikel dan panduan bermain','url':site['origin']+'/artikel/'}}
        pages.append(hub)
    paths = {p['path'] for p in pages}
    if not pages or len(paths) != len(pages) or '/' not in paths: raise ValueError('Halaman beranda dan path unik diperlukan.')
    for page in article_pages:
        if any(path not in paths for path in page['approved_document']['related_paths']): raise ValueError('Tautan halaman lokal artikel belum dibangun.')
    for path in paths:
        if path != '/' and not (path=='/artikel/' and article_pages) and not re.fullmatch(r'/(?:game|artikel)/[a-z0-9]+(?:-[a-z0-9]+)*/', path): raise ValueError('Path halaman tidak valid.')
    output.mkdir(parents=True, exist_ok=True)
    allowed = {'.html', '.css', '.js', '.png', '.webp', '.svg', '.ico', '.xml', '.txt'}
    for path in sorted(source.rglob('*')):
        if not path.is_file() or path.name in ('robots.txt', 'sitemap.xml'): continue
        relative = path.relative_to(source)
        if str(relative).startswith('assets/articles/') and str(relative) not in banner_paths:continue
        # Owner-provided Google challenges are root files, not rendered pages.
        google_file = path.suffix == '.html' and len(relative.parts) == 1 and re.fullmatch(r'google[A-Za-z0-9_-]{4,128}\.html', path.name)
        if path.suffix == '.html' and not google_file: continue
        if path.is_symlink() or path.suffix not in allowed or any(part.startswith('.') for part in relative.parts): raise ValueError('Berkas bukan aset publik ditolak.')
        if google_file and path.read_bytes() != ('google-site-verification: '+path.name).encode('utf-8'): raise ValueError('Isi file verifikasi Google harus tepat sesuai nama file.')
        target = output / relative; target.parent.mkdir(parents=True, exist_ok=True); shutil.copyfile(path, target)
    module_spec=importlib.util.spec_from_file_location('render_pages',ROOT/'scripts/render-pages.py')
    renderer=importlib.util.module_from_spec(module_spec); module_spec.loader.exec_module(renderer)
    rendered=renderer.render_pages(site)
    records=[]
    for spec in pages:
        local = spec['path'].lstrip('/') + 'index.html'
        html = rendered[local]
        title = unescape(re.search(r'<title>(.*?)</title>', html, re.S).group(1))
        description = unescape(re.search(r'<meta name="description" content="([^"]+)"', html).group(1))
        if title != spec['title'] or description != spec['description']: raise ValueError('Metadata sumber berbeda dari kontrak halaman: '+local)
        html = re.sub(r'\s*<link rel="canonical"[^>]*>', '', html)
        html = re.sub(r'\s*<meta property="og:(?:url|image(?::[a-z]+)?)"[^>]*>', '', html)
        html = re.sub(r'\s*<script type="application/ld\+json">[\s\S]*?</script>', '', html)
        graph = json.loads(json.dumps(spec['jsonLd'],ensure_ascii=False).replace(site['origin'], address))
        canonical = address + spec['path']; og = spec['openGraph']
        metadata = '\n'.join([
            '<link rel="canonical" href="'+escape(canonical,quote=True)+'">',
            '<meta property="og:url" content="'+escape(canonical,quote=True)+'">',
            '<meta property="og:image" content="'+escape(og['image'].replace(site['origin'], address),quote=True)+'">',
            '<meta property="og:image:width" content="'+str(og['image_width'])+'">',
            '<meta property="og:image:height" content="'+str(og['image_height'])+'">',
            '<meta property="og:image:alt" content="'+escape(og['image_alt'],quote=True)+'">',
            '<script type="application/ld+json">'+json.dumps(graph,ensure_ascii=False).replace('<','\\u003c')+'</script>'
        ])
        if google_meta and address+'/'==google_meta['property_id'] and spec['path']=='/':
            metadata+='\n<meta name="google-site-verification" content="'+escape(google_meta['value'],quote=True)+'">'
        html = html.replace('</head>', metadata+'\n</head>')
        if '.chatgpt.site' in html: raise ValueError('Alamat hosting privat tidak boleh berada di website publik.')
        page=Page(); page.feed(html)
        if page.headings != 1 or ''.join(page.heading_text)!=spec['h1']: raise ValueError('Satu H1 sesuai copy diperlukan: '+local)
        for asset in page.assets:
            path=source/asset.lstrip('/')
            if not path.is_file() or not path.resolve().is_relative_to(source.resolve()): raise ValueError('Aset lokal tidak valid: '+asset)
        for link in page.links:
            parsed=urlsplit(link)
            if parsed.scheme or parsed.netloc:
                if spec.get('page_type')=='article' and link in {s['url'] for s in spec['approved_document']['sources']}:
                    approvals.articles.source_url(link);continue
                if parsed.scheme!='https' or parsed.hostname!='gendutstore.com' or parsed.username or parsed.password or parsed.port or parsed.query or parsed.fragment: raise ValueError('Tautan produk pusat tidak valid: '+link)
                if parsed.path not in ['/', '/games', '/terms'] and not re.fullmatch(r'/id/[A-Za-z0-9_-]+',parsed.path): raise ValueError('Path produk tidak valid: '+link)
            elif parsed.path and parsed.path not in paths: raise ValueError('Tautan halaman lokal tidak valid: '+link)
            if parsed.fragment and (not parsed.path or parsed.path==spec['path']) and parsed.fragment not in page.ids: raise ValueError('Jangkar tidak ditemukan: '+link)
        target=output/local; target.parent.mkdir(parents=True,exist_ok=True); target.write_text(html)
        records.append({'slug':spec['path'],'path':spec['path'],'title':title,'description':description,'target_keywords':spec['target_keywords'],'canonical':canonical,'source_path':'content/site.json','content_sha256':hashlib.sha256(target.read_bytes()).hexdigest(),**approval_proofs.get(spec['path'],{}),**({'page_type':spec['page_type']} if spec.get('page_type') else {}),**({'derived_from':spec['derived_from']} if spec.get('derived_from') else {})})
    (output/'robots.txt').write_text('User-agent: *\nAllow: /\n\nSitemap: '+address+'/sitemap.xml\n')
    (output/'sitemap.xml').write_text('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'+''.join('<url><loc>'+escape(address+p['path'])+'</loc></url>' for p in pages)+'</urlset>\n')
    commit=os.environ.get('RENDER_GIT_COMMIT') or None
    if commit and not re.fullmatch('[0-9a-f]{40}',commit): raise ValueError('RENDER_GIT_COMMIT tidak valid.')
    assets=[{'path':'/'+str(p.relative_to(output)),'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'bytes':p.stat().st_size} for p in sorted((output/'assets').rglob('*')) if p.is_file()]
    manifest={'schema_version':1,'origin':address,'repository':'phantomx567/gendut-store-seo','branch':'main','source_commit':commit,'generated_at':datetime.now(timezone.utc).isoformat(),'pages':records,'assets':assets,'deployment':{'provider':'Render','commit':commit,'status':'built','url':address}}
    (output/'site-manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2))
    return {'output':str(output),'origin':address,'pages':len(records),'files':sum(p.is_file() for p in output.rglob('*')),'source_commit':commit,'published':False}

if __name__ == '__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--origin', default=os.environ.get('SITE_ORIGIN') or os.environ.get('RENDER_EXTERNAL_URL'))
    parser.add_argument('--output',type=Path,default=ROOT/'public')
    args=parser.parse_args()
    try: print(json.dumps(build(args.origin,args.output)))
    except (ValueError,OSError,KeyError) as error: parser.exit(1,str(error)+'\n')
