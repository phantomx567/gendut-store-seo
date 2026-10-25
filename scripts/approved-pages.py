"""Validate staff-private exports; expose only exact public-content snapshots."""
import importlib.util
import hashlib
import json
from pathlib import Path
import re
ORIGIN='https://gendut-store-panduan.onrender.com'
SOURCE={'origin':ORIGIN,'repository':'phantomx567/gendut-store-seo','branch':'main'}
PUBLIC_FIELDS={'path','title','description','target_keywords','content'}
article_spec=importlib.util.spec_from_file_location('article_pages',Path(__file__).with_name('article-pages.py'));articles=importlib.util.module_from_spec(article_spec);article_spec.loader.exec_module(articles)
SNAPSHOT_FIELDS={'schema_version','page_id','revision','canonical_public_document_json','public_content_hash','source'}

def parse_snapshot(value, expected_path=None):
    raw=value.get('canonical_public_document_json')
    if not isinstance(raw,str): raise ValueError('Canonical public document diperlukan.')
    digest=hashlib.sha256(raw.encode('utf-8')).hexdigest();document=json.loads(raw)
    article=document.get('page_type')=='article'
    fields=(articles.ARTICLE_FIELDS|({'banner'} if 'banner' in document else set())) if article else PUBLIC_FIELDS
    if set(document)!=fields or value.get('schema_version')!=1 or digest!=value.get('public_content_hash'): raise ValueError('Public content/hash tidak sesuai whitelist.')
    revision=value.get('revision');page_id=value.get('page_id')
    if type(revision)!=int or revision<1 or not isinstance(page_id,str) or not re.fullmatch(r'[A-Za-z0-9_-]{1,160}',page_id): raise ValueError('Identitas snapshot tidak valid.')
    if value.get('source')!=SOURCE: raise ValueError('Sumber snapshot tidak valid.')
    route=document.get('path','')
    if not re.fullmatch(articles.ARTICLE_PATH if article else r'(?:/|/game/[a-z0-9]+(?:-[a-z0-9]+)*/)',route) or (expected_path and route!=expected_path): raise ValueError('Path snapshot tidak sesuai.')
    if article: articles.validate_article(document)
    for key,minimum,maximum in [('title',3,200),('description',10,500)]+([] if article else [('content',20,60000)]):
        text=document.get(key)
        if not isinstance(text,str) or not minimum<=len(text)<=maximum: raise ValueError('Isi publik tidak valid: '+key)
    words=document.get('target_keywords')
    if not isinstance(words,list) or len(words)>12 or any(not isinstance(k,str) or not 2<=len(k)<=100 for k in words): raise ValueError('Keyword publik tidak valid.')
    if not article and route in {'/game/mobile-legends/','/game/free-fire/'}:
        spec=importlib.util.spec_from_file_location('canonical_landing',Path(__file__).with_name('landing-pages.py'));lp=importlib.util.module_from_spec(spec);spec.loader.exec_module(lp);lp.canonical_document(raw,digest,expected_path)
    return document,{'page_id':page_id,'approval_revision':revision,'approved_snapshot_hash':digest}

def public_snapshot(path, expected_path=None):
    value=json.loads(Path(path).read_text())
    if set(value)!=SNAPSHOT_FIELDS: raise ValueError('Snapshot publik tidak boleh memuat receipt privat.')
    return parse_snapshot(value,expected_path)

def approved_export(path, expected_path=None):
    export=json.loads(Path(path).read_text());document,proof=parse_snapshot(export,expected_path)
    if {k:export.get('document',{}).get(k) for k in document}!=document: raise ValueError('Dokumen privat dan proyeksi publik berbeda.')
    for key in ['approval','qa']:
        receipt=export.get(key,{})
        if receipt.get('revision')!=proof['approval_revision'] or receipt.get('content_hash')!=proof['approved_snapshot_hash']: raise ValueError('QA/persetujuan berbeda snapshot publik.')
    if export['approval'].get('actor')!='Reza' or not export['qa'].get('agent_id'): raise ValueError('Keputusan pemilik/QA tidak tersedia.')
    sanitized={k:export[k] for k in SNAPSHOT_FIELDS}
    return document,proof,sanitized
