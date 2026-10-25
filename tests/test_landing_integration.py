"""SYNTHETIC approval fixtures only. Actual importer/build, never real owner exports."""
import copy,hashlib,importlib.util,json,pathlib,shutil,tempfile,unittest
ROOT=pathlib.Path(__file__).resolve().parents[1]
def load(path,name):
 s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
class LandingIntegration(unittest.TestCase):
 def setUp(self):
  self.temp=tempfile.TemporaryDirectory();self.root=pathlib.Path(self.temp.name)
  for p in ['content','scripts','dist']:shutil.copytree(ROOT/p,self.root/p)
  self.adapter=load(self.root/'scripts/import-approved-page.py','lp_import');self.adapter.ROOT=self.root;self.builder=load(self.root/'scripts/build-static.py','lp_build');self.builder.ROOT=self.root;self.n=0
 def tearDown(self):self.temp.cleanup()
 def export(self,game='mobile-legends'):
  article='/artikel/cara-membaca-user-id-server-id-mobile-legends/' if game=='mobile-legends' else '/artikel/cara-menemukan-player-id-free-fire/'
  doc={'path':'/game/'+game+'/','title':'SYNTHETIC '+game+' metadata','description':'Synthetic local integration description; not a real owner draft.','target_keywords':['fixture'],'content':'# Synthetic '+game+' heading\n\nCanonical body only.\n\n## Bagian fixture\n- Satu isi\n- Dua isi\n\nBaca [panduan](https://gendut-store-panduan.onrender.com'+article+') dan [cek transaksi](https://gendutstore.com/transaction).\n\n## Pertanyaan fixture\nJawaban kanonik baru. <b>Teks bukan markup.</b>'};raw=json.dumps(doc,ensure_ascii=False,separators=(',',':'));sha=hashlib.sha256(raw.encode()).hexdigest();value={'schema_version':1,'page_id':'synthetic-'+game,'revision':1,'canonical_public_document_json':raw,'public_content_hash':sha,'content_hash':sha,'document':doc,'source':{'origin':'https://gendut-store-panduan.onrender.com','repository':'phantomx567/gendut-store-seo','branch':'main'},'approval':{'actor':'Reza','revision':1,'content_hash':sha},'qa':{'agent_id':'synthetic-independent-reviewer','revision':1,'content_hash':sha}};p=self.root/('fixture-'+game+'.json');p.write_text(json.dumps(value));return p,value,article
 def build(self):
  self.n+=1;p=self.root/('output'+str(self.n));self.builder.build('https://gendut-store-panduan.onrender.com',p);return p
 def hashes(self):return {str(p.relative_to(self.root)):hashlib.sha256(p.read_bytes()).hexdigest() for p in (self.root/'content').rglob('*') if p.is_file()}
 def test_actual_import_and_build_two_new_LPs_keep_canonical_frame_and_only_new_body(self):
  for game in ['mobile-legends','free-fire']:
   p,v,article=self.export(game);old=next(x for x in json.loads((self.root/'content/site.json').read_text())['pages'] if x['path']==v['document']['path']);proof=self.adapter.import_export(p);entry=next(x for x in json.loads((self.root/'content/site.json').read_text())['pages'] if x['path']==v['document']['path']);self.assertEqual(entry['image'],old['image']);stored=json.loads((self.root/entry['approval_export']).read_text());self.assertEqual(stored['canonical_public_document_json'],v['canonical_public_document_json']);self.assertEqual(stored['public_content_hash'],v['public_content_hash'])
  out=self.build();m=json.loads((out/'site-manifest.json').read_text());self.assertEqual(len(m['pages']),11)
  for game in ['mobile-legends','free-fire']:
   html=(out/'game'/game/'index.html').read_text();self.assertIn('<h1>Synthetic '+game+' heading</h1>',html);self.assertIn('Canonical body only.',html);self.assertIn('class="game-hero"',html);self.assertIn('class="related-guide"',html);self.assertIn('href="https://gendutstore.com/transaction"',html);self.assertIn('&lt;b&gt;Teks bukan markup.&lt;/b&gt;',html);self.assertNotIn('FAQPage',html);self.assertNotIn('Langkah menuju produk pilihanmu',html);self.assertEqual(html.count('<h1>'),1)
 def test_bad_hash_approval_QA_and_missing_game_frame_reject_before_write(self):
  for key in ['hash','approval','qa','frame']:
   p,v,_=self.export()
   if key=='hash':v['public_content_hash']='0'*64
   elif key in ['approval','qa']:v[key]['content_hash']='0'*64
   else:
    site=json.loads((self.root/'content/site.json').read_text());next(x for x in site['pages'] if x['path']==v['document']['path']).pop('image');(self.root/'content/site.json').write_text(json.dumps(site))
   p.write_text(json.dumps(v));before=self.hashes()
   with self.assertRaises(ValueError):self.adapter.import_export(p)
   self.assertEqual(self.hashes(),before,key)
 def test_actual_withdrawn_article_absolute_inline_link_is_plaintext(self):
  p,v,article=self.export();self.adapter.import_export(p);site=json.loads((self.root/'content/site.json').read_text());a=next(x for x in site['pages'] if x['path']==article);snap=json.loads((self.root/a['approval_export']).read_text());row={'path':article,'page_id':snap['page_id'],'approval_revision':snap['revision'],'approved_snapshot_hash':snap['public_content_hash'],'revoked_through_revision':snap['revision']};(self.root/'content/release-selection.json').write_text(json.dumps({'schema_version':1,'withdrawn':[row]}));out=self.build();html=(out/'game/mobile-legends/index.html').read_text();self.assertIn('Baca panduan dan',html);self.assertNotIn('href="'+article+'"',html);self.assertNotIn('href="https://gendut-store-panduan.onrender.com'+article+'"',html);self.assertFalse((out/article.lstrip('/')/'index.html').exists())
if __name__=='__main__':unittest.main()
