"""Contextual anchors derive from active approved snapshots, never paragraph markup."""
import copy,importlib.util,json,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
s=importlib.util.spec_from_file_location('related_renderer',ROOT/'scripts/render-pages.py');renderer=importlib.util.module_from_spec(s);s.loader.exec_module(renderer)
class RelatedGuides(unittest.TestCase):
 def setUp(self):
  site=json.loads((ROOT/'content/site.json').read_text());self.data=site;self.page=copy.deepcopy(next(p for p in site['pages'] if p.get('page_type')=='article' and 'free-fire' in p['path']));snapshot=json.loads((ROOT/self.page['approval_export']).read_text());self.page['approved_document']=json.loads(snapshot['canonical_public_document_json']);collection=json.loads((ROOT/'content/editorial-covers.json').read_text());sha=collection['articles'][self.page['path']]['cover_sha256'];self.page['editorial_cover']=collection['covers'][sha]
 def test_real_href_exact_approved_title_summary_cover_and_immutable_input(self):
  before=copy.deepcopy(self.page);doc=self.page['approved_document'];html=renderer.related_guides('/game/free-fire/',[self.page]);self.assertIn('<a class="related-guide" href="'+doc['path']+'">',html);self.assertIn('<h3>'+doc['title']+'</h3>',html);self.assertIn(doc['description'],html);self.assertIn(self.page['editorial_cover']['path'],html);self.assertNotIn('&lt;a',html);self.assertEqual(self.page,before)
 def test_missing_unrelated_unapproved_and_withdrawn_are_omitted(self):
  self.assertEqual(renderer.related_guides('/game/free-fire/',[]),'');self.assertEqual(renderer.related_guides('/game/mobile-legends/',[self.page]),'');self.assertEqual(renderer.related_guides('/game/free-fire/',[{**self.page,'approval_export':None}]),'');self.assertEqual(renderer.related_guides('/game/free-fire/',[self.page],{self.page['path']}),'')
 def test_active_missing_cover_fails_closed(self):
  self.page.pop('editorial_cover')
  with self.assertRaisesRegex(ValueError,'qualified'):renderer.related_guides('/game/free-fire/',[self.page])
 def test_plain_text_is_escaped_not_interpreted_as_extra_links(self):
  self.page['approved_document']['description']='<a href="https://bad.test">plain</a>'
  html=renderer.related_guides('/game/free-fire/',[self.page]);self.assertIn('&lt;a href=',html);self.assertEqual(html.count('<a '),1)
 def test_actual_legacy_and_approved_landing_render_both_include_real_context_link(self):
  data=copy.deepcopy(self.data);data['pages']=[p for p in data['pages'] if not p.get('page_type')];data['pages'].append(self.page);data['withdrawn_paths']=[];route='game/free-fire/index.html';before=renderer.render_pages(data)[route];self.assertIn('class="article-section related-guides"',before);self.assertIn('href="'+self.page['path']+'"',before)
  landing=next(p for p in data['pages'] if p['path']=='/game/free-fire/');landing['approved_document']={'path':landing['path'],'title':landing['title'],'description':landing['description'],'target_keywords':[],'content':'Exact approved fixture prose.'};after=renderer.render_pages(data)[route];self.assertIn('<p>Exact approved fixture prose.</p>',after);self.assertIn('class="article-section related-guides"',after);self.assertIn('href="'+self.page['path']+'"',after)

if __name__=='__main__':unittest.main()
