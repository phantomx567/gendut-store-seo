"""SYNTHETIC offline documents; not actual registry drafts/owner approval."""
import hashlib,importlib.util,json,tempfile,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
s=importlib.util.spec_from_file_location('preview',ROOT/'scripts/preview-landing-draft.py');preview=importlib.util.module_from_spec(s);s.loader.exec_module(preview)
class LandingPreview(unittest.TestCase):
 def setUp(self):self.doc={'path':'/game/mobile-legends/','title':'SYNTHETIC ML local fixture','description':'Synthetic offline preview; not an actual owner draft.','target_keywords':['fixture'],'content':'Unapproved fixture text, not new game facts.\n\n<script>plain text is escaped</script>'}
 def raw(self):return json.dumps(self.doc,ensure_ascii=False,separators=(',',':'))
 def test_actual_canonical_preview_game_art_escaping_and_readonly(self):
  with tempfile.TemporaryDirectory() as tmp:
   raw=self.raw();p=Path(tmp)/'doc.json';p.write_text(raw);before=(ROOT/'content/site.json').read_bytes();receipt=preview.preview(p,hashlib.sha256(raw.encode()).hexdigest(),Path(tmp)/'index.html');html=(Path(tmp)/'index.html').read_text();self.assertIn('class="game-hero"',html);self.assertIn('/assets/mlbb-game.webp',html);self.assertIn('&lt;script&gt;',html);self.assertIsNone(receipt['approval']);self.assertEqual(p.read_text(),raw);self.assertEqual((ROOT/'content/site.json').read_bytes(),before)
 def test_hash_path_schema_and_unsafe_scheme_rejected(self):
  raw=self.raw()
  with self.assertRaises(ValueError):preview.landing.canonical_document(raw,'0'*64)
  for value in ['javascript:alert(1)','data:text/html,hello','//evil.example/x']:
   self.doc['content']='Synthetic unsafe link fixture '+value;raw=self.raw()
   with self.assertRaises(ValueError):preview.landing.canonical_document(raw,hashlib.sha256(raw.encode()).hexdigest())
  self.doc['path']='/game/unknown/';raw=self.raw()
  with self.assertRaises(ValueError):preview.landing.canonical_document(raw,hashlib.sha256(raw.encode()).hexdigest())
 def test_no_preview_writes_in_production(self):
  with tempfile.TemporaryDirectory() as tmp:
   p=Path(tmp)/'doc.json';raw=self.raw();p.write_text(raw)
   with self.assertRaises(ValueError):preview.preview(p,hashlib.sha256(raw.encode()).hexdigest(),ROOT/'dist/new-preview.html')
if __name__=='__main__':unittest.main()

class LandingGrammar(unittest.TestCase):
 def setUp(self):
  self.article='/artikel/example-guide/';self.pages=[{'path':self.article,'page_type':'article','approval_export':'fixture','approved_document':{'sources':[{'url':'https://example.org/verified'}]}}]
 def test_explicit_heading_sections_list_and_safe_links(self):
  h1,body=preview.landing.content_blocks('# Pilihan akun\n\n## Data akun\n- User ID\n- Server ID\n\nBaca [panduan]('+self.article+') dan [status](https://gendutstore.com/transaction).',self.pages)
  self.assertEqual(h1,'Pilihan akun');self.assertIn('<h2>Data akun</h2>',body);self.assertIn('<ul><li>User ID</li><li>Server ID</li></ul>',body);self.assertIn('href="'+self.article+'"',body);self.assertIn('href="https://gendutstore.com/transaction"',body)
 def test_withdrawn_unknown_absolute_and_unapproved_articles_plaintext(self):
  for href in [self.article,'https://gendut-store-panduan.onrender.com'+self.article]:
   self.assertEqual(preview.landing.inline('[Panduan]('+href+')',self.pages,[self.article]),'Panduan');self.assertEqual(preview.landing.inline('[Panduan]('+href+')',[]),'Panduan')
 def test_bad_schemes_hosts_and_html_are_not_links(self):
  for href in ['javascript:alert','data:text/html,yes','http://gendutstore.com/','//gendutstore.com/','https://unknown.example/','/game/unknown/']:
   with self.assertRaises(ValueError):preview.landing.inline('[Klik]('+href+')',self.pages)
  self.assertEqual(preview.landing.inline('<a href="x">raw</a>',self.pages),'&lt;a href=&quot;x&quot;&gt;raw&lt;/a&gt;')
 def test_plain_legacy_paragraph_html_unchanged(self):
  self.assertEqual(preview.landing.content_blocks('Lama & aman.\nBaris kedua.\n\nParagraf akhir.')[1],'<p>Lama &amp; aman.<br>Baris kedua.</p><p>Paragraf akhir.</p>')
