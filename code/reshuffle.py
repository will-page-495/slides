import importlib.util,json,glob,collections,random,re,unicodedata
spec=importlib.util.spec_from_file_location('g','gen2.py');g=importlib.util.module_from_spec(spec);spec.loader.exec_module(g)
random.seed(2026)
norm=lambda x:''.join(c for c in unicodedata.normalize('NFD',x) if unicodedata.category(c)!='Mn').lower().strip()
pm=json.load(open('photo_match.json'))
havecity={norm(h['city']) for h in pm['have']}
banned=set()
def hasphoto(d): return norm(d['city']) in havecity or (d['id']=='bali' and 'ubud' in havecity)
HAVE=[d for d in g.DL if hasphoto(d)]
WEAK={'Piešťany','Hévíz','Lake Balaton','Poiana Brașov','Špindlerův Mlýn','Trenčín','Timisoara','Kaunas','Varna','Ulcinj','Bansko','Zakopane','Corralejo','Puno','Sinaia','Brno','Wrocław','Plovdiv','Bratislava','Nuremberg','Sofia','Bucharest','Kochi','Agadir','Lima','Kutaisi','Padua','Šibenik','Kathmandu'}
RM={'wadirum','la-paz','uyuni'}
STRONG=[d for d in HAVE if d['id'] not in RM and d['city'] not in WEAK and d['cc']!='BO']
print('pool have',len(HAVE),'strong',len(STRONG))
byk={(d['city'],d['country']):d for d in g.DL}
byc={norm(d['city']):d for d in g.DL}
plans={f"plan-d{g.positions[p][0]:02d}-s{g.positions[p][1]}":(p,sp,t) for p,sp,t,_ in g.plans}
docs={}
for f in glob.glob('live6/videos/plan-*.json'):
    n=f.split('/')[-1][:-5]; docs[n]=json.load(open(f))
todo=sorted([n for n,d in docs.items() if d.get('status')=='drafted' and d['date']>='2026-11-16'],key=lambda n:(docs[n]['date'],docs[n]['slot']))
print(len(todo),'drafted from today')
usage=collections.Counter(); where=collections.defaultdict(list)
order={n:i for i,n in enumerate(todo)}
def ids_of(d):
    out=[]
    for x in d['destinations']:
        k=byk.get((x['city'],x['country'])) or byc.get(norm(x['city']))
        out.append(k)
    return out
for n in todo:
    for k in ids_of(docs[n]):
        if k and hasphoto(k): usage[k['id']]+=1; where[k['id']].append(order[n])
changes=[];newdocs={};FALL=[]
for n in todo:
    d=docs[n]; rows=ids_of(d); p,sp,t=plans[n]
    bad=[i for i,k in enumerate(rows) if k is None or not hasphoto(k)]
    if not bad: continue
    keep=[k for i,k in enumerate(rows) if i not in bad]
    cc=collections.Counter(k['cc'] for k in keep)
    pos=order[n]
    for i in bad:
        def ok(c): return sp['flt'](c) and c not in keep and cc[c['cc']]<2 and not(sp['fam']=='more-romantic' and sp['extra']['hook']=='Paris' and c['cc']=='FR') and not(c['cc']=='JO' and c['id']!='petra')
        cands=[c for c in STRONG if ok(c)] or [c for c in HAVE if ok(c)]
        if not cands:
            relax=lambda c: c not in keep and cc[c['cc']]<2 and ('r' in c['tags'] or 'l' in c['tags'] or 'h' in c['tags'])
            cands=[c for c in STRONG if relax(c)] or [c for c in HAVE if c not in keep and cc[c['cc']]<2]
            FALL.append((n,sp['edition']))
        assert cands,(n,sp['base'],sp['edition'])
        def sc(c):
            v=-usage[c['id']]*6+random.random()*3
            if any(abs(pos-q)<14 for q in where[c['id']]): v-=10
            if sp['fam'] in('cheap-couples','looks-expensive','more-romantic') and 'r' not in c['tags'] and 'l' not in c['tags']: v-=3
            return v
        c=max(cands,key=sc); keep.append(c); cc[c['cc']]+=1; usage[c['id']]+=1; where[c['id']].append(pos)
    keep=sorted(keep,key=lambda x:x['ex'])
    doc,name=g.build(p,sp,d['title'] if False else t,keep); assert name==n
    doc['notes']=doc['notes'].replace('5 or 6 places','6 places')
    for k in('date','slot','status','title','cover','part','seriesId','example','posted','saves','shares','views47','url','verdict'):
        if k in d: doc[k]=d[k]
    # re-title captions to live title
    doc['captions']['tiktok']=doc['captions']['tiktok'].replace(t,d['title'],1)
    assert 800<=len(doc['captions']['tiktok'])<=1000,(n,len(doc['captions']['tiktok']))
    newdocs[n]=doc; changes.append((n,d['date'],d['slot'],[rows[i]['city'] if rows[i] else d['destinations'][i]['city'] for i in bad],[c['city'] for c in keep if c not in rows]))
print(len(changes),'videos changed')
for c in changes[:12]: print(c)
json.dump(newdocs,open('reshuffled.json','w'),ensure_ascii=False)
print('fallbacks',FALL)
print('max reuse',usage.most_common(5))
