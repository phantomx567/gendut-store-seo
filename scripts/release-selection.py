"""Minimal public withdrawal selection. Private owner receipts never persist here."""
import json,re,uuid,importlib.util
from pathlib import Path
from html import unescape
from urllib.parse import urlsplit
SOURCE={'origin':'https://gendut-store-panduan.onrender.com','repository':'phantomx567/gendut-store-seo','branch':'main'}
FIELDS={'path','page_id','approval_revision','approved_snapshot_hash'}
EXTERNAL_FIELDS={'path','page_id','observed_html_sha256'}
def valid(row):
 if not isinstance(row,dict) or set(row) not in (FIELDS,EXTERNAL_FIELDS,FIELDS|{'revoked_through_revision'},EXTERNAL_FIELDS|{'revoked_through_revision'}) or not re.fullmatch(r'/(?:game|artikel)/[a-z0-9]+(?:-[a-z0-9]+)*/',str(row.get('path',''))):raise ValueError('Seleksi path tidak valid; beranda tidak boleh ditarik.')
 if not re.fullmatch(r'[A-Za-z0-9_-]{1,160}',str(row.get('page_id',''))) or ('approval_revision' in row and (type(row['approval_revision'])!=int or row['approval_revision']<1 or not re.fullmatch('[a-f0-9]{64}',str(row['approved_snapshot_hash'])))) or ('observed_html_sha256' in row and (not row['path'].startswith('/game/') or not re.fullmatch('[a-f0-9]{64}',str(row['observed_html_sha256'])))):raise ValueError('Identitas seleksi tidak valid.')
 if 'revoked_through_revision' in row and (type(row['revoked_through_revision'])!=int or row['revoked_through_revision']<row.get('approval_revision',1)):raise ValueError('Batas revokasi tidak valid.')
 return row
def load(root):
 p=Path(root)/'content/release-selection.json'
 if not p.exists():return []
 if p.is_symlink():raise ValueError('Path seleksi tidak aman.')
 data=json.loads(p.read_text())
 if set(data)!={'schema_version','withdrawn'} or data['schema_version']!=1 or not isinstance(data['withdrawn'],list) or len(data['withdrawn'])>200:raise ValueError('Kontrak seleksi tidak valid.')
 rows=[valid(x) for x in data['withdrawn']]
 if any('revoked_through_revision' not in x for x in rows):raise ValueError('Batas revokasi diperlukan.')
 if len({x['path'] for x in rows})!=len(rows) or len({x['page_id'] for x in rows})!=len(rows):raise ValueError('Seleksi berulang.')
 return rows
def save(root,rows):
 p=Path(root)/'content/release-selection.json';p.parent.mkdir(exist_ok=True)
 if p.is_symlink():raise ValueError('Path seleksi tidak aman.')
 if not rows:
  if p.exists():p.unlink()
 else:p.write_text(json.dumps({'schema_version':1,'withdrawn':sorted(rows,key=lambda x:x['path'])},ensure_ascii=False,sort_keys=True,indent=2))
