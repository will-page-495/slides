from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageOps
import re
W,H=1080,1440
import os as _os
_R=_os.environ.get('TRIPFLUX_ROOT','/home/claude/slides')
EMOJI='/usr/share/fonts/truetype/noto/NotoColorEmoji.ttf'
SERIF='/usr/share/fonts/truetype/liberation/LiberationSerif-Bold.ttf'
if not _os.path.exists(EMOJI): EMOJI=_R+'/assets/NotoColorEmoji.ttf'
if not _os.path.exists(SERIF): SERIF=_R+'/assets/LiberationSerif-Bold.ttf'
BLUE=(0,172,255)
import os
ROOT=os.environ.get('TRIPFLUX_ROOT','/home/claude/slides')
LOGO=ROOT+'/assets/logo.png'
MARGIN=7
LOGO_H=74; LOGO_BOTTOM=70
EMO=re.compile('\\s*([\U0001F300-\U0001FAFF\u2600-\u27BF])$')
FLAG=re.compile('^([\U0001F1E6-\U0001F1FF]{2})\\s*')
_fc={}
def font(size):
    if size not in _fc: _fc[size]=ImageFont.truetype(SERIF,size)
    return _fc[size]
def wrap(f,text,maxw):
    out=[]
    for para in text.split('\n'):
        cur=''
        for w in para.split(' '):
            t=(cur+' '+w).strip()
            if f.getlength(t)<=maxw or not cur: cur=t
            else: out.append(cur); cur=w
        out.append(cur)
    return out
CROPS={  # fractional (left, top, right, bottom) to cut watermarks/overlays out
 'Cordoba/b05_16.jpg':(0,0,1,0.90),'Bucharest/f5_169.jpg':(0.04,0,1,1),'Mykonos/b08_09.jpg':(0,0,1,0.95),
 'Kyoto/f5_111.jpg':(0,0,1,0.95),'Fes/f5_142.jpg':(0,0,0.95,0.95),'Perast/f5_138.jpg':(0,0,1,0.95),
 'Ubud/b11_17.jpg':(0,0,1,0.88),'Vilnius/f3_043.jpg':(0.05,0,1,1)}
from PIL import ImageEnhance, ImageStat
def enhance(im, scale):
    hsv=im.convert('HSV'); s_mean=ImageStat.Stat(hsv.split()[1]).mean[0]/255
    l=ImageStat.Stat(im.convert('L')); mean=l.mean[0]; sd=l.stddev[0]
    out=im
    if sd<55: out=Image.blend(out,ImageOps.autocontrast(out,cutoff=0.4),0.5)
    if mean<105: out=ImageEnhance.Brightness(out).enhance(min(1.15,1+(105-mean)/300))
    sat=1.15 if s_mean<0.30 else 1.08 if s_mean<0.45 else 1.0
    if sat>1: out=ImageEnhance.Color(out).enhance(sat)
    if scale>1.2: out=out.filter(ImageFilter.UnsharpMask(radius=1.2,percent=60,threshold=3))
    return out
def fit_photo(photo):
    im=Image.open(photo) if isinstance(photo,str) else photo
    key='/'.join(str(photo).split('/')[-2:]) if isinstance(photo,str) else None
    im=ImageOps.exif_transpose(im).convert('RGB')
    if key in CROPS:
        l,t,r_,b=CROPS[key]; im=im.crop((round(l*im.width),round(t*im.height),round(r_*im.width),round(b*im.height)))
    r=max(W/im.width,H/im.height)
    im=im.resize((max(W,round(im.width*r)),max(H,round(im.height*r))),Image.LANCZOS)
    x0=(im.width-W)//2; y0=(im.height-H)//2
    return enhance(im.crop((x0,y0,x0+W,y0+H)),r)
def logo_mark(height):
    lg=Image.open(LOGO).convert('RGB')
    # white artwork on blue: alpha from how far a pixel is from the blue
    r,g,b=lg.split()
    a=r.point(lambda v: max(0,min(255,int((v-10)*255/235))))
    mark=Image.new('RGBA',lg.size,(255,255,255,0)); mark.putalpha(a)
    mark=mark.crop(mark.getbbox())
    return mark.resize((round(mark.width*height/mark.height),height),Image.LANCZOS)
