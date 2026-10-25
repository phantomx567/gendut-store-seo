"""Synthetic isolated fixtures only; these images are not production covers."""
import binascii,hashlib,importlib.util,json,struct,tempfile,unittest,zlib
from pathlib import Path
spec=importlib.util.spec_from_file_location('editorial_cover_fixture',Path(__file__).resolve().parents[1]/'scripts/editorial-covers.py');covers=importlib.util.module_from_spec(spec);spec.loader.exec_module(covers)

class EditorialCovers(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.root=Path(self.temp.name);(self.root/'content').mkdir()
        def chunk(k,v):return struct.pack('>I',len(v))+k+v+struct.pack('>I',binascii.crc32(k+v)&0xffffffff)
        self.data=b'\x89PNG\r\n\x1a\n'+chunk(b'IHDR',struct.pack('>IIBBBBB',64,36,8,2,0,0,0))+chunk(b'IDAT',zlib.compress((b'\0'+b'\x20\x30\x40'*64)*36))+chunk(b'IEND',b'')
        h=hashlib.sha256(self.data).hexdigest();self.asset={'path':'/assets/editorial-covers/'+h+'.png','sha256':h,'mime':'image/png','width':64,'height':36,'alt':'Ilustrasi game fixture, bukan screenshot resmi.'}
        p=self.root/'dist'/self.asset['path'].lstrip('/');p.parent.mkdir(parents=True);p.write_bytes(self.data)
        self.doc={'path':'/artikel/synthetic/','related_paths':['/game/fixture/']};self.collection={'schema_version':1,'covers':{h:{'game_path':'/game/fixture/',**self.asset}},'articles':{self.doc['path']:{'game_path':'/game/fixture/','cover_sha256':h}}}
    def tearDown(self):self.temp.cleanup()
    def test_actual_bytes_binding_and_reuse_preserve_document(self):
        before=json.dumps(self.doc);cover=covers.select(self.root,self.doc,self.collection);self.assertEqual(cover['game_path'],'/game/fixture/');self.assertEqual(json.dumps(self.doc),before)
        proof={'page_id':'fixture','approval_revision':2,'approved_snapshot_hash':'a'*64};self.assertEqual(covers.binding(cover,proof)['approved_snapshot_hash'],'a'*64)
        another={**self.doc,'path':'/artikel/another/'}
        with self.assertRaisesRegex(ValueError,'belum qualified'):covers.select(self.root,another,self.collection)
        self.collection['articles'][another['path']]=dict(self.collection['articles'][self.doc['path']])
        self.assertEqual(covers.select(self.root,another,self.collection),cover)
    def test_assignment_wrong_game_or_unknown_variant_is_rejected(self):
        path=self.root/'content/editorial-covers.json'
        for field,value in [('game_path','/game/other/'),('cover_sha256','f'*64)]:
            bad=json.loads(json.dumps(self.collection));bad['articles'][self.doc['path']][field]=value;path.write_text(json.dumps(bad))
            with self.assertRaises(ValueError):covers.load(self.root)
        with self.assertRaises(ValueError):covers.select(self.root,{**self.doc,'related_paths':['/game/other/']},self.collection)
    def test_missing_cover_fails_without_catalog_icon_fallback(self):
        with self.assertRaisesRegex(ValueError,'belum qualified'):covers.select(self.root,self.doc,{})
    def test_hash_dimension_path_alt_and_symlink_mismatch_fail(self):
        for field,value in [('sha256','b'*64),('width',65),('path','/assets/mlbb-game.webp'),('alt','Official screenshot')]:
            with self.assertRaises(ValueError):covers.local_asset(self.root,{**self.asset,field:value})
        p=self.root/'dist'/self.asset['path'].lstrip('/');target=self.root/'outside.png';target.write_bytes(self.data);p.unlink();p.symlink_to(target)
        with self.assertRaises(ValueError):covers.local_asset(self.root,self.asset)
    def test_collection_strict_public_whitelist(self):
        p=self.root/'content/editorial-covers.json';p.write_text(json.dumps(self.collection));self.assertEqual(covers.load(self.root),self.collection)
        p.write_text(json.dumps({**self.collection,'private_asset_id':'NOT_PUBLIC'}))
        with self.assertRaises(ValueError):covers.load(self.root)

if __name__=='__main__':unittest.main()