def active(root,path):
 site=json.loads((Path(root)/'content/site.json').read_text());entries=[p for p in site['pages'] if p['path']==path]
 if len(entries)!=1 or not entries[0].get('approval_export'):raise ValueError('Binding approved aktif tidak tersedia; jangan menebak legacy.')
 file=Path(root)/entries[0]['approval_export']
 if file.is_symlink() or not file.resolve().is_relative_to((Path(root)/'content/approved').resolve()):raise ValueError('Path snapshot tidak aman.')
 spec=importlib.util.spec_from_file_location('selection_approved',Path(root)/'scripts/approved-pages.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
 doc,proof=m.public_snapshot(file,path);return valid({'path':path,**proof})
def withdraw(root,file,manifest_file=None,render_directory=None):
 data=json.loads(Path(file).read_text());w=data.get('withdrawal',{})
 if data.get('schema_version')!=1 or data.get('source')!=SOURCE or data.get('state') not in ['withdraw_requested','withdrawal_built','withdrawn']:raise ValueError('Instruksi penarikan owner tidak tersedia.')
 try:uuid.UUID(w['request_id'])
 except (KeyError,ValueError,TypeError):raise ValueError('ID keputusan privat tidak valid.')
 if w.get('revision')!=data.get('revision') or w.get('content_hash')!=data.get('content_hash'):raise ValueError('Keputusan current snapshot tidak cocok.')
 decision=valid({'path':data.get('path'),'page_id':data.get('page_id'),'approval_revision':data.get('revision'),'approved_snapshot_hash':data.get('content_hash')})
 target=w.get('target')
 external=False
 if target is None:
  previous=w.get('previous_approval') or {}
  if w.get('previous_state') not in ['approved','queued_publish','built'] or previous.get('actor')!='Reza' or previous.get('revision')!=data['revision'] or previous.get('content_hash')!=data['content_hash']:raise ValueError('Pembatalan antrean memerlukan persetujuan sebelumnya yang tepat.')
 if target is not None:
  expected={'kind','revision','content_hash','commit','url','sha256','checked_at','provenance'}
  if not isinstance(target,dict) or set(target)!=expected or target['kind'] not in ['approved_snapshot','external_html'] or not re.fullmatch('[a-f0-9]{40}',str(target['commit'])) or not re.fullmatch('[a-f0-9]{64}',str(target['sha256'])) or target['url']!=SOURCE['origin']+data['path']:raise ValueError('Target publik typed tidak valid.')
  from datetime import datetime
  try:datetime.fromisoformat(target['checked_at'].replace('Z','+00:00'))
  except (ValueError,TypeError,AttributeError):raise ValueError('Waktu bukti publik tidak valid.')
  pair=valid({**decision,'approval_revision':target['revision'],'approved_snapshot_hash':target['content_hash']})
  external=target['kind']=='external_html'
  if external:
   if not data['path'].startswith('/game/') or target['provenance']!='current_public_manifest_without_invented_approval' or not manifest_file or not render_directory:raise ValueError('Legacy memerlukan manifest dan hasil render aktual.')
   manifest=json.loads(Path(manifest_file).read_text());entry=next((p for p in manifest.get('pages',[]) if p.get('path')==data['path']),None)
   if manifest.get('origin')!=SOURCE['origin'] or manifest.get('repository')!=SOURCE['repository'] or manifest.get('branch')!='main' or manifest.get('source_commit')!=target['commit'] or not entry or entry.get('content_sha256')!=target['sha256'] or any(entry.get(k) is not None for k in ['page_id','approval_revision','approved_snapshot_hash']):raise ValueError('Manifest legacy tidak cocok dengan target publik.')
   local=Path(render_directory)/data['path'].lstrip('/')/'index.html'
   if local.is_symlink() or not local.resolve().is_relative_to(Path(render_directory).resolve()) or __import__('hashlib').sha256(local.read_bytes()).hexdigest()!=target['sha256']:raise ValueError('HTML source legacy berbeda dari bukti publik.')
   # Do not trust a stale caller render directory when current source changed.
   import tempfile,hashlib
   spec=importlib.util.spec_from_file_location('selection_current_builder',Path(root)/'scripts/build-static.py');builder=importlib.util.module_from_spec(spec);spec.loader.exec_module(builder);builder.ROOT=Path(root)
   if not any(x.get('path')==data['path'] for x in load(root)):
    with tempfile.TemporaryDirectory() as temp:
     output=Path(temp)/'current';builder.build(SOURCE['origin'],output)
     if hashlib.sha256((output/data['path'].lstrip('/')/'index.html').read_bytes()).hexdigest()!=target['sha256']:raise ValueError('HTML source aktif legacy sudah berubah.')
   entries=[p for p in json.loads((Path(root)/'content/site.json').read_text())['pages'] if p['path']==data['path']]
   if len(entries)!=1 or entries[0].get('approval_export'):raise ValueError('Binding legacy berubah atau sudah approved.')
   decision=valid({'path':data['path'],'page_id':data['page_id'],'observed_html_sha256':target['sha256']})
  else:
   if target['provenance']!='approved_snapshot_and_current_public_manifest':raise ValueError('Provenance approved tidak valid.')
   decision=pair
 if not external:
  current=active(root,decision['path']);current_decision={'path':data['path'],'page_id':data['page_id'],'approval_revision':data['revision'],'approved_snapshot_hash':data['content_hash']}
  if current not in [decision,current_decision]:raise ValueError('Snapshot aktif berbeda, lebih baru, atau target tidak dikenal.')
  if current!=decision:
   if not manifest_file:raise ValueError('Manifest target publik diperlukan untuk membatalkan revisi antre yang belum tayang.')
   m=json.loads(Path(manifest_file).read_text());entry=next((p for p in m.get('pages',[]) if p.get('path')==data['path']),None)
   if m.get('origin')!=SOURCE['origin'] or m.get('repository')!=SOURCE['repository'] or m.get('branch')!='main' or m.get('source_commit')!=target['commit'] or not entry or entry.get('page_id')!=decision['page_id'] or entry.get('approval_revision')!=decision['approval_revision'] or entry.get('approved_snapshot_hash')!=decision['approved_snapshot_hash'] or entry.get('content_sha256')!=target['sha256']:raise ValueError('Manifest target publik tidak cocok.')
 decision={**decision,'revoked_through_revision':max(data['revision'],target['revision'] if target else data['revision'])}
 rows=load(root);prior=next((x for x in rows if x['path']==decision['path'] or x['page_id']==decision['page_id']),None)
 if prior and prior!=decision:raise ValueError('Seleksi sebelumnya berbeda.')
 if not prior:save(root,rows+[decision])
 return decision
def after_approved_import(root,path,proof):
 rows=load(root);old=next((x for x in rows if x['path']==path or x['page_id']==proof['page_id']),None)
 if not old:return rows
 if old['path']!=path or old['page_id']!=proof['page_id'] or proof['approval_revision']<=old['revoked_through_revision']:raise ValueError('Snapshot ditarik tidak dapat diaktifkan ulang; perlu revisi approved yang lebih baru.')
 return [x for x in rows if x!=old]
def selected(pages,proofs,rows):
 bypath={p['path']:p for p in pages}
 for row in rows:
  if row['path'] not in bypath:raise ValueError('Seleksi tidak cocok dengan snapshot aktif.')
  proof=proofs.get(row['path'])
  if 'approval_revision' in row:
   if not proof or proof['page_id']!=row['page_id'] or not row['approval_revision']<=proof['approval_revision']<=row['revoked_through_revision'] or (proof['approval_revision']==row['approval_revision'] and proof['approved_snapshot_hash']!=row['approved_snapshot_hash']):raise ValueError('Seleksi tidak cocok dengan snapshot aktif.')
  elif bypath[row['path']].get('approval_export'):raise ValueError('Seleksi legacy tidak cocok dengan approved baru.')
 return [p for p in pages if p['path'] not in {r['path'] for r in rows}]
def suppress_links(html,paths,origin):
 if not paths:return html
 def replace(m):
  href=re.search(r'\bhref\s*=\s*[\"\x27]([^\"\x27]*)[\"\x27]',m[1],re.I)
  if not href:return m[0]
  u=urlsplit(unescape(href[1]));local=(not u.scheme and not u.netloc) or u.scheme+'://'+u.netloc in [origin,SOURCE['origin']]
  return '<span>'+m[2]+'</span>' if local and u.path in paths else m[0]
 return re.sub(r'<a\b([^>]*)>(.*?)</a\s*>',replace,html,flags=re.I|re.S)
