"""Optional public Google HTML metatag; private owner export stays outside source."""
import argparse
import hashlib
import json
from pathlib import Path
import re
ROOT=Path(__file__).resolve().parents[1]
PROPERTY='https://gendut-store-panduan.onrender.com/'
PUBLIC_FIELDS={'property_id','method','value'}

def validate_public(value):
    if value is None or value=={}:return None
    if not isinstance(value,dict) or set(value)!=PUBLIC_FIELDS or value.get('property_id')!=PROPERTY or value.get('method')!='html_meta':raise ValueError('Konfigurasi verifikasi publik harus meta Google pada properti tetap.')
    token=value.get('value')
    if token=='':return None
    if not isinstance(token,str) or not re.fullmatch(r'[A-Za-z0-9_-]{8,300}',token):raise ValueError('Nilai metatag publik Google tidak valid.')
    return value

def load_public(path):
    return None if not path.exists() else validate_public(json.loads(path.read_text(encoding='utf-8')))

def import_export(file):
    export=json.loads(Path(file).read_text(encoding='utf-8'));raw=export.get('canonical_artifact_json');artifact=export.get('artifact')
    if export.get('schema_version')!=1 or export.get('property_id')!=PROPERTY or export.get('source')!='owner_provided_google_public_verification':raise ValueError('Ekspor artefak pemilik tidak sesuai properti/sumber.')
    if not isinstance(raw,str) or hashlib.sha256(raw.encode('utf-8')).hexdigest()!=export.get('artifact_sha256') or json.loads(raw)!=artifact:raise ValueError('Hash byte artefak pemilik tidak cocok.')
    if not isinstance(artifact,dict) or set(artifact)!={'method','value','provided_by_google'} or artifact.get('provided_by_google') is not True:raise ValueError('Metatag publik asli dari pemilik diperlukan.')
    public=validate_public({'property_id':PROPERTY,'method':artifact.get('method'),'value':artifact.get('value')})
    if public is None:raise ValueError('Ekspor pemilik tidak boleh memasang token kosong.')
    destination=ROOT/'content/google-verification.json';destination.write_text(json.dumps(public,ensure_ascii=False,indent=2,sort_keys=True),encoding='utf-8')
    return {'property_id':PROPERTY,'method':'html_meta','saved':str(destination.relative_to(ROOT)),'google_ownership':'not_checked'}

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--export',type=Path,required=True);args=parser.parse_args()
    try:print(json.dumps(import_export(args.export)))
    except (ValueError,OSError,KeyError) as error:parser.exit(1,str(error)+'\n')
