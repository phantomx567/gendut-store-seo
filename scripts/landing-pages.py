"""Current canonical LP contract and shared game-frame rendering; no approval IO."""
import hashlib,html,json,re
from urllib.parse import urlsplit
FIELDS={'path','title','description','target_keywords','content'}
ROUTES={'/game/mobile-legends/','/game/free-fire/'}
e=lambda value:html.escape(str(value),quote=True)
def canonical_document(raw,digest,expected_path=None):
 if not isinstance(raw,str) or not re.fullmatch(r'[a-f0-9]{64}',digest or '') or hashlib.sha256(raw.encode('utf-8')).hexdigest()!=digest:raise ValueError('Canonical LP hash mismatch.')
 doc=json.loads(raw)
 if not isinstance(doc,dict) or set(doc)!=FIELDS or doc.get('path') not in ROUTES or (expected_path and doc['path']!=expected_path):raise ValueError('Unsupported LP document/path.')
 for key,lo,hi in [('title',3,200),('description',10,500),('content',20,60000)]:
  if not isinstance(doc[key],str) or not lo<=len(doc[key])<=hi:raise ValueError('Invalid LP '+key)
 if not isinstance(doc['target_keywords'],list) or len(doc['target_keywords'])>12 or any(not isinstance(k,str) or not 2<=len(k)<=100 for k in doc['target_keywords']):raise ValueError('Invalid LP keywords.')
 if re.search(r'(?:javascript|data|http)\s*:|(?<!:)//',doc['content'],re.I):raise ValueError('LP content must be plain text, not HTML or unsafe links.')
 return doc

def inline(text,pages,withdrawn=()):
 active={p['path'] for p in pages if p.get('page_type')=='article' and p.get('approval_export') and p['path'] not in withdrawn}
 reviewed={source['url'] for p in pages if p.get('page_type')=='article' and p.get('approval_export') and p['path'] not in withdrawn for source in p.get('approved_document',{}).get('sources',[])}
 result=[];position=0
 for match in re.finditer(r'\[([^\]\n]+)\]\(([^\s()]*)\)',text):
  result.append(e(text[position:match.start()]));label,href=match.groups();url=urlsplit(href)
  if any(ord(c)<33 for c in href) or href.startswith('//') or url.username or url.password or url.scheme not in ('','https') or url.port:raise ValueError('Unsafe LP hyperlink.')
  local=href if not url.scheme else url.path if url.netloc=='gendut-store-panduan.onrender.com' else None
  if local and local.startswith('/artikel/'):
   if url.query or url.fragment:raise ValueError('Article links require exact current path.')
   result.append('<a href="'+e(local)+'">'+e(label)+'</a>' if local in active else e(label))
  elif url.scheme=='https' and ((url.netloc=='gendutstore.com' and not url.query and not url.fragment) or href in reviewed):result.append('<a href="'+e(href)+'">'+e(label)+'</a>')
  else:raise ValueError('Unreviewed LP hyperlink.')
  position=match.end()
 return ''.join(result)+e(text[position:])
def content_blocks(content,pages=(),withdrawn=()):
 lines=content.splitlines();h1=None
 if lines and lines[0].startswith('# '):h1=lines.pop(0)[2:].strip()
 if any(line.startswith('# ') for line in lines):raise ValueError('Only the first line may be an H1.')
 # Legacy strings keep exactly the previous paragraph HTML.
 if not any(line.startswith(('## ','- ')) for line in lines):return h1,''.join('<p>'+inline(t,pages,withdrawn).replace('\n','<br>')+'</p>' for t in '\n'.join(lines).split('\n\n') if t.strip())
 out=[];paragraph=[];items=[]
 def flush():
  if paragraph:out.append('<p>'+inline('\n'.join(paragraph),pages,withdrawn).replace('\n','<br>')+'</p>');paragraph.clear()
  if items:out.append('<ul>'+''.join('<li>'+inline(x,pages,withdrawn)+'</li>' for x in items)+'</ul>');items.clear()
 for line in lines:
  if line.startswith('## '):flush();out.append('<h2>'+e(line[3:].strip())+'</h2>')
  elif line.startswith('- '):
   if paragraph:flush()
   items.append(line[2:].strip())
  elif not line.strip():flush()
  else:
   if items:flush()
   paragraph.append(line)
 flush();return h1,''.join(out)
def render_game_document(doc,frame,pages=(),withdrawn=()):
 if doc['path'] not in ROUTES or frame.get('path')!=doc['path']:raise ValueError('LP game frame/path mismatch.')
 im=frame.get('image',{});copy=frame.get('copy',{})
 if not re.fullmatch(r'/assets/[a-z0-9-]+\.webp',im.get('path','')) or any(type(im.get(k))!=int or im[k]<=0 for k in ['width','height']) or not copy.get('game'):raise ValueError('Known game image/identity required.')
 raw=json.dumps(doc,ensure_ascii=False,separators=(',',':'));canonical_document(raw,hashlib.sha256(raw.encode()).hexdigest(),frame['path'])
 h1,paragraphs=content_blocks(doc['content'],pages,withdrawn)
 return '<main id="konten" class="game-page"><div class="wrap"><nav class="breadcrumb" aria-label="Breadcrumb"><a href="/">Beranda</a><span aria-hidden="true">/</span><span aria-current="page">'+e(copy['game'])+'</span></nav><section class="game-hero"><div><p class="eyebrow">Panduan pilihan game &amp; voucher</p><h1>'+e(h1 or doc['title'])+'</h1><p class="lead">'+e(doc['description'])+'</p></div><div class="product-visual"><img src="'+e(im['path'])+'" width="'+str(im['width'])+'" height="'+str(im['height'])+'" alt="" fetchpriority="high"></div></section><article class="article-section approved-copy">'+paragraphs+'</article><p class="catalog-note"><a href="/">Kembali ke beranda</a></p><!-- related-guides --></div></main>'
