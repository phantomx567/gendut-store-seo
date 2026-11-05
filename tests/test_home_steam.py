"""Approved navigation is derived from active release selection, without new page copy."""
import copy,importlib.util,json,pathlib,unittest
ROOT=pathlib.Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('home_renderer',ROOT/'scripts/render-pages.py');r=importlib.util.module_from_spec(spec);spec.loader.exec_module(r)
class HomeSteam(unittest.TestCase):
 def setUp(self):
  self.site=json.loads((ROOT/'content/site.json').read_text());self.steam=next(p for p in self.site['pages'] if p['path']=='/game/voucher-steam-wallet/');self.steam['approved_document']={k:self.steam[k] for k in ('path','title','description')};self.steam['approved_document']['content']='Synthetic rendering fixture.';self.site['pages']=[p for p in self.site['pages'] if p.get('page_type')!='article']
 def test_approved_exact_metadata_eighth_and_idempotent(self):
  before=copy.deepcopy(self.site['pages'][0]['cards']);cards=r.home_cards(self.site);self.assertEqual(cards[:7],before);self.assertEqual(len(cards),8);self.assertEqual(cards[-1]['name'],self.steam['title']);self.assertEqual(cards[-1]['description'],self.steam['description']);self.assertNotIn('image',cards[-1]);self.assertEqual(r.home_cards(self.site),cards)
  html=r.render_pages(self.site)['index.html'];self.assertIn('class="game-card game-card--text"',html);self.assertIn('href="'+self.steam['path']+'"',html);node=next(n for n in self.site['pages'][0]['jsonLd']['@graph'] if n['@type']=='ItemList');self.assertEqual(node['numberOfItems'],8);self.assertEqual([v['position'] for v in node['itemListElement']],list(range(1,9)));self.assertEqual([v['url'] for v in node['itemListElement']],[self.site['origin']+c['path'] for c in cards])
 def test_withdrawn_missing_and_unapproved_not_promoted(self):
  for mode in ('withdrawn','missing','unapproved','mismatch'):
   with self.subTest(mode=mode):
    data=copy.deepcopy(self.site);s=next(p for p in data['pages'] if p['path']==self.steam['path'])
    if mode=='withdrawn':data['withdrawn_paths']=[s['path']]
    if mode=='missing':data['pages'].remove(s)
    if mode=='unapproved':s.pop('approval_export')
    if mode=='mismatch':s['approved_document']['path']='/game/other/'
    self.assertEqual(len(r.home_cards(data)),7)
 def test_visible_search_label_has_own_flow_container_and_preserves_input_binding(self):
  out=r.render_pages(self.site)['index.html'];self.assertEqual(out.count('class="search-field"'),1);self.assertEqual(out.count('<label for="game-search" class="search-label">Cari nama game atau voucher</label><div class="search-box">'),1);self.assertEqual(out.count('id="game-search"'),1);self.assertNotIn('<label for="game-search" class="sr-only">',out)
 def test_text_card_escaped_no_fabricated_image(self):
  card=r.home_cards(self.site)[-1];card['name']='<script>Steam</script>';out=r.home_card(card);self.assertNotIn('<img',out);self.assertNotIn('<script>',out);self.assertIn('&lt;script&gt;',out)
