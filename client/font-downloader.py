#!/usr/bin/env python3

from pathlib import Path
from dataclasses import dataclass
import re
import json
import subprocess as S
from textwrap import dedent

FAMILY_FIX_MAP = {
    'Source Sans Pro': 'Source Sans 3',
}

SERVICE = 'https://gwfh.mranftl.com/api/fonts'

RAW_DATA = json.loads(S.run(['curl', SERVICE], stdout=S.PIPE).stdout.decode('utf-8'))


ROOT_DIR = Path(__file__).parent.resolve()
DIST_DIR = ROOT_DIR / 'node_modules' / 'bootswatch' / 'dist'
OUT_DIR  = ROOT_DIR / 'src' / 'assets' / 'fonts'
TTF_DIR  = OUT_DIR / 'ttf'
WOFF_DIR  = OUT_DIR / 'woff'
WOFF2_DIR  = OUT_DIR / 'woff2'

data = {}

@dataclass
class Family:
    id: str
    name: str
    orig_name: str
    weights_normal: list[str]
    weights_italic: list[str]

def parse_family(raw: str) -> Family:
    m = re.match(r'([^:@]+)(:([^@]+))?(@(.*))?', raw)
    if not m:
        return None

    name = FAMILY_FIX_MAP.get(m.group(1), m.group(1))
    id = ''
    for i in RAW_DATA:
        if i['family'] == name:
            id = i['id']
            break

    types = m.group(3).split(',') if m.group(3) else []
    raw_weights = m.group(5).split(';') if m.group(5) else []

    weights_normal = []
    weights_italic = []

    if types and raw_weights:
        ital_idx = types.index('ital') if 'ital' in types else -1
        wght_idx = types.index('wght')
        for w in raw_weights:
            w = w.split(',')
            if ital_idx >= 0 and w[ital_idx] == '1':
                weights_italic += [w[wght_idx]]
            else:
                weights_normal += [w[wght_idx]]
    else:
        weights_normal += ['400']

    return Family(
        id,
        name,
        m.group(1),
        weights_normal,
        weights_italic,
    )


for i in [OUT_DIR, TTF_DIR, WOFF_DIR, WOFF2_DIR]:
    i.mkdir(parents=True, exist_ok=True)


# Parse
for i in DIST_DIR.glob('*/_bootswatch.scss'):
    theme = i.parent.name
    raw = i.read_text()
    for l in raw.splitlines():
        l = l.strip()
        if not l.startswith("$web-font-path"):
            continue

        url = re.sub(r'^.*?"|".*?$', '', l)
        family = re.search(r'\?family=(.*?)&', url).group(1)
        family = family.replace('+', ' ')
        families = family.split('|')
        families = [parse_family(x) for x in families]

        data[theme] = {
            'url': url,
            'family': families,
        }


family_data = {}

# Generate
for theme, d in data.items():
    css_file = OUT_DIR / f'{theme}-fonts.css'
    raw_css = ''
    family: Family
    for family in d['family']:
        if family.id not in family_data:
            family_data[family.id] = json.loads(S.run(['curl', f'{SERVICE}/{family.id}'], stdout=S.PIPE).stdout.decode('utf-8'))

        for variant in family_data[family.id]['variants']:
            fontStyle = variant['fontStyle']
            fontWeight = variant['fontWeight']

            if fontStyle == 'normal' and fontWeight not in family.weights_normal:
                continue
            elif fontStyle == 'italic' and fontWeight not in family.weights_italic:
                continue

            # Download font
            ttf = TTF_DIR / f'{family.id}-{fontStyle}-{fontWeight}.ttf'
            woff = WOFF_DIR / f'{family.id}-{fontStyle}-{fontWeight}.woff'
            woff2 = WOFF2_DIR / f'{family.id}-{fontStyle}-{fontWeight}.woff2'
            if not ttf.exists():
                S.run(['curl', '-o', ttf.as_posix(), variant['ttf']])
            if not woff.exists():
                S.run(['curl', '-o', woff.as_posix(), variant['woff']])
            if not woff2.exists():
                S.run(['curl', '-o', woff2.as_posix(), variant['woff2']])

            raw_css += dedent(f'''
                /* {family.id} */
                @font-face {{
                    font-display: swap; /* Check https://developer.mozilla.org/en-US/docs/Web/CSS/@font-face/font-display for other options. */
                    font-family: '{family.orig_name}';
                    font-style: {fontStyle};
                    font-weight: {fontWeight};
                    src:
                        url('./{WOFF2_DIR.name}/{woff2.name}') format('woff2'),
                        url('./{WOFF_DIR.name}/{woff.name}') format('woff'),
                        url('./{TTF_DIR.name}/{ttf.name}') format('ttf'),
                    ;
                }}
            ''')

    css_file.write_text(raw_css, encoding='utf-8', newline='\n')
