"""Exercise the real renderer/build without network or production writes."""
import copy
import hashlib
import importlib.util
import json
import os
import subprocess
import sys
from pathlib import Path
import shutil
import tempfile
import unittest
from unittest.mock import patch
import xml.etree.ElementTree as ET

REPO=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('build_static',REPO/'scripts/build-static.py')
build_module=importlib.util.module_from_spec(spec);spec.loader.exec_module(build_module)

class StaticBuild(unittest.TestCase):
 def setUp(self):
  self.temp=tempfile.TemporaryDirectory();self.root=Path(self.temp.name)
  for name in ['content','scripts','dist']:shutil.copytree(REPO/name,self.root/name)
  self.original_root=build_module.ROOT;build_module.ROOT=self.root
  self.site=json.loads((self.root/'content/site.json').read_text());self.counter=0
 def tearDown(self):build_module.ROOT=self.original_root;self.temp.cleanup()
 def run_build(self,commit=None):
  (self.root/'content/site.json').write_text(json.dumps(self.site,ensure_ascii=False))
  self.counter+=1;out=self.root/('build-'+str(self.counter))
  with patch.dict('os.environ',{'RENDER_GIT_COMMIT':commit or ''}):build_module.build('https://preview.example.org',out)
  return out,json.loads((out/'site-manifest.json').read_text())
 def test_eight_pages_have_exact_hashes_seo_faq_assets_and_sitemap(self):
  out,manifest=self.run_build();self.assertEqual(len(manifest['pages']),8);self.assertIsNone(manifest['source_commit']);self.assertEqual(manifest['deployment']['status'],'built')
  self.assertEqual(len(ET.parse(out/'sitemap.xml').getroot()),8)
  titles=set();descriptions=set()
  for record in manifest['pages']:
   html=(out/(record['path'].lstrip('/')+'index.html')).read_text();titles.add(record['title']);descriptions.add(record['description'])
   self.assertEqual(hashlib.sha256(html.encode()).hexdigest(),record['content_sha256']);self.assertEqual(html.count('rel="canonical"'),1);self.assertEqual(html.count('application/ld+json'),1)
   self.assertEqual(html.count('<details>'),5 if record['path']=='/' else 3)
   self.assertTrue(all(len(k)<=100 for k in record['target_keywords']));self.assertNotIn('/workspace/',html)
   parser=build_module.Page();parser.feed(html)
   for asset in parser.assets:self.assertTrue((out/asset.lstrip('/')).is_file())
  self.assertEqual(len(titles),8);self.assertEqual(len(descriptions),8)
  for asset in manifest['assets']:
   self.assertEqual(hashlib.sha256((out/asset['path'].lstrip('/')).read_bytes()).hexdigest(),asset['sha256'])
  self.assertFalse((out/'game/not-a-page/index.html').exists(),'No invented route or homepage fallback')
 def test_ninth_page_compiles_from_document_without_prewritten_html(self):
  page=copy.deepcopy(self.site['pages'][1]);old=page['path'];page['path']='/game/build-fixture/';page['title']='Isolated new page';page['description']='Unique isolated fixture description';page['h1']='New useful isolated heading';page['copy']['h1']=page['h1'];page['copy']['game']='Fixture game';page['copy']['intro']='Actual content added to this isolated document.';page['jsonLd']=json.loads(json.dumps(page['jsonLd']).replace(old,page['path']));self.site['pages'].append(page)
  out,manifest=self.run_build();self.assertEqual(len(manifest['pages']),9);self.assertEqual(len(ET.parse(out/'sitemap.xml').getroot()),9)
  html=(out/'game/build-fixture/index.html').read_text();self.assertIn(page['copy']['intro'],html);self.assertIn(page['h1'],html)
 def test_duplicate_and_traversal_paths_are_refused(self):
  self.site['pages'].append(copy.deepcopy(self.site['pages'][1]))
  with self.assertRaises(ValueError):self.run_build()
  self.site['pages'].pop();self.site['pages'][1]['path']='/game/../escape/'
  with self.assertRaises(ValueError):self.run_build()
 def test_copy_is_escaped_and_mismatching_h1_is_refused(self):
  self.site['pages'][1]['copy']['intro']='<script>alert("fixture")</script>'
  out,_=self.run_build();html=(out/'game/mobile-legends/index.html').read_text();self.assertIn('&lt;script&gt;',html);self.assertNotIn('<script>alert',html)
  self.site['pages'][1]['copy']['h1']='Wrong draft heading'
  with self.assertRaises(ValueError):self.run_build()
 def test_product_url_and_asset_escape_are_refused(self):
  self.site['pages'][1]['copy']['cta']['url']='javascript:alert(1)'
  with self.assertRaises(ValueError):self.run_build()
  self.site['pages'][1]['copy']['cta']['url']='https://gendutstore.com/id/MLBB';self.site['pages'][1]['image']['path']='/../../etc/passwd'
  with self.assertRaises(ValueError):self.run_build()
 def test_render_commit_is_exact_and_malformed_values_fail(self):
  _,manifest=self.run_build('a'*40);self.assertEqual(manifest['source_commit'],'a'*40);self.assertEqual(manifest['deployment']['commit'],'a'*40)
  with self.assertRaises(ValueError):self.run_build('not-a-git-commit')

 def test_hero_body_and_ctas_are_rendered_from_customer_data(self):
  home=self.site['pages'][0];home['hero']['lede']='A distinct isolated hero introduction with safe customer-facing text.';home['hero']['primary_cta']['label']='Open fixture catalog'
  out,_=self.run_build();html=(out/'index.html').read_text();self.assertIn(home['hero']['lede'],html);self.assertIn(home['hero']['primary_cta']['label'],html);self.assertNotIn('Pilih game, cek data akun, lalu lanjutkan di gendutstore.com.',html)
  home['hero']['primary_cta']['href']='https://attacker.example/checkout'
  with self.assertRaises(ValueError):self.run_build()

 def fixture_export(self):
  doc={'path':'/game/approved-fixture/','title':'Approved isolated fixture','description':'A useful isolated fixture description for the approval adapter.','target_keywords':['fixture game'],'content':'<script>not executable</script>\n\nDistinct factual paragraphs from an isolated approved document.','pic_agent_id':'isolated-writer','workflow_task_id':None}
  public={k:v for k,v in doc.items() if k not in ['pic_agent_id','workflow_task_id']};raw=json.dumps(public,ensure_ascii=False,separators=(',',':'));digest=hashlib.sha256(raw.encode()).hexdigest()
  export={'schema_version':1,'page_id':'isolated-page','revision':3,'content_hash':digest,'canonical_public_document_json':raw,'public_content_hash':digest,'document':doc,'approval':{'actor':'Reza','revision':3,'content_hash':digest},'qa':{'agent_id':'isolated-reviewer','revision':3,'content_hash':digest},'source':{'origin':'https://gendut-store-panduan.onrender.com','repository':'phantomx567/gendut-store-seo','branch':'main'}}
  file=self.root/'staff-export.json';file.write_text(json.dumps(export,ensure_ascii=False));return file,export
 def test_approved_export_compiles_exact_document_and_emits_snapshot_binding(self):
  spec=importlib.util.spec_from_file_location('import_approved',self.root/'scripts/import-approved-page.py');adapter=importlib.util.module_from_spec(spec);spec.loader.exec_module(adapter);adapter.ROOT=self.root
  file,export=self.fixture_export();adapter.import_export(file);self.site=json.loads((self.root/'content/site.json').read_text());out,manifest=self.run_build()
  record=next(p for p in manifest['pages'] if p['path']==export['document']['path']);self.assertEqual(record['approved_snapshot_hash'],export['content_hash']);self.assertEqual(record['approval_revision'],3);self.assertEqual(record['page_id'],'isolated-page')
  html=(out/'game/approved-fixture/index.html').read_text();self.assertIn('Distinct factual paragraphs',html);self.assertIn('&lt;script&gt;',html);self.assertNotIn('<script>not executable',html)
  self.assertTrue(all('approved_snapshot_hash' not in p for p in manifest['pages'] if p['path']!=record['path']),'Initial external release does not invent panel approvals')
 def test_export_hash_revision_and_immutable_receipt_cannot_be_overwritten(self):
  spec=importlib.util.spec_from_file_location('import_approved',self.root/'scripts/import-approved-page.py');adapter=importlib.util.module_from_spec(spec);spec.loader.exec_module(adapter);adapter.ROOT=self.root
  file,export=self.fixture_export();adapter.import_export(file)
  export['qa']['revision']=2;file.write_text(json.dumps(export))
  with self.assertRaises(ValueError):adapter.import_export(file)
  file,export=self.fixture_export();export['canonical_public_document_json']+=' ';file.write_text(json.dumps(export))
  with self.assertRaises(ValueError):adapter.import_export(file)
  file,export=self.fixture_export();export['exported_at']='new timestamp';file.write_text(json.dumps(export));adapter.import_export(file)
  saved=next((self.root/'content/approved').glob('*.json')).read_text();self.assertNotIn('pic_agent_id',saved);self.assertNotIn('workflow_task_id',saved);self.assertNotIn('isolated-reviewer',saved);self.assertNotIn('approval',json.loads(saved))
  export['document']['content']+=' A conflicting revision body.';public={k:v for k,v in export['document'].items() if k not in ['pic_agent_id','workflow_task_id']};export['canonical_public_document_json']=json.dumps(public,ensure_ascii=False,separators=(',',':'));digest=hashlib.sha256(export['canonical_public_document_json'].encode()).hexdigest();export['public_content_hash']=digest
  for key in ['qa','approval']:export[key]['content_hash']=digest
  file.write_text(json.dumps(export))
  with self.assertRaises(ValueError):adapter.import_export(file)

 def test_snapshot_retry_is_deterministic_across_process_hash_seeds(self):
  file,export=self.fixture_export()
  for seed in ['1','2']:
   result=subprocess.run([sys.executable,str(self.root/'scripts/import-approved-page.py'),'--export',str(file)],env={**os.environ,'PYTHONHASHSEED':seed},capture_output=True,text=True)
   self.assertEqual(result.returncode,0,result.stderr)
   snapshot=next((self.root/'content/approved').glob('*.json')).read_bytes()
   if seed=='1':first=snapshot
   else:self.assertEqual(snapshot,first)
  saved=json.loads(snapshot)
  self.assertEqual(saved['canonical_public_document_json'],export['canonical_public_document_json'])
  self.assertEqual(hashlib.sha256(saved['canonical_public_document_json'].encode()).hexdigest(),export['public_content_hash'])

if __name__=='__main__':unittest.main(verbosity=2)
