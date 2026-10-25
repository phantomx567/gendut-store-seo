"""Synthetic local exports only: never withdraw a real production page."""
import unittest,tempfile,shutil,json,hashlib,importlib.util,copy
from pathlib import Path
from cover_fixture import assign as assign_cover
ROOT=Path(__file__).resolve().parents[1]
def module(path,name):
 s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
class ReleaseSelection(unittest.TestCase):
 def setUp(self):
  self.temp=tempfile.TemporaryDirectory();self.root=Path(self.temp.name)
  for p in ['content','scripts','dist']:shutil.copytree(ROOT/p,self.root/p)
  self.adapter=module(self.root/'scripts/import-approved-page.py','sel_adapter');self.adapter.ROOT=self.root
  self.selection=module(self.root/'scripts/release-selection.py','selection');self.builder=module(self.root/'scripts/build-static.py','sel_build');self.builder.ROOT=self.root;self.n=0
  self.doc={'page_type':'article','path':'/artikel/selection-fixture/','title':'Synthetic isolated selection fixture','description':'A synthetic approved document used only for local withdrawal integration tests.','target_keywords':['fixture selection'],'content':{'lead':'A synthetic introduction for isolated tests.','sections':[{'heading':'One useful fixture section','paragraphs':['Exact immutable fixture prose.'],'source_ids':['ref']}]},'sources':[{'id':'ref','label':'Synthetic reference','url':'https://example.org/help','verified_at':'2026-10-25T00:00:00Z'}],'related_paths':['/game/free-fire/']}
  self.file,self.exp=self.export(1);self.adapter.import_export(self.file)
 def tearDown(self):self.temp.cleanup()
 def export(self,revision,doc=None):
  doc=copy.deepcopy(doc or self.doc);assign_cover(self.root,doc);raw=json.dumps(doc,ensure_ascii=False,separators=(',',':'));sha=hashlib.sha256(raw.encode()).hexdigest();v={'schema_version':1,'page_id':'selection-fixture','revision':revision,'canonical_public_document_json':raw,'public_content_hash':sha,'content_hash':sha,'document':doc,'source':self.selection.SOURCE,'approval':{'actor':'Reza','revision':revision,'content_hash':sha},'qa':{'agent_id':'synthetic-reviewer','revision':revision,'content_hash':sha}};f=self.root/('export'+str(revision)+'.json');f.write_text(json.dumps(v));return f,v
 def instruction(self):
  sha=self.exp['content_hash'];v={'schema_version':1,'page_id':'selection-fixture','path':self.doc['path'],'revision':1,'content_hash':sha,'state':'withdraw_requested','source':self.selection.SOURCE,'withdrawal':{'request_id':'9d9b64c5-8213-4892-88dc-cfeff979094c','revision':1,'content_hash':sha,'note':'PRIVATE_REASON_CANARY','staff':'PRIVATE_STAFF_CANARY','target':{'kind':'approved_snapshot','revision':1,'content_hash':sha,'commit':'a'*40,'url':self.selection.SOURCE['origin']+self.doc['path'],'sha256':'b'*64,'checked_at':'2026-10-25T00:00:00Z','provenance':'approved_snapshot_and_current_public_manifest'}}};return v
 def withdraw(self,v=None):
  f=self.root/'private-withdrawal.json';f.write_text(json.dumps(v or self.instruction()));return self.selection.withdraw(self.root,f)
 def build(self):
  self.n+=1;out=self.root/('out'+str(self.n));self.builder.build(self.selection.SOURCE['origin'],out);return out
 def test_target_pair_privacy_replay_clean_build_and_snapshot_immutable(self):
  self.assertIn('href="'+self.doc['path']+'"',(self.build()/'game/free-fire/index.html').read_text())
  snapshot=self.root/'content/approved/selection-fixture-r1.json';before=snapshot.read_bytes();self.withdraw();selection=(self.root/'content/release-selection.json').read_bytes();self.withdraw();self.assertEqual((self.root/'content/release-selection.json').read_bytes(),selection)
  self.assertNotIn(b'PRIVATE',selection);self.assertNotIn(b'request_id',selection);self.assertEqual(snapshot.read_bytes(),before);out=self.build();self.assertFalse((out/'artikel/selection-fixture/index.html').exists());self.assertNotIn(self.doc['path'],(out/'sitemap.xml').read_text());self.assertNotIn(self.doc['title'],(out/'artikel/index.html').read_text())
  self.assertTrue((out/'artikel/cara-membaca-user-id-server-id-mobile-legends/index.html').exists());self.assertTrue((out/'artikel/cara-menemukan-player-id-free-fire/index.html').exists())
  self.assertNotIn('href="'+self.doc['path']+'"',(out/'game/free-fire/index.html').read_text())
 def test_identical_old_approval_cannot_republish_newer_approval_can(self):
  self.withdraw()
  with self.assertRaisesRegex(ValueError,'lebih baru'):self.adapter.import_export(self.file)
  f,e=self.export(2);self.adapter.import_export(f);self.assertEqual(self.selection.load(self.root),[]);self.assertTrue((self.build()/'artikel/selection-fixture/index.html').exists());self.assertTrue((self.root/'content/approved/selection-fixture-r1.json').exists())
 def test_stale_target_unknown_binding_and_homepage_refused(self):
  for mutate in [lambda v:v['withdrawal']['target'].update(content_hash='f'*64),lambda v:v.update(page_id='unknown'),lambda v:v.update(path='/'),lambda v:v['source'].update(repository='unknown/repo')]:
   v=copy.deepcopy(self.instruction());mutate(v)
   with self.assertRaises(ValueError):self.withdraw(v)
  self.assertFalse((self.root/'content/release-selection.json').exists())
 def test_old_withdrawal_cannot_remove_newer_current_snapshot(self):
  f,e=self.export(2);self.adapter.import_export(f)
  with self.assertRaisesRegex(ValueError,'Snapshot aktif'):self.withdraw()
 def test_selection_unknown_fields_rejected(self):
  self.withdraw();p=self.root/'content/release-selection.json';v=json.loads(p.read_text());v['withdrawn'][0]['note']='PRIVATE';p.write_text(json.dumps(v))
  with self.assertRaises(ValueError):self.build()
 def test_suppressed_derived_href_preserves_readable_prose(self):
  text='<p>Keep this exact prose <a href="/artikel/selection-fixture/?x=1#part">read the same label</a>.</p>';result=self.selection.suppress_links(text,{self.doc['path']},self.selection.SOURCE['origin']);self.assertNotIn('href=',result);self.assertIn('Keep this exact prose',result);self.assertIn('read the same label',result)
 def test_shared_explicit_scene_survives_one_withdrawal_then_orphan_is_not_served(self):
  collection=json.loads((self.root/'content/editorial-covers.json').read_text());sha=collection['articles'][self.doc['path']]['cover_sha256'];scene=collection['covers'][sha]['path'];snapshot=self.root/'content/approved/selection-fixture-r1.json';before=snapshot.read_bytes()
  second={**self.doc,'path':'/artikel/shared-cover/'};file,value=self.export(2,second);value['page_id']='shared-fixture';file.write_text(json.dumps(value));self.adapter.import_export(file)
  self.withdraw();out=self.build();self.assertTrue((out/scene.lstrip('/')).exists());self.assertEqual(snapshot.read_bytes(),before)
  decision=self.instruction();decision.update(page_id='shared-fixture',path=second['path'],revision=2,content_hash=value['content_hash']);decision['withdrawal'].update(request_id='34b5d009-dd11-4ccc-9ee5-ea7f186b1ab8',revision=2,content_hash=value['content_hash']);decision['withdrawal']['target'].update(revision=2,content_hash=value['content_hash'],url=self.selection.SOURCE['origin']+second['path']);self.withdraw(decision)
  out=self.build();self.assertFalse((out/scene.lstrip('/')).exists());self.assertFalse((out/'artikel/shared-cover/index.html').exists());bindings=json.loads((out/'editorial-cover-manifest.json').read_text())['covers'];self.assertNotIn(second['path'],[b['article_path'] for b in bindings]);self.assertEqual(snapshot.read_bytes(),before)

 def test_legacy_external_html_uses_current_manifest_and_actual_render_without_approval(self):
  out=self.build();path='/game/free-fire/';body=(out/path.lstrip('/')/'index.html').read_bytes();sha=hashlib.sha256(body).hexdigest();manifest=json.loads((out/'site-manifest.json').read_text());manifest['source_commit']='a'*40;mf=self.root/'observed-manifest.json';mf.write_text(json.dumps(manifest));v=self.instruction();v['path']=path;v['page_id']='legacy-fixture';v['withdrawal']['target'].update(kind='external_html',url=self.selection.SOURCE['origin']+path,sha256=sha,provenance='current_public_manifest_without_invented_approval');f=self.root/'private-legacy.json';f.write_text(json.dumps(v))
  for bad in ['sha','commit','path']:
   broken=copy.deepcopy(v);broken['withdrawal']['target'][{'sha':'sha256','commit':'commit','path':'url'}[bad]]={'sha':'f'*64,'commit':'f'*40,'path':self.selection.SOURCE['origin']+'/game/unknown/'}[bad];f.write_text(json.dumps(broken))
   with self.assertRaises(ValueError):self.selection.withdraw(self.root,f,mf,out)
  current=json.loads((self.root/'content/site.json').read_text());changed=copy.deepcopy(current);next(p for p in changed['pages'] if p['path']==path)['copy']['intro']='A changed current source introduction, not the observed public version.';(self.root/'content/site.json').write_text(json.dumps(changed));f.write_text(json.dumps(v))
  with self.assertRaisesRegex(ValueError,'source aktif'):self.selection.withdraw(self.root,f,mf,out)
  (self.root/'content/site.json').write_text(json.dumps(current))
  f.write_text(json.dumps(v));row=self.selection.withdraw(self.root,f,mf,out);self.assertEqual(set(row),{'path','page_id','observed_html_sha256','revoked_through_revision'});self.assertNotIn('approval',json.dumps(row));self.assertFalse((self.build()/'game/free-fire/index.html').exists())

 def test_revokes_public_r1_and_already_approved_r2_until_fresh_r3(self):
  public=self.build();manifest=json.loads((public/'site-manifest.json').read_text());manifest['source_commit']='a'*40;entry=next(p for p in manifest['pages'] if p['path']==self.doc['path']);mf=self.root/'public-target.json';mf.write_text(json.dumps(manifest))
  private_doc=copy.deepcopy(self.doc);private_doc['content']['lead']='A private approved queued revision B which must not silently reappear.';f2,e2=self.export(2,private_doc);self.adapter.import_export(f2);decision=self.instruction();decision['revision']=2;decision['content_hash']=e2['content_hash'];decision['withdrawal'].update(revision=2,content_hash=e2['content_hash']);decision['withdrawal']['target']['sha256']=entry['content_sha256'];wf=self.root/'private-owner.json';wf.write_text(json.dumps(decision));self.selection.withdraw(self.root,wf,mf)
  stored=(self.root/'content/release-selection.json').read_text();self.assertNotIn(e2['content_hash'],stored);self.assertNotIn('PRIVATE',stored);self.assertEqual(json.loads(stored)['withdrawn'][0]['revoked_through_revision'],2);self.assertFalse((self.build()/'artikel/selection-fixture/index.html').exists())
  for f in [self.file,f2]:
   with self.assertRaisesRegex(ValueError,'lebih baru'):self.adapter.import_export(f)
  f3,e3=self.export(3,private_doc);self.adapter.import_export(f3);self.assertEqual(self.selection.load(self.root),[]);self.assertTrue((self.build()/'artikel/selection-fixture/index.html').exists())

 def test_never_live_queue_requires_exact_previous_approval(self):
  v=self.instruction();v['withdrawal']['target']=None
  with self.assertRaisesRegex(ValueError,'persetujuan sebelumnya'):self.withdraw(v)
  v['withdrawal'].update(previous_state='queued_publish',previous_approval={'actor':'Reza','revision':1,'content_hash':self.exp['content_hash']});self.withdraw(v);self.assertFalse((self.build()/'artikel/selection-fixture/index.html').exists())
