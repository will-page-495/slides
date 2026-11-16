"""Build slides + Metricool manifest for drafted videos in a date range.
Usage: python3 code/run_week.py --docs DIR --from 2026-11-16 --to 2026-11-22 [--slots 12:00,18:00]
DIR = folder of exported calendar video docs (ArtifactData list -> out_dir .../videos).
Writes slides/<date>-s<slot>/NN_*.jpg and slides/manifest_<from>_<to>.json
"""
import json,sys,os,re,glob,argparse,unicodedata
ROOT=os.environ.get('TRIPFLUX_ROOT','/home/claude/slides'); os.environ['TRIPFLUX_ROOT']=ROOT
sys.path.insert(0,ROOT+'/code')
import render2 as R, slidetext as S
D=ROOT+'/data/'; PH=ROOT+'/photos/'
picks=json.load(open(D+'picks.json')); A=json.load(open(D+'aesthetic.json'))
BAN={'Santorini/f6_312.jpg','Zakynthos/f5_091.jpg'}|set(json.load(open(D+'banned.json')))
cov=json.load(open(D+'covers.json'))
match=json.load(open(D+'photo_match.json')); fold={(h['city'],h['country']):h['folder'] for h in match['have']}
sid=json.load(open(D+'site_ids.json'))
RAW='https://raw.githubusercontent.com/will-page-495/slides/main/'
norm=lambda x:''.join(c for c in unicodedata.normalize('NFD',x) if unicodedata.category(c)!='Mn').lower()
def have(p): return os.path.exists(PH+p)
def folder(x):
    return fold.get((x['city'],x['country'])) or next((f for (c,co),f in fold.items() if norm(c)==norm(x['city'])),None)
def pick_cover(name,doc,used):
    c=cov.get(name,{}).get('cover')
    if c and have(c): return c
    fs={folder(x) for x in doc['destinations']}
    best=None
    for p,a in A.items():
        if p in used or p in BAN or not have(p) or a['scale']>1.4: continue
        sc=3*min(a['col'],120)/120+1.2*(1-abs(a['lum']-135)/135)+(1.5 if p.split('/')[0] in fs else 0)
        if best is None or sc>best[0]: best=(sc,p)
    return best[1]
def final_photo(doc,used):
    fs=[folder(x) for x in doc['destinations']]
    alts=[p for p,a in A.items() if p.split('/')[0] in fs and p not in used and p not in BAN and have(p) and a['scale']<=1.4]
    return max(alts,key=lambda p:min(A[p]['col'],120)) if alts else fs[0]+'/'+picks[fs[0]]
def build(name,doc,outdir):
    os.makedirs(outdir,exist_ok=True); files=[]; used=set()
    c=pick_cover(name,doc,used); used.add(c)
    R.render_title(PH+c,doc['title'],f'{outdir}/01_cover.jpg'); files.append(f'01_cover.jpg')
    for i,x in enumerate(doc['destinations']):
        f=folder(x); ph=f+'/'+picks[f]; used.add(ph)
        fn=f"{i+2:02d}_{re.sub('[^A-Za-z]','',norm(x['city']))}.jpg"
        R.render(PH+ph,S.blocks_from_custom(x['custom']),f'{outdir}/{fn}'); files.append(fn)
    blue=(0,172,255)
    blocks=[dict(text='Which one are you booking?\nComment below 👇',size=42),
            dict(text='Prices exclude flights\nFull guides and prices\nwww.TripFlux.co\n(link in bio)',size=34,bg=blue,fg=(255,255,255),maxw=450)]
    fn=f'{len(doc["destinations"])+2:02d}_final.jpg'; R.render(PH+final_photo(doc,used),blocks,f'{outdir}/{fn}'); files.append(fn)
    return files
def slug(t): return re.sub('-+','-',re.sub('[^a-z0-9]+','-',norm(t).replace("'",''))).strip('-')
ap=argparse.ArgumentParser(); ap.add_argument('--docs',required=True); ap.add_argument('--from',dest='a',required=True); ap.add_argument('--to',dest='b',required=True)
ap.add_argument('--min-time',default=''); ap.add_argument('--ignore-metricool',action='store_true')
a=ap.parse_args()
docs=[]
for f in glob.glob(a.docs+'/*.json'):
    d=json.load(open(f)); n=os.path.basename(f)[:-5]
    if d.get('status')=='drafted' and a.a<=d['date']<=a.b and (a.ignore_metricool or not d.get('metricool')): docs.append((d['date'],d['slot'],n,d))
docs.sort(key=lambda x:(x[0],x[1]))
man=[];problems=[]
for date,slot,n,d in docs:
    when=f"{date}T{'12:00' if slot==0 else '18:00'}:00"
    if a.min_time and when<a.min_time: problems.append((n,'in the past, skipped')); continue
    miss=[x['city'] for x in d['destinations'] if not folder(x) or not have((folder(x) or '')+'/'+picks.get(folder(x) or '','x'))]
    if miss: problems.append((n,'missing photos: '+', '.join(miss))); continue
    out=f'{ROOT}/slides/{date}-s{slot}-{n}'
    files=build(n,d,out)
    tags=' '.join(d['hashtags'].split()[:5]); fix=lambda t: re.sub(r'\b1 nights\b','1 night',t)
    man.append(dict(doc=n,date=date,slot=slot,when=when,title=d['title'],tiktok_text=fix(d['captions']['tiktok'])+'\n\n'+tags,ig_text=fix(d['captions']['instagram'])+'\n\n'+tags,
        media=[RAW+f"slides/{date}-s{slot}-{n}/{f}" for f in files],
        dest_ids=[sid.get(x['city']+'|'+x['country']) for x in d['destinations']],slug=slug(d['title']),published_on=date))
json.dump(dict(videos=man,problems=problems),open(f'{ROOT}/slides/manifest_{a.a}_{a.b}.json','w'),ensure_ascii=False,indent=1)
print(len(man),'videos built; problems:',problems)
