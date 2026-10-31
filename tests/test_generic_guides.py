"""Generic renderer regression tests; synthetic documents only, no network."""
import copy,hashlib,importlib.util,json,pathlib,re,shutil,tempfile,unittest
from html.parser import HTMLParser
ROOT=pathlib.Path(__file__).resolve().parents[1]
def load(path,name):
 s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
lp=load(ROOT/'scripts/landing-pages.py','generic_lp')
class Tags(HTMLParser):
 def __init__(self,body):super().__init__();self.tags=[];self.links=[];self.feed(body)
 def handle_starttag(self,t,a):
  self.tags.append(t)
  if t=='a':self.links.append(dict(a).get('href'))
class GenericSafety(unittest.TestCase):
 def test_semantic_blocks_and_exact_safe_links(self):
  text='Intro.\n\n## Checklist\n\n- Account\n- Product\n\n[Official help](https://support.example.org/guide)'
  p=Tags(lp.generic_content_blocks(text));self.assertEqual(p.tags.count('h2'),1);self.assertEqual(p.tags.count('ul'),1);self.assertEqual(p.tags.count('li'),2);self.assertEqual(p.links,['https://support.example.org/guide'])
 def test_legacy_plain_paragraphs_unchanged(self):
  self.assertEqual(lp.generic_content_blocks('Plain\nline\n\nOther'),'<'+'p>Plain<br>line</p><p>Other</p>')
 def test_html_is_text(self):
  body=lp.generic_content_blocks('<script>x</script>\n\n## <img src=x>\n\n- <iframe>');self.assertNotIn('<script',body);self.assertNotIn('<img',body);self.assertNotIn('<iframe',body)
 def test_unsafe_and_unsupported_links_fail(self):
  for url in ['javascript:bad','data:text/html,bad','http://example.org','//example.org','https://user:pass@example.org','https://127.0.0.1/','https://127.1/','https://foo.local./','https://foo.internal/','https://foo.chatgpt.site/','https://example.org:443/','https://example.org\\evil','https://gendutstore.com/unknown','https://localhost/']:
   with self.subTest(url=url),self.assertRaises(ValueError):lp.generic_content_blocks('[link]('+url+')')
 def test_current_internal_and_absolute_withdrawal_guard(self):
  pages=[{'path':'/artikel/current/'}]
  for prefix in ['', 'https://gendut-store-panduan.onrender.com']:
   content='[read]('+prefix+'/artikel/current/)';self.assertIn('href="/artikel/current/"',lp.generic_content_blocks(content,pages))
   with self.assertRaises(ValueError):lp.generic_content_blocks(content,pages,['/artikel/current/'])
 def test_no_inferred_links_or_duplicate_h1(self):
  self.assertEqual(Tags(lp.generic_content_blocks('Official help title only')).links,[])
  with self.assertRaises(ValueError):lp.generic_content_blocks('# Duplicate title')
class GenericBuild(unittest.TestCase):
 def setUp(self):
  self.temp=tempfile.TemporaryDirectory();self.root=pathlib.Path(self.temp.name)
  for name in ['content','scripts','dist']:shutil.copytree(ROOT/name,self.root/name)
  self.adapter=load(self.root/'scripts/import-approved-page.py','generic_import');self.adapter.ROOT=self.root;self.n=0
 def tearDown(self):self.temp.cleanup()
 def build(self):
  self.n+=1;out=self.root/('output'+str(self.n));builder=load(self.root/'scripts/build-static.py','generic_build'+str(self.n));builder.ROOT=self.root;builder.build('https://gendut-store-panduan.onrender.com',out);return out
 def fixture(self):
  doc={'path':'/game/synthetic-guide/','title':'Synthetic guide title','description':'Synthetic useful description for isolated rendering tests.','target_keywords':['fixture'],'content':'Introductory synthetic text.\n\n## Checklist\n\n- Check account\n- Check product\n\n[Official help](https://support.example.org/guide)\n\n[Catalogue](https://gendutstore.com/games)'}
  raw=json.dumps(doc,ensure_ascii=False,separators=(',',':'));sha=hashlib.sha256(raw.encode()).hexdigest();v={'schema_version':1,'page_id':'synthetic-generic-guide','revision':1,'canonical_public_document_json':raw,'public_content_hash':sha,'content_hash':sha,'document':doc,'source':{'origin':'https://gendut-store-panduan.onrender.com','repository':'phantomx567/gendut-store-seo','branch':'main'},'approval':{'actor':'Reza','revision':1,'content_hash':sha},'qa':{'agent_id':'synthetic-independent-reviewer','revision':1,'content_hash':sha}};p=self.root/'synthetic-export.json';p.write_text(json.dumps(v));return p,v
 def test_real_import_build_keeps_hash_semantics_and_links(self):
  p,v=self.fixture();self.adapter.import_export(p);out=self.build();html=(out/'game/synthetic-guide/index.html').read_text();parsed=Tags(html)
  self.assertEqual(parsed.tags.count('h1'),1);self.assertIn('<h2>Checklist</h2>',html);self.assertIn('<li>Check account</li>',html);self.assertIn('https://support.example.org/guide',parsed.links)
  manifest=json.loads((out/'site-manifest.json').read_text());record=next(p for p in manifest['pages'] if p['path']==v['document']['path']);self.assertEqual(record['approved_snapshot_hash'],v['public_content_hash'])
 def test_approval_QA_and_hash_still_required(self):
  for key in ['approval','qa','hash']:
   p,v=self.fixture()
   if key=='hash':v['public_content_hash']='0'*64
   else:v[key]['content_hash']='0'*64
   p.write_text(json.dumps(v));before=(self.root/'content/site.json').read_bytes()
   with self.assertRaises(ValueError):self.adapter.import_export(p)
   self.assertEqual(before,(self.root/'content/site.json').read_bytes())
 def test_all_current_pages_byte_identical_to_previous_renderer(self):
  current=self.build();renderer=self.root/'scripts/render-pages.py';source=renderer.read_text()
  new="paragraphs=landings.generic_content_blocks(doc['content'],data['pages'],data.get('withdrawn_paths',[])) if doc['path'].startswith('/game/') else "
  self.assertEqual(source.count(new),1);renderer.write_text(source.replace(new,'paragraphs='));baseline=self.build()
  manifest=json.loads((baseline/'site-manifest.json').read_text());self.assertEqual(len(manifest['pages']),11)
  for row in manifest['pages']:
   path=row['path'].lstrip('/')+'index.html';self.assertEqual((baseline/path).read_bytes(),(current/path).read_bytes(),row['path'])
  self.assertEqual((baseline/'sitemap.xml').read_bytes(),(current/'sitemap.xml').read_bytes());self.assertEqual((baseline/'robots.txt').read_bytes(),(current/'robots.txt').read_bytes())
  for asset in manifest['assets']:self.assertEqual((baseline/asset['path'].lstrip('/')).read_bytes(),(current/asset['path'].lstrip('/')).read_bytes())
if __name__=='__main__':unittest.main()
