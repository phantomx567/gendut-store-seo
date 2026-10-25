"""Actual scene rendering; catalog/icon fallback is retired."""
import copy,importlib.util,unittest
from pathlib import Path
spec=importlib.util.spec_from_file_location
s=spec('scene_render',Path(__file__).resolve().parents[1]/'scripts/article-pages.py');articles=importlib.util.module_from_spec(s);s.loader.exec_module(articles)
class ArticleCover(unittest.TestCase):
 def setUp(self):
  self.cover={'game_path':'/game/third-game/','path':'/assets/editorial-covers/'+'a'*64+'.webp','width':1672,'height':941,'alt':'Ilustrasi Third game & friends.'}
  self.page={'path':'/artikel/fixture-help/','title':'A useful Third game guide','description':'A readable explanation.','approved_document':{'related_paths':['/game/third-game/'],'banner':{'path':'/assets/articles/instruction.png'}},'editorial_cover':self.cover}
 def test_full_scene_intrinsic_dimensions_single_link_and_immutable_document(self):
  before=copy.deepcopy(self.page);html=articles.render_index([self.page]);self.assertIn(self.cover['path'],html);self.assertIn('width="1672" height="941"',html);self.assertIn('Ilustrasi Third game &amp; friends',html);self.assertNotIn('instruction.png',html);self.assertNotIn('editorial-cover-copy',html);self.assertEqual(html.count('<a '),1);self.assertEqual(self.page,before)
 def test_missing_scene_fails_even_if_catalog_metadata_exists(self):
  del self.page['editorial_cover']
  with self.assertRaisesRegex(ValueError,'belum tersedia'):articles.render_index([self.page],[{'path':'/game/third-game/','image':{'path':'/assets/icon.webp'}}])
 def test_explicit_shared_scene_renders_both_active_articles(self):
  html=articles.render_index([self.page,{**self.page,'path':'/artikel/second/'}]);self.assertEqual(html.count(self.cover['path']),2);self.assertIn('href="/artikel/second/"',html)
 def test_escaped_alt_is_not_raw_HTML(self):
  self.cover['alt']='Ilustrasi <script>game</script>';html=articles.render_index([self.page]);self.assertIn('&lt;script&gt;',html);self.assertNotIn('<script>',html)
if __name__=='__main__':unittest.main()
