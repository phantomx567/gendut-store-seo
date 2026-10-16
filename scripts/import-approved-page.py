#!/usr/bin/env python3
"""Import a real panel export file after authenticated staff export, not a claimed hash.

Example: python3 scripts/import-approved-page.py --export /private/work/export.json
This does not approve, fetch accounts, commit, push, or publish anything.
"""
import argparse
import importlib.util
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('approved_pages',ROOT/'scripts/approved-pages.py');module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)

def import_export(file,banner_file=None):
    doc,proof,snapshot=module.approved_export(file);origin=module.ORIGIN;route=doc['path']
    banner=doc.get('banner');banner_data=None
    if banner:
        if banner_file is None:raise ValueError('Banner approved memerlukan --banner-file lokal asli.')
        banner_data=module.articles.banners.local_bytes(banner_file,banner)
        banner_destination=ROOT/'dist'/banner['path'].lstrip('/')
        if not banner_destination.resolve().is_relative_to((ROOT/'dist').resolve()) or banner_destination.is_symlink():raise ValueError('Tujuan banner publik tidak aman.')
        if banner_destination.exists() and banner_destination.read_bytes()!=banner_data:raise ValueError('Asset banner immutable berbeda.')
    elif banner_file is not None:raise ValueError('Snapshot tidak memiliki banner approved.')
    destination=ROOT/'content/approved'/f"{proof['page_id']}-r{proof['approval_revision']}.json"
    encoded=json.dumps(snapshot,ensure_ascii=False,indent=2,sort_keys=True)
    if destination.exists() and destination.read_text()!=encoded: raise ValueError('Snapshot revisi yang tersimpan tidak boleh ditimpa.')
    site=json.loads((ROOT/'content/site.json').read_text());destination.parent.mkdir(parents=True,exist_ok=True)
    if banner_data is not None:
        banner_destination.parent.mkdir(parents=True,exist_ok=True)
        if not banner_destination.exists():banner_destination.write_bytes(banner_data)
    if not destination.exists(): destination.write_text(encoded)
    entry={'path':route,'title':doc['title'],'description':doc['description'],'h1':doc['title'],'target_keywords':doc['target_keywords'],'approval_export':str(destination.relative_to(ROOT)),
      'twitterCard':'summary','openGraph':{'image':origin+'/assets/gendut-store-social.png','image_width':1080,'image_height':1080,'image_alt':'Logo Gendut Store'},
      'jsonLd':{'@context':'https://schema.org','@graph':[{'@type':'WebPage','@id':origin+route+'#webpage','url':origin+route,'name':doc['title'],'description':doc['description'],'inLanguage':'id'}]}}
    if doc.get('page_type')=='article':
        entry['page_type']='article';entry['jsonLd']=module.articles.metadata(doc,origin)
    site['pages']=[entry if p['path']==route else p for p in site['pages']]
    if not any(p['path']==route for p in site['pages']):site['pages'].append(entry)
    (ROOT/'content/site.json').write_text(json.dumps(site,ensure_ascii=False,indent=2));return proof
if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--export',dest='file',type=Path,required=True);parser.add_argument('--banner-file',type=Path);args=parser.parse_args()
    print(json.dumps(import_export(args.file,args.banner_file)))
