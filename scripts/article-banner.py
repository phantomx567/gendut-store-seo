"""Bounded PNG structural checks; visual QA remains independent."""
import binascii
import hashlib
from pathlib import Path
import re
import struct

MAX_BYTES=15*1024*1024
FIELDS={'path','alt','width','height','sha256','mime'}

def descriptor(value):
    if not isinstance(value,dict) or set(value)!=FIELDS: raise ValueError('Metadata banner publik tidak sesuai whitelist.')
    digest=value['sha256']
    if not isinstance(digest,str) or not re.fullmatch('[0-9a-f]{64}',digest) or value['path']!='/assets/articles/'+digest+'.png' or value['mime']!='image/png': raise ValueError('Banner harus PNG dengan path sesuai SHA256.')
    if not isinstance(value['alt'],str) or not 3<=len(value['alt'].strip())<=500 or '\x00' in value['alt']: raise ValueError('Alt banner diperlukan.')
    w=value['width'];h=value['height']
    if type(w)!=int or type(h)!=int or not 1<=w<=8192 or not 1<=h<=8192 or w*h>40000000: raise ValueError('Dimensi banner melampaui batas gambar.')
    return value

def inspect_png(data):
    if not 45<=len(data)<=MAX_BYTES or data[:8]!=b'\x89PNG\r\n\x1a\n': raise ValueError('Bytes banner bukan PNG yang valid.')
    pos=8;has_data=False;ended=False;width=height=0
    while pos+12<=len(data):
        size=struct.unpack_from('>I',data,pos)[0];kind=data[pos+4:pos+8];end=pos+12+size
        if end>len(data): raise ValueError('Chunk PNG terpotong.')
        body=data[pos+8:pos+8+size]
        if (binascii.crc32(kind+body)&0xffffffff)!=struct.unpack_from('>I',data,pos+8+size)[0]: raise ValueError('CRC PNG tidak sesuai.')
        if pos==8:
            if kind!=b'IHDR' or size!=13: raise ValueError('IHDR PNG tidak valid.')
            width,height=struct.unpack_from('>II',body)
        elif kind==b'IHDR': raise ValueError('IHDR PNG ganda.')
        if kind==b'IDAT' and size:has_data=True
        pos=end
        if kind==b'IEND':
            if size or pos!=len(data): raise ValueError('Penutup PNG tidak valid.')
            ended=True;break
    if not has_data or not ended: raise ValueError('PNG memerlukan data dan penutup lengkap.')
    return width,height

def validate_bytes(data,value):
    descriptor(value)
    if len(data)>MAX_BYTES or hashlib.sha256(data).hexdigest()!=value['sha256']: raise ValueError('Bytes/hash banner berbeda dari snapshot approved.')
    if inspect_png(data)!=(value['width'],value['height']): raise ValueError('Dimensi bytes banner berbeda dari snapshot.')
    return data

def local_bytes(file,value):
    path=Path(file)
    if path.is_symlink() or not path.is_file() or path.stat().st_size>MAX_BYTES: raise ValueError('Berkas PNG lokal diperlukan, tanpa symlink dan maksimal15MiB.')
    return validate_bytes(path.read_bytes(),value)
