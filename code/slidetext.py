import re
def blocks_from_custom(custom, BLUE=(0,172,255)):
    L=[x for x in custom.split('\n') if x.strip()!='']
    head,tag=L[0],L[1]; rest=L[2:]
    out=[dict(text=head,size=42),dict(text=tag,size=34)]
    i=0
    while i<len(rest):
        ln=rest[i]
        if ln.startswith('Budget'):
            ln=re.sub(r'^Budget:?\s*','Budget: ',ln); ln=re.sub(r'\b1 nights\b','1 night',ln); out.append(dict(text=ln,size=34))
        elif ln.startswith('Things to do'):
            items=[]; i+=1
            while i<len(rest) and rest[i].lstrip().startswith('•'): items.append(rest[i].strip()); i+=1
            out.append(dict(text='Things to do:\n'+'\n'.join(items),size=34)); continue
        elif ln.startswith('Where to stay'):
            out.append(dict(text='Where to stay:\n'+ln.split(':',1)[1].strip(),size=34))
        elif '@' in ln and 'TripFlux' in ln:
            cta=ln.split('@')[0].strip()
            out.append(dict(text=f'{cta} @\nwww.TripFlux.co\n(link in bio)',size=34,bg=BLUE,fg=(255,255,255),maxw=450))
        else: out.append(dict(text=ln,size=34))
        i+=1
    return out
