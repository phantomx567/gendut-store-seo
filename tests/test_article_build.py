"""Article publication fixtures are isolated; no real draft enters the public repo."""
import copy
import hashlib
import importlib.util
import json
import re
from pathlib import Path
import shutil
import tempfile
import unittest
from unittest.mock import patch

REPO=Path(__file__).resolve().parents[1]

def load(name,path):
    spec=importlib.util.spec_from_file_location(name,path);module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);return module

class ArticleBuild(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.root=Path(self.temp.name)
        for name in ['content','scripts','dist']:shutil.copytree(REPO/name,self.root/name)
        self.builder=load('article_builder',self.root/'scripts/build-static.py');self.builder.ROOT=self.root
        self.adapter=load('article_adapter',self.root/'scripts/import-approved-page.py');self.adapter.ROOT=self.root
        self.count=0
        self.doc={'page_type':'article','path':'/artikel/isolated-help/','title':'Isolated article answering one question','description':'An isolated article fixture for testing the actual approved publication adapter.','target_keywords':['isolated help'],'content':{'lead':'A useful introduction belonging only to an isolated test fixture.','sections':[{'heading':'Check the original record','paragraphs':['Use the official instructions. <script>fixture is plain text</script>'],'bullets':['Keep the reference available.'],'source_ids':['official']}]},'sources':[{'id':'official','label':'Official isolated help reference','url':'https://help.example.org/articles/check?lang=id#record','verified_at':'2026-10-16T02:00:00Z'}],'related_paths':['/game/free-fire/']}
    def tearDown(self):self.temp.cleanup()
    def export(self,doc=None):
        doc=copy.deepcopy(doc or self.doc);raw=json.dumps(doc,ensure_ascii=False,separators=(',',':'));digest=hashlib.sha256(raw.encode()).hexdigest()
        value={'schema_version':1,'page_id':'isolated-article','revision':2,'canonical_public_document_json':raw,'public_content_hash':digest,'content_hash':digest,'document':{**doc,'pic_agent_id':'PRIVATE_CANARY','workflow_task_id':'PRIVATE_TASK'},'source':self.adapter.module.SOURCE,'approval':{'actor':'Reza','revision':2,'content_hash':digest},'qa':{'agent_id':'PRIVATE_QA','revision':2,'content_hash':digest}}
        file=self.root/'private-export.json';file.write_text(json.dumps(value));return file,value
    def build(self):
        self.count+=1;out=self.root/('out'+str(self.count))
        with patch.dict('os.environ',{'RENDER_GIT_COMMIT':'b'*40}):self.builder.build('https://gendut-store-panduan.onrender.com',out)
        return out,json.loads((out/'site-manifest.json').read_text())
    def test_approved_article_builds_citations_schema_hub_and_exact_binding(self):
        file,value=self.export();self.adapter.import_export(file);out,manifest=self.build()
        html=(out/'artikel/isolated-help/index.html').read_text();hub=(out/'artikel/index.html').read_text()
        self.assertIn('&lt;script&gt;',html);self.assertNotIn('<script>fixture',html)
        self.assertIn(self.doc['sources'][0]['url'].replace('&','&amp;'),html);self.assertIn('"@type": "Article"',html);self.assertIn('"@type": "BreadcrumbList"',html)
        self.assertNotIn('datePublished',html);self.assertNotIn('"author"',html);self.assertNotIn('https://gendutstore.com/games',html)
        self.assertIn(self.doc['title'],hub);self.assertEqual(len(manifest['pages']),10)
        article=next(p for p in manifest['pages'] if p['path']==self.doc['path']);index=next(p for p in manifest['pages'] if p['path']=='/artikel/')
        self.assertEqual(article['approved_snapshot_hash'],value['public_content_hash']);self.assertEqual(article['approval_revision'],2)
        self.assertEqual(index['derived_from'],[{k:article[k] for k in ['page_id','approval_revision','approved_snapshot_hash']}]);self.assertNotIn('approval_revision',index)
        for path in (self.root/'content/approved').glob('*'):
            text=path.read_text();self.assertNotIn('PRIVATE',text);self.assertNotIn('"qa"',text)
        for path in out.rglob('*'):
            if path.suffix in ['.html','.json','.xml']:self.assertNotIn('PRIVATE',path.read_text())
        self.assertIn(self.doc['path'],(out/'sitemap.xml').read_text())
        self.assertNotIn(self.doc['title'],(out/'game/valorant/index.html').read_text(),'Articles are not game-related card entries')
    def test_script_parser_tokens_stay_json_data_and_roundtrip_exactly(self):
        doc=copy.deepcopy(self.doc);doc['title']='Fixture <!--<script> parser title';file,_=self.export(doc);self.adapter.import_export(file)
        out,_=self.build();html=(out/'artikel/isolated-help/index.html').read_text()
        raw=re.search(r'<script type="application/ld\+json">(.*?)</script>',html,re.S).group(1)
        self.assertNotIn('<',raw,'No HTML script-state transition is allowed in JSON data')
        self.assertEqual(json.loads(raw)['@graph'][0]['headline'],doc['title'])
        self.assertIn('<main id="konten"',html)
    def test_no_approved_article_has_no_hub_and_preserves_google_file(self):
        out,manifest=self.build();self.assertEqual(len(manifest['pages']),8);self.assertFalse((out/'artikel').exists());self.assertNotIn('/artikel/',(out/'index.html').read_text())
        self.assertEqual((out/'google3a3d604f96efc674.html').read_bytes(),b'google-site-verification: google3a3d604f96efc674.html')
    def test_unapproved_raw_article_cannot_enter_build_or_create_output(self):
        sitefile=self.root/'content/site.json';site=json.loads(sitefile.read_text());site['pages'].append({**self.doc,'h1':self.doc['title']});sitefile.write_text(json.dumps(site))
        with self.assertRaisesRegex(ValueError,'snapshot approved'):self.build()
        self.assertFalse((self.root/'out1').exists())
    def test_missing_qa_wrong_revision_and_changed_public_hash_refused(self):
        for key in ['qa','approval','public_content_hash']:
            file,value=self.export()
            if key=='public_content_hash':value[key]='0'*64
            else:value[key]['revision']=1
            file.write_text(json.dumps(value))
            with self.assertRaises(ValueError):self.adapter.import_export(file)
        self.assertFalse((self.root/'content/approved').exists())
    def test_typed_contract_rejects_private_fields_paths_and_bad_references(self):
        candidates=[]
        for path in ['/artikel/../escape/','/artikel/','//attacker.example/a/']:
            doc=copy.deepcopy(self.doc);doc['path']=path;candidates.append(doc)
        doc=copy.deepcopy(self.doc);doc['worker_id']='PRIVATE';candidates.append(doc)
        doc=copy.deepcopy(self.doc);doc['content']['sections'][0]['source_ids']=['missing'];candidates.append(doc)
        for doc in candidates:
            file,_=self.export(doc)
            with self.assertRaises(ValueError):self.adapter.import_export(file)
    def test_sources_reject_unsafe_destinations_and_false_time_order(self):
        for url in ['javascript:alert(1)','http://help.example.org/','https://127.0.0.1/a','https://user:password@help.example.org/a','https://example.internal/a']:
            doc=copy.deepcopy(self.doc);doc['sources'][0]['url']=url;file,_=self.export(doc)
            with self.assertRaises(ValueError):self.adapter.import_export(file)
        doc=copy.deepcopy(self.doc);doc['sources'][0]['published_at']='2026-10-17T02:00:00Z';file,_=self.export(doc)
        with self.assertRaises(ValueError):self.adapter.import_export(file)
    def test_related_path_must_exist_and_receipt_hash_is_rechecked_by_build(self):
        doc=copy.deepcopy(self.doc);doc['related_paths']=['/game/not-built/'];file,_=self.export(doc);self.adapter.import_export(file)
        with self.assertRaisesRegex(ValueError,'Tautan halaman lokal'):self.build()
    def test_saved_snapshot_is_revalidated_during_build(self):
        file,_=self.export();self.adapter.import_export(file)
        saved=next((self.root/'content/approved').glob('*.json'));value=json.loads(saved.read_text());value['canonical_public_document_json']+=' ';saved.write_text(json.dumps(value))
        with self.assertRaisesRegex(ValueError,'hash'):self.build()

if __name__=='__main__':unittest.main()
