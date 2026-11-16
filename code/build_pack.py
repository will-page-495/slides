#!/usr/bin/env python3
"""Build the daily pack page. Usage: build_pack.py --manifests M1 M2 --dates D1 D2 [--skip docid,..] --out DIR
Writes DIR/index.html, DIR/t/<folder>/NN.jpg thumbnails, DIR/files.json (published path -> source path)."""
import argparse,json,os,html,io,base64,zipfile
from PIL import Image
ap=argparse.ArgumentParser(); ap.add_argument('--manifests',nargs='+',required=True); ap.add_argument('--dates',required=True)
ap.add_argument('--skip',default=''); ap.add_argument('--out',required=True); ap.add_argument('--root',default='/home/claude/slides')
ap.add_argument('--today',default='')
a=ap.parse_args(); dates=a.dates.split(','); skip=set(filter(None,a.skip.split(',')))
vids={}
for mf in a.manifests:
    m=json.load(open(mf)); v=m['videos'] if isinstance(m,dict) else m
    for x in v:
        if x['date'] in dates and x['doc'] not in skip: vids[x['doc']]=x
vids=sorted(vids.values(),key=lambda x:(x['date'],x['slot']))
os.makedirs(a.out,exist_ok=True); files={}; data=[]
for x in vids:
    items=[]
    for u in x['media']:
        rel=u.split('/main/',1)[1]; src=os.path.join(a.root,rel); folder=rel.split('/')[-2]; fn=rel.split('/')[-1]
        full='img/%s/%s'%(folder,fn); th='t/%s/%s'%(folder,fn)
        os.makedirs(os.path.dirname(os.path.join(a.out,full)),exist_ok=True)
        Image.open(src).convert('RGB').save(os.path.join(a.out,full),quality=88,optimize=True); files[full]=os.path.join(a.out,full)
        im=Image.open(src).convert('RGB'); im.thumbnail((300,400)); bio=io.BytesIO(); im.save(bio,'JPEG',quality=76); th='data:image/jpeg;base64,'+base64.b64encode(bio.getvalue()).decode()
        items.append({'full':full,'th':th,'name':fn})
    folder=items[0]['full'].split('/')[1]
    title=x['title']
    data.append({'doc':x['doc'],'date':x['date'],'time':x['when'][11:16],'title':title,'tiktok':x['tiktok_text'],'insta':x['ig_text'],'slides':items,'folder':folder})
tpl=open(os.path.join(os.path.dirname(os.path.abspath(__file__)),'pack_template.html')).read()
open(os.path.join(a.out,'index.html'),'w').write(tpl.replace('/*DATA*/[]',json.dumps(data,ensure_ascii=False)))
json.dump(files,open(os.path.join(a.out,'files.json'),'w'))
print(len(data),'videos',len(files),'files')
