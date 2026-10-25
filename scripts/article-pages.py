"""Public article contract and derived metadata; no draft or private receipts."""
import importlib.util
from pathlib import Path
from datetime import datetime
from html import escape
import ipaddress
import re
from urllib.parse import urlsplit

banner_spec=importlib.util.spec_from_file_location('article_banner',Path(__file__).with_name('article-banner.py'));banners=importlib.util.module_from_spec(banner_spec);banner_spec.loader.exec_module(banners)
ARTICLE_FIELDS={'page_type','path','title','description','target_keywords','content','sources','related_paths'}
ARTICLE_PATH=r'/artikel/[a-z0-9]+(?:-[a-z0-9]+)*/'

def text(value, minimum=1, maximum=8000):
    if not isinstance(value,str) or not minimum<=len(value.strip())<=maximum or '\x00' in value:
        raise ValueError('Teks artikel tidak valid.')

def actual_date(value):
    if not isinstance(value,str): raise ValueError('Waktu sumber diperlukan.')
    try: stamp=datetime.fromisoformat(value.replace('Z','+00:00'))
    except ValueError: raise ValueError('Waktu sumber harus ISO.')
    if not stamp.tzinfo: raise ValueError('Waktu sumber harus memiliki zona waktu.')
    return stamp

def source_url(value):
    if not isinstance(value,str) or len(value)>2000 or any(c.isspace() or ord(c)<32 or ord(c)==127 for c in value): raise ValueError('URL sumber tidak valid.')
    parsed=urlsplit(value);host=parsed.hostname or ''
    if parsed.scheme!='https' or not host or '.' not in host or parsed.username or parsed.password or parsed.port or '\\' in value or host.endswith(('.local','.localhost','.internal','.chatgpt.site')):
        raise ValueError('Sumber harus HTTPS publik tanpa kredensial.')
    try: ipaddress.ip_address(host)
    except ValueError: pass
    else: raise ValueError('Alamat IP bukan sumber artikel.')
    return value

def validate_article(doc):
    if set(doc) not in (ARTICLE_FIELDS,ARTICLE_FIELDS|{'banner'}) or doc.get('page_type')!='article' or not re.fullmatch(ARTICLE_PATH,doc.get('path','')):
        raise ValueError('Whitelist/path artikel tidak valid.')
    if 'banner' in doc:banners.descriptor(doc['banner'])
    content=doc.get('content');sources=doc.get('sources');related=doc.get('related_paths')
    if not isinstance(content,dict) or set(content)!={'lead','sections'}: raise ValueError('Artikel memerlukan lead dan sections.')
    text(content['lead'],20,3000)
    sections=content['sections']
    if not isinstance(sections,list) or not 1<=len(sections)<=40: raise ValueError('Jumlah bagian artikel tidak valid.')
    if not isinstance(sources,list) or not 1<=len(sources)<=40: raise ValueError('Sumber artikel diperlukan.')
    ids=set()
    for source in sources:
        if not isinstance(source,dict) or not {'id','label','url','verified_at'}<=set(source) or set(source)-{'id','label','url','verified_at','published_at'}: raise ValueError('Metadata sumber tidak valid.')
        key=source['id']
        if not isinstance(key,str) or not re.fullmatch('[A-Za-z0-9_-]{1,80}',key) or key in ids: raise ValueError('ID sumber harus unik.')
        ids.add(key);text(source['label'],2,300);source_url(source['url']);verified=actual_date(source['verified_at'])
        if source.get('published_at') is not None and actual_date(source['published_at'])>verified: raise ValueError('Tanggal sumber melewati verifikasi.')
    used=set()
    for section in sections:
        if not isinstance(section,dict) or not {'heading','paragraphs','source_ids'}<=set(section) or set(section)-{'heading','paragraphs','source_ids','bullets'}: raise ValueError('Bagian artikel tidak valid.')
        text(section['heading'],2,200)
        paragraphs=section['paragraphs'];bullets=section.get('bullets',[]);refs=section['source_ids']
        if not isinstance(paragraphs,list) or not 1<=len(paragraphs)<=20 or not isinstance(bullets,list) or len(bullets)>30: raise ValueError('Isi bagian artikel tidak valid.')
        for paragraph in paragraphs: text(paragraph,1,8000)
        for bullet in bullets: text(bullet,1,2000)
        if not isinstance(refs,list) or not refs or any(not isinstance(ref,str) for ref in refs) or len(refs)!=len(set(refs)) or any(ref not in ids for ref in refs): raise ValueError('Kutipan bagian tidak sesuai sumber.')
        used.update(refs)
    if used!=ids: raise ValueError('Setiap sumber harus dirujuk oleh isi artikel.')
    if not isinstance(related,list) or len(related)>5 or any(not isinstance(path,str) or not re.fullmatch(r'/game/[a-z0-9]+(?:-[a-z0-9]+)*/',path) for path in related) or len(related)!=len(set(related)): raise ValueError('Related LP harus path lokal aman.')
    if len(str(content))>60000: raise ValueError('Isi artikel terlalu panjang.')
    return doc

