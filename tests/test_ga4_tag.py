import unittest,importlib.util,json,pathlib,subprocess,tempfile,io,tarfile,ast,re
from html.parser import HTMLParser
ROOT=pathlib.Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('renderer',ROOT/'scripts/render-pages.py');renderer=importlib.util.module_from_spec(spec);spec.loader.exec_module(renderer)
class Scripts(HTMLParser):
 def __init__(self):super().__init__();self.head=False;self.current=None;self.scripts=[]
 def handle_starttag(self,t,a):
  if t=='head':self.head=True
  if t=='script':self.current={'attrs':dict(a),'head':self.head,'text':''};self.scripts.append(self.current)
 def handle_data(self,d):
  if self.current is not None:self.current['text']+=d
 def handle_endtag(self,t):
  if t=='script':self.current=None
  if t=='head':self.head=False
class GA4(unittest.TestCase):
 def test_every_current_page_exact_once_in_head(self):
  with tempfile.TemporaryDirectory() as out:
   subprocess.run(['python',str(ROOT/'scripts/build-static.py'),'--origin','https://gendut-store-panduan.onrender.com','--output',out],check=True,capture_output=True)
   manifest=json.loads((pathlib.Path(out)/'site-manifest.json').read_text());pages={(v['path'].lstrip('/')+'index.html'):(pathlib.Path(out)/(v['path'].lstrip('/')+'index.html')).read_text() for v in manifest['pages']}
   for p in pathlib.Path(out).glob('google*.html'):
    self.assertEqual(p.read_bytes(),(ROOT/'dist'/p.name).read_bytes());self.assertNotIn(b'gtag',p.read_bytes())
  self.assertEqual(len(pages),11)
  for path,html in pages.items():
   with self.subTest(path=path):
    p=Scripts();p.feed(html);external=[s for s in p.scripts if 'googletagmanager.com/gtag/js' in s['attrs'].get('src','')];inline=[s for s in p.scripts if "gtag('config'" in s['text']]
    self.assertEqual(len(external),1);self.assertEqual(len(inline),1);self.assertTrue(external[0]['head']);self.assertTrue(inline[0]['head']);self.assertIn('async',external[0]['attrs']);self.assertEqual(external[0]['attrs']['src'],'https://www.googletagmanager.com/gtag/js?id=G-M4D32F17L8');self.assertEqual(inline[0]['text'].count("gtag('config', 'G-M4D32F17L8')"),1);self.assertNotIn('user_id',inline[0]['text']);self.assertNotIn('email',inline[0]['text'])
 def test_exact_external_exception_and_negative_contexts(self):
  spec=importlib.util.spec_from_file_location('builder',ROOT/'scripts/build-static.py');b=importlib.util.module_from_spec(spec);spec.loader.exec_module(b)
  def validate(tag):
   p=b.Page();p.feed(tag);b.validate_assets(p,ROOT/'dist')
  good='<head><script async src="'+b.GA4_URL+'"></script></head>'
  validate(good)
  bad=[good.replace('G-M4D32F17L8','G-P8MJX026LN'),good+good,good.replace(' async',''),good.replace('head','body'),good.replace('script','img'),good.replace('https:','http:'),good.replace('https:',''),good.replace('www.googletagmanager.com','evil.example'),good.replace('G-M4D32F17L8','G-WRONG'),good.replace('gtag/js','other.js'),good.replace(b.GA4_URL,b.GA4_URL+'&extra=1'),good+'<img src="https://evil.example/a.png">',good+'<link rel="stylesheet" href="https://evil.example/a.css">',good+'<img src="/../README.md">',good+'<img src="/assets/missing.png">',good+'<img src="'+b.GA4_URL+'">']
  for case in bad:
   with self.subTest(case=case):
    with self.assertRaises(ValueError):validate(case)
 def test_official_build_repeat_and_exact_baseline_invariance(self):
  with tempfile.TemporaryDirectory() as temp:
   tmp=pathlib.Path(temp);base=tmp/'base';base.mkdir()
   archive=subprocess.run(['git','archive','HEAD'],cwd=ROOT,check=True,capture_output=True).stdout
   with tarfile.open(fileobj=io.BytesIO(archive)) as tar:tar.extractall(base,filter='data')
   baseline_tag=''
   for node in ast.parse((base/'scripts/render-pages.py').read_text()).body:
    if isinstance(node,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='GA4_TAG' for t in node.targets):baseline_tag=ast.literal_eval(node.value)
   if baseline_tag:
    match=re.search(r'gtag/js\?id=(G-[A-Z0-9]{10})',baseline_tag);self.assertIsNotNone(match)
    self.assertEqual(baseline_tag,renderer.GA4_TAG.replace('G-M4D32F17L8',match.group(1)),'Normalize only an exact standard baseline tag, not arbitrary HTML')
   outputs=[]
   for src,name in [(base,'baseline'),(ROOT,'candidate1'),(ROOT,'candidate2')]:
    out=tmp/name;subprocess.run(['python',str(src/'scripts/build-static.py'),'--origin','https://gendut-store-panduan.onrender.com','--output',str(out)],check=True,capture_output=True);outputs.append(out)
   baseline,one,two=outputs;m=json.loads((one/'site-manifest.json').read_text());self.assertEqual(len(m['pages']),11)
   expected={p.relative_to(baseline) for p in baseline.rglob('*') if p.is_file()};self.assertEqual(expected,{p.relative_to(one) for p in one.rglob('*') if p.is_file()})
   content={pathlib.Path(v['path'].lstrip('/')+'index.html') for v in m['pages']}
   for rel in expected:
    if rel==pathlib.Path('site-manifest.json'):continue
    a,b,c=(x/rel for x in outputs)
    if rel in content:
     baseline_html=a.read_text()
     if baseline_tag:
      self.assertEqual(baseline_html.count(baseline_tag),1);baseline_html=baseline_html.replace(baseline_tag,'',1)
     self.assertEqual(b.read_text().replace(renderer.GA4_TAG,'',1),baseline_html,str(rel))
    else:self.assertEqual(b.read_bytes(),a.read_bytes(),str(rel))
    self.assertEqual(b.read_bytes(),c.read_bytes(),str(rel)+' repeat')
   old=json.loads((baseline/'site-manifest.json').read_text());self.assertEqual(m['assets'],old['assets'])
   for a,b in zip(old['pages'],m['pages']):
    self.assertEqual({k:v for k,v in a.items() if k!='content_sha256'},{k:v for k,v in b.items() if k!='content_sha256'})
 def test_standard_queue_preserves_existing_events(self):
  p=Scripts();p.feed(renderer.head({'title':'Synthetic','description':'Synthetic'}));code=next(s['text'] for s in p.scripts if "gtag('config'" in s['text'])
  js="const vm=require('node:vm'),a=require('node:assert/strict'),c={dataLayer:[['existing']]};c.window=c;vm.runInNewContext("+json.dumps(code)+",c);a.equal(c.dataLayer.length,3);a.equal(c.dataLayer[0][0],'existing');a.equal(c.dataLayer[1][0],'js');a.equal(c.dataLayer[2][0],'config');a.equal(c.dataLayer[2][1],'G-M4D32F17L8');a.equal(c.dataLayer[2].length,2);"
  subprocess.run(['node','-e',js],check=True,capture_output=True)
if __name__=='__main__':unittest.main()
