# Gera o site da Lá de Fora (site/index.html + site/img/*.webp)
import json, os, re, glob, html
from PIL import Image

ROOT = os.path.dirname(os.path.abspath(__file__))
SITE = os.path.join(ROOT, 'site'); IMG = os.path.join(SITE, 'img')
os.makedirs(IMG, exist_ok=True)

DET = json.load(open('/home/claude/det.json'))
PRE = json.load(open('/home/claude/pricing/precos.json'))
SEM = json.load(open('/home/claude/pricing/seminovos.json'))
PE = json.load(open('/home/claude/fotos/pe/items.json'))
BOTTLE = {34, 36, 37, 39, 40, 41, 43, 44, 45}

def short(n):
    n = re.sub(r'^(Celular |Notebook |Tablet |Relógio |Fone de Ouvido |Perfume |Caixa de Som |Drone |Placa de Vídeo |Teclado |Mouse |Filmadora |Câmera Digital |Processador |Roteador Wireless |Controle )', '', n)
    n = n.replace('Apple MacBook', 'MacBook').replace('Apple iPad', 'iPad').replace('Apple iPhone', 'iPhone').replace(' Bluetooth', '').replace('Eau de Parfum', 'EDP').replace('Eau de Toilette', 'EDT')
    n = re.sub(r' 2026 Apple (M5 Pro|M5|A18 Pro) / Memória (\d+GB) / SSD (\w+) / ([\d.]+)"', lambda m: f' {m.group(1)} {m.group(2)}/{m.group(3)} {m.group(4).replace(".", ",")}"', n)
    n = re.sub(r' Dual Chip| Global| - RAM 8GB| 4G| PCI-Express| Óptico| USB$', '', n)
    n = re.sub(r'(Notebook )?(Lenovo LOQ|Acer Nitro V 16) .*?/ (RTX \d+).*', lambda m: f'{m.group(2)} {m.group(3)}', n)
    n = re.sub(r' (\d+)MM', r' \1mm', n); n = n.replace(' seminovo grade A', '')
    n = re.sub(r'\s+', ' ', n)
    return n.strip()

CAT = {'iPhone': 'iphone', 'iPhone seminovo': 'seminovo', 'MacBook': 'mac', 'iPad': 'mac', 'Apple Watch / AirPods': 'watch',
       'Perfumes': 'perfume', 'Caixa de som JBL': 'jbl', 'Videogames': 'games', 'Drones': 'games',
       'Placa de vídeo': 'pc', 'Processadores': 'pc', 'SSD / Armazenamento': 'pc', 'Periféricos PC': 'pc', 'Notebooks': 'pc',
       'Smartphones Android': 'mais', 'Câmeras': 'mais', 'Smartwatch': 'mais', 'Eletrônicos diversos': 'mais'}

done = {}
def pimg(i):
    """imagem de produto: recorte com transparência quando houver, senão foto de fundo branco"""
    key = f'b{i:03d}' if (isinstance(i, int) and i in BOTTLE) else (i if isinstance(i, str) else f'{i:03d}')
    if key in done: return done[key]
    cut = f'/home/claude/fotos/cut/{key}.png'; raw = f'/home/claude/fotos/raw/{key}.png'
    src, mode = (cut, 'cut') if os.path.exists(cut) else (raw, 'raw')
    im = Image.open(src); im.thumbnail((640, 640))
    if mode == 'raw': im = im.convert('RGB')
    name = f'p{key}.webp'
    if not os.path.exists(os.path.join(IMG, name)): im.save(os.path.join(IMG, name), quality=84, method=4)
    done[key] = (name, mode); return done[key]

def specs(i):
    if not isinstance(i, int): return []
    out = []
    for s in DET[i]['specs'][:9]:
        if s.startswith('Marca:'): continue
        s = s if len(s) < 150 else s[:147].rsplit(' ', 1)[0] + '…'
        out.append(s)
    return out[:7]

prods = []
for r in PRE:
    if r['status'] == 'nao compensa' or 'Swap' in r['nome']: continue
    im, mode = pimg(r['i'])
    sp = specs(r['i'])
    if r['i'] == 7: sp = ['Versão com chip físico + eSIM'] + sp
    prods.append(dict(id=f"e{r['i']}", n=short(r['nome']), c=CAT[r['cat']], p=r['preco'], img=im, m=mode, s=sp, t='enc'))
for k, r in enumerate(SEM):
    im, mode = pimg(r['i'])
    prods.append(dict(id=f's{k}', n=short(r['nome']), c='seminovo', p=r['preco'], img=im, m=mode,
                      s=['Seminovo grade A', 'Por encomenda, chega na próxima leva'], t='enc'))
for k, r in enumerate(PE):
    name = f'pe{k:02d}.webp'
    if not os.path.exists(os.path.join(IMG, name)): im = Image.open(r['img']); im.thumbnail((720, 720)); im.save(os.path.join(IMG, name), quality=82, method=4)
    nome = r['nome'] + (f" ({r['extra']})" if r.get('extra') else '')
    cat = {'perfumes': 'perfumes', 'bolsas': 'bolsas', 'relogios': 'relogios', 'esportivos': 'esportivos', 'short': 'esportivos'}[r['cat']]
    prods.append(dict(id=f'pe{k}', b=r['marca'], n=nome, c=cat, p=int(r['preco'].replace('.', '')), img=name, m='photo', s=[], t='pe',
                      o={'Camera Crossbody preta, com acessórios': 1200, 'Mochila Los Angeles Monogram marrom': 850, 'Mochila preta Monograma 4G': 850}.get(r['nome'])))

# imagens do hero
hero = {}
for key in ['000', 'b034', '028', '030']:
    if not os.path.exists(os.path.join(IMG, f'h{key}.webp')): im = Image.open(f'/home/claude/fotos/cut/{key}.png'); im.thumbnail((900, 900)); im.save(os.path.join(IMG, f'h{key}.webp'), quality=86, method=4)

DATA = json.dumps(prods, ensure_ascii=False, separators=(',', ':'))
tpl = open(os.path.join(ROOT, 'site_template.html'), encoding='utf-8').read()
open(os.path.join(SITE, 'index.html'), 'w', encoding='utf-8').write(tpl.replace('/*DATA*/[]', DATA))
print(len(prods), 'produtos;', len(os.listdir(IMG)), 'imagens')
