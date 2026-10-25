"""Deliberate synthetic QA assignment, never a production automatic fallback."""
import binascii,hashlib,json,re,struct,zlib

def assign(root,doc):
    related=doc.get('related_paths',[])
    game=related[0] if isinstance(related,list) and related and isinstance(related[0],str) and re.fullmatch(r'/game/[a-z0-9]+(?:-[a-z0-9]+)*/',related[0]) else '/game/free-fire/'
    def chunk(k,v):return struct.pack('>I',len(v))+k+v+struct.pack('>I',binascii.crc32(k+v)&0xffffffff)
    # Encode the fixture game into pixels so variants for distinct games have distinct hashes.
    pixel=hashlib.sha256(game.encode()).digest()[:3]
    data=b'\x89PNG\r\n\x1a\n'+chunk(b'IHDR',struct.pack('>IIBBBBB',64,36,8,2,0,0,0))+chunk(b'IDAT',zlib.compress((b'\0'+pixel*64)*36))+chunk(b'IEND',b'')
    sha=hashlib.sha256(data).hexdigest();path='/assets/editorial-covers/'+sha+'.png';target=root/'dist'/path.lstrip('/');target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(data)
    file=root/'content/editorial-covers.json';collection=json.loads(file.read_text()) if file.exists() else {'schema_version':1,'covers':{},'articles':{}}
    collection['covers'][sha]={'game_path':game,'path':path,'sha256':sha,'mime':'image/png','width':64,'height':36,'alt':'Ilustrasi sintetis untuk pengujian terisolasi.'}
    collection['articles'][doc['path']]={'game_path':game,'cover_sha256':sha};file.write_text(json.dumps(collection));return path
