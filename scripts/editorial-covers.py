"""Curated presentation assets, independent of immutable Article snapshots."""
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import struct

spec=importlib.util.spec_from_file_location('cover_png',Path(__file__).with_name('article-banner.py'))
png=importlib.util.module_from_spec(spec);spec.loader.exec_module(png)
FIELDS={'path','alt','width','height','sha256','mime'}
GAME_PATH=r'/game/[a-z0-9]+(?:-[a-z0-9]+)*/'

def descriptor(value):
    if not isinstance(value,dict) or set(value)!=FIELDS:raise ValueError('Metadata cover editorial tidak sesuai whitelist.')
    digest=value['sha256'];mime=value['mime'];extension={'image/png':'png','image/webp':'webp'}.get(mime)
    if not extension or not isinstance(digest,str) or not re.fullmatch('[0-9a-f]{64}',digest) or value['path']!='/assets/editorial-covers/'+digest+'.'+extension:raise ValueError('Path cover editorial harus sesuai MIME dan SHA256.')
    if not isinstance(value['alt'],str) or not 10<=len(value['alt'].strip())<=500 or '\x00' in value['alt'] or 'ilustrasi' not in value['alt'].casefold():raise ValueError('ALT cover harus menjelaskan ilustrasi game secara jujur.')
    w=value['width'];h=value['height']
    if type(w)!=int or type(h)!=int or not 1<=h<w<=8192 or w*h>40000000:raise ValueError('Cover editorial memerlukan dimensi landscape yang valid.')
    return value

def webp_dimensions(data):
    if len(data)<20 or data[:4]!=b'RIFF' or data[8:12]!=b'WEBP' or struct.unpack_from('<I',data,4)[0]+8!=len(data):raise ValueError('Cover bukan WebP lengkap.')
    pos=12;canvas=None;image=None
    while pos+8<=len(data):
        kind=data[pos:pos+4];size=struct.unpack_from('<I',data,pos+4)[0];body=data[pos+8:pos+8+size];pos+=8+size+(size%2)
        if len(body)!=size or pos>len(data):raise ValueError('Chunk WebP terpotong.')
        if kind in (b'ANIM',b'ANMF'):raise ValueError('Cover animasi tidak didukung.')
        if kind==b'VP8X':
            if size!=10 or canvas is not None:raise ValueError('Canvas WebP tidak valid.')
            canvas=(int.from_bytes(body[4:7],'little')+1,int.from_bytes(body[7:10],'little')+1)
        elif kind in (b'VP8 ',b'VP8L'):
            if image is not None:raise ValueError('Data gambar WebP ganda.')
            if kind==b'VP8 ':
                if size<10 or body[3:6]!=b'\x9d\x01\x2a':raise ValueError('Frame WebP tidak valid.')
                image=(int.from_bytes(body[6:8],'little')&0x3fff,int.from_bytes(body[8:10],'little')&0x3fff)
            else:
                if size<5 or body[0]!=0x2f:raise ValueError('Frame lossless WebP tidak valid.')
                bits=int.from_bytes(body[1:5],'little');image=((bits&0x3fff)+1,((bits>>14)&0x3fff)+1)
    if pos!=len(data) or image is None or canvas is not None and canvas!=image:raise ValueError('Dimensi/data WebP tidak konsisten.')
    return image

def local_asset(root,value):
    descriptor(value);source=Path(root)/'dist';path=source/value['path'].lstrip('/')
    if not path.resolve().is_relative_to(source.resolve()) or any(p.is_symlink() for p in [path,*path.parents] if p!=source and source in p.parents) or not path.is_file() or path.stat().st_size>png.MAX_BYTES:raise ValueError('Berkas cover editorial lokal tidak aman atau belum tersedia.')
    data=path.read_bytes()
    if hashlib.sha256(data).hexdigest()!=value['sha256']:raise ValueError('Hash bytes cover editorial berbeda.')
    dimensions=png.inspect_png(data) if value['mime']=='image/png' else webp_dimensions(data)
    if dimensions!=(value['width'],value['height']):raise ValueError('Dimensi cover editorial berbeda dari bytes.')
    return path

def load(root):
    path=Path(root)/'content/editorial-covers.json'
    if not path.exists():return {}
    if path.is_symlink() or path.stat().st_size>100000:raise ValueError('Koleksi cover editorial tidak valid.')
    data=json.loads(path.read_text())
    if not isinstance(data,dict) or set(data)!={'schema_version','covers','articles'} or type(data['schema_version'])!=int or data['schema_version']!=1 or not isinstance(data['covers'],dict) or len(data['covers'])>100:raise ValueError('Schema koleksi cover editorial tidak valid.')
    if not isinstance(data['articles'],dict) or len(data['articles'])>200:raise ValueError('Penetapan cover Artikel tidak valid.')
    for digest,value in data['covers'].items():
        if not isinstance(value,dict) or set(value)!=FIELDS|{'game_path'} or not re.fullmatch(GAME_PATH,value['game_path']) or digest!=value['sha256']:raise ValueError('Varian cover/game/hash tidak valid.')
        descriptor({k:v for k,v in value.items() if k!='game_path'})
    for path,assignment in data['articles'].items():
        if not re.fullmatch(r'/artikel/[a-z0-9]+(?:-[a-z0-9]+)*/',path) or not isinstance(assignment,dict) or set(assignment)!={'game_path','cover_sha256'} or not re.fullmatch(GAME_PATH,assignment['game_path']) or assignment['cover_sha256'] not in data['covers']:raise ValueError('Penetapan cover Artikel harus eksplisit.')
        if data['covers'][assignment['cover_sha256']]['game_path']!=assignment['game_path']:raise ValueError('Game penetapan cover berbeda.')
    return data

def select(root,doc,collection=None):
    collection=load(root) if collection is None else collection
    assignment=collection.get('articles',{}).get(doc.get('path'))
    if assignment and assignment['game_path'] in doc.get('related_paths',[]):
        cover=collection.get('covers',{}).get(assignment['cover_sha256'])
        if cover and cover['game_path']==assignment['game_path']:
            value={k:v for k,v in cover.items() if k!='game_path'};local_asset(root,value)
            return cover
    raise ValueError('Cover editorial Artikel belum qualified atau belum ditetapkan; siapkan dan review sebelum import/build: '+doc.get('path',''))

def binding(cover,proof):
    return {key:proof[key] for key in ('page_id','approval_revision','approved_snapshot_hash')}|{'game_path':cover['game_path'],'path':cover['path'],'sha256':cover['sha256']}
