#!/usr/bin/env python3
"""Offline UNAPPROVED canonical LP preview. Never creates approval or imports a snapshot."""
import argparse,copy,hashlib,importlib.util,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def load(name,file):
 s=importlib.util.spec_from_file_location(name,ROOT/'scripts'/file);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
landing=load('landing_draft','landing-pages.py');renderer=load('landing_render','render-pages.py')
def preview(canonical_file,digest,output):
 raw=Path(canonical_file).read_bytes().decode('utf-8');doc=landing.canonical_document(raw,digest)
 output=Path(output).resolve()
 if output.is_relative_to(ROOT):raise ValueError('Preview output must be outside production repository.')
 data=json.loads((ROOT/'content/site.json').read_text());approvals=load('preview_approvals','approved-pages.py');proofs={}
 for page in data['pages']:
  if page.get('approval_export'):
   document,proof=approvals.public_snapshot(ROOT/page['approval_export'],page['path']);page['approved_document']=document;proofs[page['path']]=proof
 selection=load('preview_selection','release-selection.py');withdrawn=selection.load(ROOT);data['pages']=selection.selected(data['pages'],proofs,withdrawn);data['withdrawn_paths']=[p['path'] for p in withdrawn]
 covers=load('preview_covers','editorial-covers.py');collection=covers.load(ROOT)
 for page in data['pages']:
  if page.get('page_type')=='article':page['editorial_cover']=covers.select(ROOT,page['approved_document'],collection)
 frame=next(p for p in data['pages'] if p['path']==doc['path']);frame.update(approved_document=doc,title=doc['title'],description=doc['description'],h1=doc['title'],target_keywords=doc['target_keywords'])
 frame['jsonLd']={'@context':'https://schema.org','@type':'WebPage','name':doc['title'],'description':doc['description'],'url':data['origin']+doc['path']}
 # Same production renderer. No approval_export, receipt, registry write or production output.
 result=renderer.render_pages(data)[doc['path'].lstrip('/')+'index.html'];output.parent.mkdir(parents=True,exist_ok=True);output.write_text(result)
 receipt={'status':'LOCAL_UNAPPROVED_PREVIEW','canonical_sha256':digest,'html_sha256':hashlib.sha256(result.encode()).hexdigest(),'path':doc['path'],'output':str(output),'approval':None}
 output.with_suffix('.preview.json').write_text(json.dumps(receipt,indent=2));return receipt
if __name__=='__main__':
 a=argparse.ArgumentParser(description=__doc__);a.add_argument('--canonical',type=Path,required=True);a.add_argument('--sha256',required=True);a.add_argument('--output',type=Path,required=True);x=a.parse_args();print(json.dumps(preview(x.canonical,x.sha256,x.output)))
