"""Derived hub covers follow active related game metadata, never editorial PNGs."""
import copy
import importlib.util
from pathlib import Path
import unittest

spec=importlib.util.spec_from_file_location('cover_articles',Path(__file__).resolve().parents[1]/'scripts/article-pages.py')
articles=importlib.util.module_from_spec(spec);spec.loader.exec_module(articles)

class ArticleCover(unittest.TestCase):
    def setUp(self):
        self.page={'path':'/artikel/fixture-help/','title':'A useful guide','description':'A readable explanation.','approved_document':{'related_paths':['/game/third-game/'],'banner':{'path':'/assets/articles/instruction.png'}}}
        self.game={'path':'/game/third-game/','copy':{'game':'Third game & friends'},'image':{'path':'/assets/third-game.webp','width':358,'height':358}}
    def test_dynamic_explicit_metadata_whole_art_and_single_article_link(self):
        original=copy.deepcopy(self.page)
        html=articles.render_index([self.page],[self.page,self.game])
        self.assertIn('src="/assets/third-game.webp"',html)
        self.assertIn('width="358" height="358"',html)
        self.assertIn('Third game &amp; friends',html)
        self.assertNotIn('instruction.png',html)
        self.assertEqual(html.count('<a '),1)
        self.assertIn('href="/artikel/fixture-help/"',html)
        self.assertEqual(self.page,original)
    def test_withdrawn_or_missing_game_has_readable_text_fallback_without_dead_link(self):
        html=articles.render_index([self.page],[self.page])
        self.assertNotIn('<img',html)
        self.assertNotIn('/game/third-game/',html)
        self.assertIn('A useful guide',html)
        self.assertIn('Baca artikel',html)
    def test_unsafe_or_incomplete_metadata_never_fabricates_image(self):
        for field,value in [('path','https://other.test/game.webp'),('path','/assets/../game.webp'),('width',0),('height',True),('width','358')]:
            game=copy.deepcopy(self.game);game['image'][field]=value
            self.assertNotIn('<img',articles.render_index([self.page],[game]))
        game=copy.deepcopy(self.game);game['copy']={}
        self.assertNotIn('<img',articles.render_index([self.page],[game]))
        for field in ('copy','image'):
            game=copy.deepcopy(self.game);game[field]=None
            self.assertNotIn('<img',articles.render_index([self.page],[game]))
    def test_later_valid_related_game_is_selected_and_names_are_escaped(self):
        self.page['approved_document']['related_paths'].insert(0,'/game/removed/')
        self.game['copy']['game']='<script>game</script>'
        html=articles.render_index([self.page],[self.game])
        self.assertIn('&lt;script&gt;game&lt;/script&gt;',html)
        self.assertNotIn('<script>',html)
    def test_explicit_game_cover_name_overrides_storefront_region_label(self):
        self.game['copy']['game']='Third game regional storefront'
        self.game['image']['cover_name']='Third game'
        html=articles.render_index([self.page],[self.game])
        self.assertIn('<strong>Third game</strong>',html)
        self.assertNotIn('regional storefront',html)

if __name__=='__main__':unittest.main()