def add_logo(im,variant):
    if variant=='badge':      # blue rounded square, top right
        s=118; S=4
        badge=Image.new('RGBA',(s*S,s*S),(0,0,0,0)); ImageDraw.Draw(badge).rounded_rectangle([0,0,s*S-1,s*S-1],radius=26*S,fill=BLUE+(255,))
        badge=badge.resize((s,s),Image.LANCZOS)
        m=logo_mark(round(s*0.52)); badge.alpha_composite(m,((s-m.width)//2,(s-m.height)//2))
        im.paste(badge,(W-s-40,150),badge)
    elif variant=='mark':     # white logo with soft shadow, top left above the text
        m=logo_mark(78); sh=Image.new('RGBA',m.size,(0,0,0,0)); sh.putalpha(m.split()[3].point(lambda v:int(v*0.55)))
        sh=sh.filter(ImageFilter.GaussianBlur(5))
        im.paste((0,0,0),(46,62),sh); im.paste(m,(42,58),m)
    elif variant=='bottom':   # white logo with soft shadow, bottom centre
        m=logo_mark(LOGO_H); x=(W-m.width)//2; y=H-LOGO_BOTTOM-m.height
        sh=Image.new('RGBA',m.size,(0,0,0,0)); sh.putalpha(m.split()[3].point(lambda v:int(v*0.6)))
        sh=sh.filter(ImageFilter.GaussianBlur(5))
        im.paste((0,0,0),(x+3,y+4),sh); im.paste(m,(x,y),m)
    return im
MAXW_BOX=1080
def split_emo(ln):
    m=EMO.search(ln)
    return (ln[:m.start()],m.group(1)) if m else (ln,None)
def emo_img(ch,h):
    e=Image.new('RGBA',(300,160),(0,0,0,0)); ImageDraw.Draw(e).text((0,0),ch,font=ImageFont.truetype(EMOJI,109),embedded_color=True)
    e=e.crop(e.getbbox()); return e.resize((round(e.width*h/e.height),h),Image.LANCZOS)
def render(photo,blocks,out=None,left=30,maxw=372,gap=24,padx=13,pady=6,radius=10,logo=None,check=True):
    """blocks: list of dicts {text,size,bg,fg}. Raises if any text is not fully covered by its box."""
    from PIL import ImageChops
    im=fit_photo(photo) if not (isinstance(photo,Image.Image) and photo.size==(W,H)) else photo.copy()
    laid=[]
    for b in blocks:
        size=b.get('size',34); f=font(size); pitch=round(size*1.13)
        t=b['text']; m=FLAG.match(t); flag=m.group(1) if m else None
        if m: t=t[m.end():]
        fw=round(size*1.2) if flag else 0
        mw=b.get('maxw',maxw)
        lines=wrap(f,t,mw-fw) if flag else wrap(f,t,mw)
        laid.append(dict(b=b,f=f,size=size,pitch=pitch,flag=flag,fw=fw,lines=lines,h=len(lines)*pitch+2*pady))
    total=sum(l['h'] for l in laid)+gap*(len(laid)-1)
    y=(H-total)//2
    if logo=='bottom':
        limit=H-LOGO_BOTTOM-LOGO_H-36
        if y+total>limit: y=max(60,limit-total)
    S=4; pad=40
    for l in laid:
        f=l['f']; asc,desc=f.getmetrics()
        y0=y-pad; hh=l['h']+2*pad
        mask=Image.new('L',(MAXW_BOX*S,hh*S),0); md=ImageDraw.Draw(mask)
        tm=Image.new('L',(MAXW_BOX,hh),0); td=ImageDraw.Draw(tm)
        pos=[]
        for i,ln in enumerate(l['lines']):
            off=l['fw'] if i==0 and l['flag'] else 0
            ty=y+pady+i*l['pitch']; base=ty+(l['pitch']-(asc+desc))//2+1
            txt,emo=split_emo(ln); ew=round(l['size']*0.95) if emo else 0
            gx0,gy0,gx1,gy1=f.getbbox(txt or ' ')
            lw=off+max(f.getlength(txt),gx1)+ew
            lx=left if l['b'].get('align')!='center' else round((W-lw-2*padx)/2)
            top=ty-(pady if i==0 else 0); bot=ty+l['pitch']+(pady if i==len(l['lines'])-1 else 0)
            top=min(top,base+gy0-MARGIN); bot=max(bot,base+gy1+MARGIN)
            md.rectangle([lx*S,(top-y0)*S,round((lx+lw+2*padx)*S),(bot-y0)*S],fill=255)
            td.text((lx+padx+off,base-y0),txt,font=f,fill=255)
            pos.append((txt,lx+padx+off,base,ty,emo,f.getlength(txt)))
        mask=mask.filter(ImageFilter.GaussianBlur(radius*S*0.6)).point(lambda v:255 if v>128 else 0).resize((MAXW_BOX,hh),Image.LANCZOS)
        if check:
            grown=tm.filter(ImageFilter.MaxFilter(9)).point(lambda v:255 if v>40 else 0)
            bad=ImageChops.subtract(grown,mask.point(lambda v:255 if v>200 else 0))
            if bad.getbbox(): raise ValueError('text not fully covered: '+l['lines'][0][:30])
        im.paste(Image.new('RGB',(MAXW_BOX,hh),l['b'].get('bg',(255,255,255))),(0,y0),mask)
        d=ImageDraw.Draw(im)
        for i,(ln,x,base,ty,emo,tw) in enumerate(pos):
            if emo:
                eh=round(l['size']*0.8); e=emo_img(emo,eh); im.paste(e,(round(x+tw+l['size']*0.15),round(ty+(l['pitch']-eh)/2)+2),e)
            if i==0 and l['flag']:
                e=Image.new('RGBA',(300,160),(0,0,0,0)); ImageDraw.Draw(e).text((0,0),l['flag'],font=ImageFont.truetype(EMOJI,109),embedded_color=True)
                e=e.crop(e.getbbox()); fh=round(l['size']*0.66); e=e.resize((round(e.width*fh/e.height),fh),Image.LANCZOS)
                im.paste(e,(x-l['fw'],round(ty+(l['pitch']-fh)/2)+2),e)
            d.text((x,base),ln,font=f,fill=l['b'].get('fg',(0,0,0)))
        y+=l['h']+gap
    if logo: add_logo(im,logo)
    if out: im.save(out) if out.endswith('.png') else im.save(out,quality=95,subsampling=0)
    return im

BAD_END={"You've",'Cheap','Hidden','Winter','Short','Solo','Long','Christmas','Look','That','The','A','Are','Your','Shockingly','Surprisingly','Romantic','Couples','Heard','Never','Than','Much','6','You','Actually','Can','Of'}
GOOD_START={'That','To','to','in','In','With','with','But','for','For','You','Than','Hidden','Winter','Christmas','Solo','Short','Long','Weekend','Honeymoon','City','Island','Adventure','Part','Edition'}
def balanced(f,text,maxw):
    words=text.split(); n=len(words)
    best=None
    import math
    start=min(4,max(1,math.ceil(n/3)))
    ed=None
    if 'Edition' in words:
        e=words.index('Edition'); ed=e-1
        if ed>0 and words[ed] in ('Sun','Markets','Gems','Travel','Haul','Weekend','Trip'): ed-=1
    for k in list(range(start,min(5,n)+1)):
        # choose breaks minimising the widest line, for k lines
        import itertools
        for cuts in itertools.combinations(range(1,n),k-1):
            idx=(0,)+cuts+(n,); lines=[' '.join(words[idx[i]:idx[i+1]]) for i in range(k)]
            wmax=max(f.getlength(x) for x in lines)
            if wmax>maxw: continue
            bad=sum(1 for x in lines[:-1] if x.split()[-1] in BAD_END)+sum(2 for c in cuts if ed is not None and ed<c<n)
            bad+=sum(1 for c in cuts if words[c-1] in ('for','in','to') and words[c][:2]=='20')
            good=sum(1 for x in lines[1:] if x.split()[0] in GOOD_START)+sum(1 for c in cuts if c==ed)
            score=(0, wmax/10+60*bad-25*good+40*(k-start)+(80 if any(len(x.split())==1 and x.split()[0] in BAD_END|{'for','in','to','But','That','Than','Are'} for x in lines) else 0))
            if best is None or score<best[0]: best=(score,lines)
        if best and k>=start+1: break
    return best[1] if best else wrap(f,text,maxw)
def render_title(photo,title,out=None,size=94,maxw=920,logo='bottom',stroke=6):
    im=fit_photo(photo) if not (isinstance(photo,Image.Image) and photo.size==(W,H)) else photo.copy()
    f=font(size); lines=balanced(f,title,maxw); pitch=round(size*1.12)
    total=len(lines)*pitch; y=round(H*0.505-total/2)
    d=ImageDraw.Draw(im)
    for i,ln in enumerate(lines):
        w=f.getlength(ln); x=(W-w)/2
        d.text((x,y+i*pitch),ln,font=f,fill=(255,255,255),stroke_width=stroke,stroke_fill=(0,0,0))
    if logo: add_logo(im,logo)
    if out: im.save(out)
    return im
