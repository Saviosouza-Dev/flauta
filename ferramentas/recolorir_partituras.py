"""Troca a tinta das partituras já geradas pelas cores atuais (tokens pauta-*), sem precisar do LilyPond.
Uso: python3 recolorir_partituras.py ../partituras"""
import os,sys
M={'#2a1e14':'#161b26','#3b2a1b':'#161b26','#2f5a3a':'#1f6a4a','#b0362a':'#b3261e'}
root=sys.argv[1]; n=0
for d in [root, os.path.join(root,'m')]:
    for fn in os.listdir(d):
        if not fn.endswith('.svg'): continue
        p=os.path.join(d,fn); s=open(p,encoding='utf-8').read(); o=s
        for k,v in M.items(): s=s.replace(k,v).replace(k.upper(),v)
        if s!=o:
            with open(p,'w',encoding='utf-8',newline='\n') as f: f.write(s)
            n+=1
print('recoloridos',n)