def metadata(doc,origin):
    route=doc['path'];url=origin+route
    return {'@context':'https://schema.org','@graph':[
        {'@type':'Article','@id':url+'#article','url':url,'mainEntityOfPage':url,'headline':doc['title'],'description':doc['description'],'inLanguage':'id','citation':[s['url'] for s in doc['sources']],**({'image':{'@type':'ImageObject','url':origin+doc['banner']['path'],'width':doc['banner']['width'],'height':doc['banner']['height'],'caption':doc['banner']['alt']}} if doc.get('banner') else {})},
        {'@type':'BreadcrumbList','@id':url+'#breadcrumb','itemListElement':[{'@type':'ListItem','position':1,'name':'Beranda','item':origin+'/'},{'@type':'ListItem','position':2,'name':'Artikel','item':origin+'/artikel/'},{'@type':'ListItem','position':3,'name':doc['title'],'item':url}]}
    ]}

def render_article(doc,pages):
    e=lambda value:escape(str(value),quote=True)
    parts=['<main id="konten" class="editorial wrap"><nav class="editorial-breadcrumb" aria-label="Breadcrumb"><a href="/">Beranda</a><span aria-hidden="true">/</span><a href="/artikel/">Artikel</a></nav><article><header class="editorial-heading"><p class="eyebrow">Artikel Gendut Store</p><h1>'+e(doc['title'])+'</h1><p class="editorial-lead">'+e(doc['content']['lead'])+'</p></header><nav class="editorial-toc" aria-label="Isi artikel"><h2>Dalam artikel ini</h2><ol>']
    if doc.get('banner'):
        b=doc['banner'];figure='<figure class="editorial-banner"><img src="'+e(b['path'])+'" alt="'+e(b['alt'])+'" width="'+str(b['width'])+'" height="'+str(b['height'])+'" decoding="async" fetchpriority="high"></figure>'
        parts[0]=parts[0].replace('</header><nav', '</header>'+figure+'<nav')
    parts.extend('<li><a href="#bagian-'+str(i)+'">'+e(s['heading'])+'</a></li>' for i,s in enumerate(doc['content']['sections'],1));parts.append('</ol></nav>')
    for i,section in enumerate(doc['content']['sections'],1):
        parts.append('<section class="editorial-section" id="bagian-'+str(i)+'"><h2>'+e(section['heading'])+'</h2>')
        parts.extend('<p>'+e(p)+'</p>' for p in section['paragraphs'])
        if section.get('bullets'): parts.append('<ul>'+''.join('<li>'+e(b)+'</li>' for b in section['bullets'])+'</ul>')
        parts.append('<p class="editorial-references">Sumber: '+', '.join('<a href="#sumber-'+e(ref)+'">'+str(next(i for i,s in enumerate(doc['sources'],1) if s['id']==ref))+'</a>' for ref in section['source_ids'])+'</p></section>')
    parts.append('<section class="editorial-section editorial-sources" aria-labelledby="sumber-title"><h2 id="sumber-title">Sumber dan waktu pemeriksaan</h2><ol>')
    for source in doc['sources']:
        parts.append('<li id="sumber-'+e(source['id'])+'"><a href="'+e(source['url'])+'" rel="noopener noreferrer">'+e(source['label'])+'</a><p>Diperiksa <time datetime="'+e(source['verified_at'])+'">'+e(actual_date(source['verified_at']).strftime('%d %b %Y'))+'</time>'+(' · Terbit <time datetime="'+e(source['published_at'])+'">'+e(actual_date(source['published_at']).strftime('%d %b %Y'))+'</time>' if source.get('published_at') else '')+'</p></li>')
    parts.append('</ol></section>')
    if doc['related_paths']:
        titles={p['path']:p['title'] for p in pages}
        parts.append('<aside class="editorial-related"><h2>Panduan terkait</h2><ul>'+''.join('<li><a href="'+e(path)+'">'+e(titles[path])+'</a></li>' for path in doc['related_paths'] if path in titles)+'</ul></aside>')
    return ''.join(parts)+'</article><p><a class="editorial-back" href="/artikel/">Kembali ke semua artikel</a></p></main>'

def render_index(pages):
    e=lambda value:escape(str(value),quote=True)
    return '<main id="konten" class="editorial wrap"><p class="eyebrow">Gendut Store</p><h1>Artikel dan panduan bermain</h1><p class="editorial-lead">Baca penjelasan dan langkah praktis berdasarkan sumber yang dicantumkan pada setiap artikel.</p><div class="editorial-index">'+''.join('<article><h2><a href="'+e(p['path'])+'">'+e(p['title'])+'</a></h2><p>'+e(p['description'])+'</p></article>' for p in sorted(pages,key=lambda p:p['path']))+'</div></main>'
