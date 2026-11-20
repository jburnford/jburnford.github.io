"""Build jimclifford.ca's homepage (index.html) in the tube-map design.

Content lives in homepage/source.html (the pre-2026 page markup: publications, projects,
talks, teaching, funding, timeline dots). Edit content there, then run:

    python3 homepage/build.py

The script writes index.html at the site root. It stops with an error if a correction below
no longer matches a title, or if two lines would be drawn on top of each other.
Design language: SSHA 2026 slides (Atkinson Hyperlegible Next, transit-map lines).
"""
import html, json, os, re, sys
from bs4 import BeautifulSoup

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, 'source.html')
OUT = os.path.join(HERE, '..', 'index.html')
soup = BeautifulSoup(open(SRC, encoding='utf-8').read(), 'html.parser')

def inner(el):
    return ''.join(str(c) for c in el.contents).strip() if el else ''

def txt(el):
    return el.get_text(' ', strip=True) if el else ''

esc = html.escape

# ------------------------------------------------------------------ lines
LINES = {  # key: (name, home row)
    'london':  ('Industrial London', 0),
    'ghost':   ('Ghost Acres', 2),
    'settler': ('Settler Colonialism', 3),
    'dh':      ('Digital Humanities', 1),
    'covid':   ('Health & Medicine', 4),
}
ROW_LABEL = {'Industrial London': 'london', 'Ghost Acres': 'ghost', 'Digital Humanities': 'dh',
             'Settler Colonialism': 'settler', 'Pandemic': 'covid'}
START = {'london': 2004, 'dh': 2008, 'ghost': 2011, 'settler': 2016, 'covid': 2011}

def norm(t):
    return re.sub(r'[^a-z]', '', html.unescape(t).lower())[:32]

# ------------------------------------------------------------------ publications
pubs = []
for li in soup.select('li.pub'):
    for np_ in li.select('.not-pr'):
        np_.insert_before(' · ')
    a = li.find('a', href=True)
    pubs.append({
        'year': int(re.sub(r'\D', '', txt(li.select_one('.yr')))[:4]),
        'tags': li['data-tags'].split(),
        'title': txt(li.h4),
        'authors': txt(li.select_one('.authors')),
        'venue': inner(li.select_one('.venue')),
        'venue_txt': txt(li.select_one('.venue')),
        'abstract': inner(li.select_one('.abstract')),
        'type': txt(li.select_one('.type')),
        'href': a['href'] if a else '',
    })

# works not yet on the live page (additions from Jim)
EXTRA_PUBS = [{
    'year': 2011, 'tags': ['london', 'dh', 'covid'], 'type': 'Dissertation',
    'title': 'A Wetland Suburb on the Edge of London: A Social and Environmental History of West Ham and the River Lea, 1855–1914',
    'authors': 'Clifford, J.',
    'venue': 'PhD dissertation · defended 20 January 2011 · the basis of <em>West Ham and the River Lea</em>',
    'venue_txt': 'PhD dissertation · defended 20 January 2011 · the basis of West Ham and the River Lea',
    'abstract': 'Examines the connections between ecological change on the wetlands where the River Lea meets the Thames Estuary '
                'and the development of a young suburb on the edge of London. As industry transformed the wetlands, socially '
                'marginalized people in West Ham suffered alongside the natural environment from pollution and flooding. '
                '<a href="https://jimclifford.ca/blog/disseration-defended.html">Defence post and full abstract &rarr;</a>',
    'href': 'https://jimclifford.ca/blog/disseration-defended.html',
}, {
    'year': 2004, 'tags': ['london'], 'type': 'MA Research Paper',
    'title': 'The Cultural Common Sense of East End London, Poverty, and the Social: Representations of Poverty in Late 1880s and 1890s London',
    'authors': 'Clifford, J.',
    'venue': 'Major Research Paper, MA in History, Wilfrid Laurier University · Knowledge Commons',
    'venue_txt': 'Major Research Paper, MA in History, Wilfrid Laurier University',
    'abstract': '',
    'href': 'https://doi.org/10.17613/0ngr-s213',
}, {
    'year': 2008, 'tags': ['london', 'dh'], 'type': 'Photo Essay',
    'title': "The Urban Periphery and the Rural Fringe: West Ham's Hybrid Landscape",
    'authors': 'Clifford, J.',
    'venue': '<em>Left History</em> 13, no. 1 (Spring/Summer 2008), special issue on environmental history',
    'venue_txt': 'Left History 13, no. 1 (Spring/Summer 2008)',
    'abstract': '',
    'href': 'https://lh.journals.yorku.ca/index.php/lh/article/view/24616',
}]
for ep in EXTRA_PUBS:
    k = next((i for i, p in enumerate(pubs) if p['year'] < ep['year']), len(pubs))
    pubs.insert(k, ep)

SHORT = [  # (title prefix, short station name)
    ('London Timber Consumption', 'London Timber Consumption'), ('Pandemic Politics', 'Pandemic Politics'),
    ('When Did the Great Acceleration', 'The Great Acceleration'), ('A Cypher Knowledge Graph', 'Imperial Territories Graph'),
    ('Thinking Through Forests', 'Thinking Through Forests'), ('Logging and Settlement', 'Logging and Settlement'),
    ('Mapping Commodity Histories', 'Mapping Commodity Histories'), ('Digital History Making', 'Digital History in a Crisis'),
    ('Virtual Reality in History', 'VR in History Education'), ("London's Soap Industry", "London's Soap Industry"),
    ('West Ham and the River Lea', 'West Ham and the River Lea'), ('Geoparsing History', 'Geoparsing History'),
    ('A Wetland Suburb', 'A Wetland Suburb (PhD)'),
    ('The Urban Periphery and the Rural', "West Ham's Hybrid Landscape"),
    ('British Ghost Acres and', 'British Ghost Acres'),
    ("Maitland's Moment", "Maitland's Moment"),
]
def short(t):
    n = norm(t)
    for k, v in SHORT:
        if n.startswith(norm(k)):
            return v
    return html.unescape(t).split(':')[0][:30]

# ------------------------------------------------------------------ timeline dots (singles)
singles = []
for row in soup.select('g.thread-row'):
    key = ROW_LABEL[txt(row.select_one('.thread-label'))]
    for c in row.select('circle.dot'):
        singles.append({'line': key, 'year': int(c['data-year']), 'title': c.get('data-title', ''),
                        'sub': c.get('data-sub', ''), 'href': c.get('data-href', '')})

# date corrections from Jim: the swipe map dates from about 2015 and was rebuilt in 2026
YEAR_FIX = {'londonsthcenturyindustrial': (2015, 'rebuilt 2026')}
_yhit = {k for k in YEAR_FIX for sg in singles if norm(sg['title']).startswith(k)}
if set(YEAR_FIX) - _yhit:
    sys.exit(f'YEAR_FIX keys matched no timeline station: {sorted(set(YEAR_FIX) - _yhit)}')
for sg in singles:
    for k, (yr, note) in YEAR_FIX.items():
        if norm(sg['title']).startswith(k):
            sg['year'] = yr
            sg['sub'] = (sg['sub'] + ' · ' if sg['sub'] else '') + note
# corrections from Jim: the book is digital and medical history, not ghost acres
TAG_FIX = {'westhamandtheriverlea': ['london', 'dh', 'covid'], 'londonssoapindustry': ['london', 'ghost', 'dh'],
           'virtualrealityinhistory': ['ghost', 'settler', 'dh'],
           'britishghostacres': ['ghost', 'dh']}
_hit = set()
for p in pubs:
    for k, v in TAG_FIX.items():
        if norm(p['title']).startswith(k):
            p['tags'] = v; _hit.add(k)
if set(TAG_FIX) - _hit:
    sys.exit(f'TAG_FIX keys matched no publication: {sorted(set(TAG_FIX) - _hit)}')
for ep in EXTRA_PUBS:   # single-line additions also become map stations
    if len(ep['tags']) == 1:
        singles.append({'line': ep['tags'][0], 'year': ep['year'], 'title': ep['title'],
                        'sub': f"{ep['type']} · {ep['venue_txt']}", 'href': ep['href']})
multi = [p for p in pubs if len(p['tags']) > 1]
multi_norm = [norm(p['title']) for p in multi]
def is_multi(t):
    n = norm(t)
    return any(m.startswith(n) or n.startswith(m) or m[:15] == n[:15] for m in multi_norm)
dropped = [s['title'] for s in singles if is_multi(s['title'])]
singles = [s for s in singles if not is_multi(s['title'])]
print('merged into interchanges:', dropped)

# ------------------------------------------------------------------ stations
stations = []   # each: lines, year, items[], kind ('ix' | 'single')
for p in multi:
    lines = sorted(set(p['tags']), key=lambda k: LINES[k][1])
    stations.append({'kind': 'ix', 'lines': lines, 'year': p['year'], 'label': short(p['title']),
                     'items': [{'title': p['title'], 'sub': f"{p['type']} · {p['venue_txt']}", 'href': p['href']}]})
# milestones that are not publications but still join lines (corrections from Jim)
MILESTONE_FIX = {'dlinnovationaward': (['ghost', 'settler'], 'Homesteaders Board Game'),
                 'londonsthcenturyindustrial': (['london', 'dh'], 'London Industry Swipe Map')}
_mhit = {k for k in MILESTONE_FIX for s in singles if norm(s['title']).startswith(k)}
if set(MILESTONE_FIX) - _mhit:
    sys.exit(f'MILESTONE_FIX keys matched no timeline station: {sorted(set(MILESTONE_FIX) - _mhit)}')
kept = []
for s in singles:
    hit = next((v for k, v in MILESTONE_FIX.items() if norm(s['title']).startswith(k)), None)
    if hit:
        lines, label = hit
        if not any(st['kind'] == 'ix' and st['label'] == label for st in stations):
            stations.append({'kind': 'ix', 'lines': sorted(lines, key=lambda k: LINES[k][1]), 'year': s['year'], 'label': label,
                             'items': [{'title': s['title'], 'sub': s['sub'], 'href': s['href']}]})
    else:
        kept.append(s)
singles = kept
merged = {}
for s in singles:
    k = (s['line'], s['year'])
    if k not in merged:
        merged[k] = {'kind': 'single', 'lines': [s['line']], 'year': s['year'], 'label': '', 'items': []}
        stations.append(merged[k])
    merged[k]['items'].append({'title': s['title'], 'sub': s['sub'], 'href': s['href']})

# ------------------------------------------------------------------ x layout: stretch busy years
SLOT, QUIET, Y0, Y1 = 42, 20, 2004, 2027
by_year = {}
for st in stations:
    by_year.setdefault(st['year'], []).append(st)
for y, sts in by_year.items():
    ix = sorted([s for s in sts if s['kind'] == 'ix'], key=lambda s: (sum(LINES[l][1] for l in s['lines']) / len(s['lines'])))
    slots = []  # list of sets of lines occupied
    for s in ix:
        s['slot'] = len(slots); slots.append(set(s['lines']))
    for s in [s for s in sts if s['kind'] == 'single']:
        l = s['lines'][0]
        for i, occ in enumerate(slots):
            if l not in occ:
                s['slot'] = i; occ.add(l); break
        else:
            s['slot'] = len(slots); slots.append({l})
    by_year[y] = (sts, len(slots))

# lay out x, stack the interchanges, then give extra room wherever a line has to move more
# than 45 degrees allows between two stations; repeat until nothing is too steep
HW = 11  # half-width of the flat run through a station
PAD, WIDEN = {}, {}
OCC = []   # (line, x1, x2, y): stretches where a line holds a stack slot, from the previous pass
for _pass in range(8):
    LEFT = 300
    year_x, x = {}, LEFT
    for y in range(Y0, Y1 + 1):
        n = by_year.get(y, ([], 0))[1]
        w = max(QUIET, n * SLOT) if n else {2018: 44, 2019: 44}.get(y, QUIET)
        x += PAD.get(y, 0)
        w += WIDEN.get(y, 0)
        year_x[y] = (x, w, n)
        x += w
    NOW_X = year_x[2027][0]
    WIDTH = x + 30
    for y, (sts, n) in ((y, v) for y, v in by_year.items()):
        x0, w, _ = year_x[y]
        for s in sts:
            s['x'] = x0 + (s['slot'] + 0.5) * (w / n)

    ROW, TOP_PAD = 48, 150
    def home(l):
        return TOP_PAD + LINES[l][1] * ROW
    GAP = 12

    # stack ys at interchanges: anchor on one participant's own track; the others take parallel
    # slots beside it, on the side they come from, nearest line closest (tube-map bundling)
    last = {}   # line -> (x, y) at its most recent station, to reserve slots still in use
    for s in sorted(stations, key=lambda s: s['x']):
        if s['kind'] != 'ix':
            s['ys'] = {s['lines'][0]: home(s['lines'][0])}
            last[s['lines'][0]] = (s['x'], home(s['lines'][0]))
            continue
        taken = {round(ly) for l, (lx, ly) in last.items()
                 if l not in s['lines'] and s['x'] - lx < 90 and abs(ly - home(l)) > 0.5}
        taken |= {round(oy) for (ol, x1, x2, oy) in OCC if ol not in s['lines'] and x1 - 30 < s['x'] < x2 + 30}
        hs = {l: home(l) for l in s['lines']}
        mean = sum(hs.values()) / len(hs)
        # anchor on the line with the most of its own stations nearby, so the others come to it
        busy = {l: sum(1 for o in stations if o is not s and l in o['lines'] and abs(o['year'] - s['year']) <= 2) for l in s['lines']}
        anchor = min(s['lines'], key=lambda l: (-busy[l], abs(hs[l] - mean), hs[l]))
        a = hs[anchor]
        s['anchor'] = anchor
        s['ys'] = {anchor: a}
        above = sorted([l for l in s['lines'] if hs[l] < a], key=lambda l: -hs[l])
        below = sorted([l for l in s['lines'] if hs[l] > a], key=lambda l: hs[l])
        for side, group in ((-1, above), (1, below)):
            k = 0
            for l in group:
                k += 1
                while round(a + side * k * GAP) in taken:
                    k += 1
                s['ys'][l] = a + side * k * GAP
        for l, y in s['ys'].items():
            last[l] = (s['x'], y)

    # a single station between two events where its line runs in the same bundle sits in the bundle
    for l in LINES:
        evs = sorted([s for s in stations if l in s['lines']], key=lambda s: s['x'])
        for k, s in enumerate(evs):
            if s['kind'] != 'single' or k == 0 or k == len(evs) - 1:
                continue
            yp, yn = evs[k - 1]['ys'][l], evs[k + 1]['ys'][l]
            if abs(yp - yn) < 0.5 and abs(yp - home(l)) > 0.5:
                s['ys'] = {l: yp}

    new_occ = []
    for l in LINES:
        evs = sorted([st for st in stations if l in st['lines']], key=lambda st: st['x'])
        for e1, e2 in zip(evs, evs[1:]):
            if abs(e1['ys'][l] - e2['ys'][l]) < 0.5 and abs(e1['ys'][l] - home(l)) > 0.5:
                new_occ.append((l, e1['x'], e2['x'], e1['ys'][l]))
    occ_changed = sorted((o[0], round(o[3])) for o in new_occ) != sorted((o[0], round(o[3])) for o in OCC)
    OCC = new_occ
    steep = occ_changed
    for l in LINES:
        evs = sorted([st for st in stations if l in st['lines']], key=lambda st: st['x'])
        for e1, e2 in zip(evs, evs[1:]):
            dy = abs(e1['ys'][l] - e2['ys'][l])
            need, have = 0.4 * dy + 2 * HW + 6, e2['x'] - e1['x']
            if dy > 0.5 and have < need - 0.5:
                steep = True
                if e1['year'] == e2['year']:
                    WIDEN[e2['year']] = WIDEN.get(e2['year'], 0) + (need - have) * by_year[e2['year']][1]
                else:
                    PAD[e2['year']] = PAD.get(e2['year'], 0) + (need - have)
    if not steep:
        break
print('layout passes:', _pass + 1, '| extra room by year:', {y: round(v) for y, v in sorted({**PAD, **WIDEN}.items())})

# ------------------------------------------------------------------ route each line

def route(l):
    evs = sorted([s for s in stations if l in s['lines']], key=lambda s: s['x'])
    h = home(l)
    y_start = h
    if START[l] < evs[0]['year']:
        start_x = year_x[START[l]][0] + 4
    else:
        start_x = evs[0]['x'] - HW - 4
        y_start = evs[0]['ys'][l]
    start_x = max(start_x, LEFT + 8)   # never run into the line names
    pts = [(start_x, y_start)]
    solid_end = NOW_X
    def go(xa, ya, xb, yb):
        dx, dy = xb - xa, yb - ya
        if dy == 0:
            pts.append((xb, yb)); return
        if abs(dy) >= dx:
            pts.append((xb, yb)); return
        mid = (xa + xb) / 2
        pts.append((mid - abs(dy) / 2, ya)); pts.append((mid + abs(dy) / 2, yb)); pts.append((xb, yb))
    for s in evs:
        y = s['ys'][l]
        xa, ya = pts[-1]
        xb = s['x'] - HW
        if xb < xa:
            xb = xa
        if abs(ya - y) < 0.5:
            pass  # same slot at both stations: stay side by side in the bundle
        elif ya != h and y != h and abs(ya - h) + abs(y - h) + 10 <= xb - xa:
            # return to home row between interchanges
            gap = xb - xa
            x1 = xa + (gap - abs(ya - h) - abs(y - h)) / 2
            pts.append((x1, ya)); pts.append((x1 + abs(ya - h), h))
            go(x1 + abs(ya - h), h, xb, y)
        else:
            go(xa, ya, xb, y)
        pts.append((s['x'] + HW, y))
    # back home, then to the end
    end_x = NOW_X - 6 if evs[-1]['year'] < 2027 else evs[-1]['x'] + HW + 14
    xa, ya = pts[-1]
    if ya != h and end_x - xa > abs(ya - h) + 4:
        go(xa, ya, xa + abs(ya - h) + 4, h)
    xa, ya = pts[-1]
    pts.append((max(end_x, xa), ya))
    # dedupe
    out = [pts[0]]
    for p in pts[1:]:
        if abs(p[0] - out[-1][0]) > 0.01 or abs(p[1] - out[-1][1]) > 0.01:
            out.append(p)
    return out, evs

def split_at(pts, xcut):
    """split polyline at x = xcut into (before, after)."""
    before, after = [pts[0]], []
    for a, b in zip(pts, pts[1:]):
        if after:
            after.append(b); continue
        if b[0] <= xcut:
            before.append(b); continue
        t = (xcut - a[0]) / (b[0] - a[0]) if b[0] != a[0] else 0
        c = (xcut, a[1] + t * (b[1] - a[1]))
        before.append(c); after = [c, b]
    return before, after

def d(pts):
    return 'M' + ' L'.join(f'{x:.1f},{y:.1f}' for x, y in pts)

svg = []
ORDER = ['covid', 'settler', 'ghost', 'dh', 'london']   # draw bottom rows first, so upper lines pass over
routes = {l: route(l) for l in LINES}
for l in ORDER:
    pts, evs = routes[l]
    solid, fut = split_at(pts, NOW_X)
    svg.append(f'<g class="ln-g" data-line="{l}">')
    svg.append(f'<path class="case" d="{d(solid)}"/>')
    svg.append(f'<path class="line l-{l}" d="{d(solid)}"/>')
    if len(fut) > 1:
        svg.append(f'<path class="line l-{l} future" d="{d(fut)}"/>')
    # terminus tick at start
    x0, y0 = pts[0]
    pass  # terminus ticks removed
    if not fut or len(fut) < 2:
        x1, y1 = solid[-1]
        pass  # terminus ticks removed
    # line name at its start
    name = LINES[l][0].upper()
    svg.append(f'<text class="lname l-{l}-t" x="{LEFT-14:.1f}" y="{home(l)+5:.1f}" text-anchor="end">{esc(name)}</text>')
    svg.append('</g>')

# NOW marker
NOW_MARK = True

# stations
data = []
hits = []
for i, s in enumerate(sorted(stations, key=lambda s: s['x'])):
    s['i'] = i
    ys = list(s['ys'].values())
    future = s['year'] >= 2027
    cls = 'st' + (' fut' if future else '')
    lines_attr = ' '.join(s['lines'])
    titles = [html.unescape(it['title']) for it in s['items']]
    aname = (f"{s['year']}: " + '; '.join(titles) + ' — ' + ', '.join(LINES[l][0] for l in s['lines']))
    if s['kind'] == 'ix':
        top, bot = min(ys) - 9, max(ys) + 9
        svg.append(f'<rect class="{cls} ix" data-i="{i}" data-lines="{lines_attr}" tabindex="0" role="button" aria-label="{esc(aname)}" x="{s["x"]-9:.1f}" y="{top:.1f}" width="18" height="{bot-top:.1f}" rx="9"/>')
        hits.append(f'<rect class="hit" data-i="{i}" x="{s["x"]-17:.1f}" y="{top-9:.1f}" width="34" height="{bot-top+18:.1f}" rx="17"/>')
    else:
        y = ys[0]
        r = 6.5 if len(s['items']) == 1 else 8
        svg.append(f'<circle class="{cls}" data-i="{i}" data-lines="{lines_attr}" tabindex="0" role="button" aria-label="{esc(aname)}" cx="{s["x"]:.1f}" cy="{y:.1f}" r="{r}"/>')
        hits.append(f'<circle class="hit" data-i="{i}" cx="{s["x"]:.1f}" cy="{y:.1f}" r="17"/>')
    data.append({'year': s['year'], 'lines': s['lines'], 'items': s['items']})

svg.extend(hits)

# interchange labels in tiers above and below the bundle, with leaders
def tw(t, size=19.5):
    return len(t) * size * 0.56
ix_sts = sorted([s for s in stations if s['kind'] == 'ix'], key=lambda s: s['x'])
tiers = {'up': [], 'down': []}
for k, s in enumerate(ix_sts):
    label = s['label']; yr = str(s['year'])
    w = tw(label) + tw(' ' + yr, 16)
    prefer = 'up' if min(s['ys'].values()) < TOP_PAD + 2 * ROW else 'down'
    placed = None
    for side in (prefer, 'down' if prefer == 'up' else 'up'):
        for t in range(9):
            if len(tiers[side]) <= t:
                tiers[side].append([])
            x0, x1 = s['x'] - 6, s['x'] - 6 + w
            if x1 > WIDTH - 10:
                x0, x1 = s['x'] + 6 - w, s['x'] + 6
            if all(x1 + 14 < a or x0 > b + 14 for a, b in tiers[side][t]):
                tiers[side][t].append((x0, x1)); placed = (side, t, x0); break
        if placed:
            break
    side, t, x0 = placed
    if side == 'up':
        ly = TOP_PAD - 38 - t * 29
        y_from = min(s['ys'].values()) - 9
    else:
        ly = TOP_PAD + 4 * ROW + 50 + t * 29
        y_from = max(s['ys'].values()) + 9
    svg.append(f'<line class="leader" x1="{s["x"]:.1f}" y1="{y_from:.1f}" x2="{s["x"]:.1f}" y2="{ly + (7 if side=="up" else -19):.1f}"/>')
    anchor_end = x0 < s['x'] - 7
    svg.append(f'<text class="slabel" data-i="{s["i"]}" x="{(s["x"]+6 if anchor_end else x0):.1f}" y="{ly:.1f}"'
               f'{" text-anchor=\"end\"" if anchor_end else ""}>{esc(s["label"])}<tspan class="yr"> {s["year"]}</tspan></text>')

# year axis
AX = TOP_PAD + 4 * ROW + 50 + max(len(tiers['down']), 1) * 29 + 18
for y in range(Y0, Y1 + 1):
    x0, w, n = year_x[y]
    show = y in (2004, 2008, 2012, 2016, 2020, 2022, 2024, 2025, 2026, 2027)
    svg.append(f'<line class="tick" x1="{x0:.1f}" y1="{AX-6}" x2="{x0:.1f}" y2="{AX}"/>')
    if show:
        svg.append(f'<text class="axt" x="{x0 + w/2:.1f}" y="{AX+16}" text-anchor="middle">{y}</text>'.replace(f'y="{AX+16}"', f'y="{AX+21}"'))
svg.append(f'<line class="axis" x1="{LEFT}" y1="{AX}" x2="{WIDTH-30:.1f}" y2="{AX}"/>')
svg.insert(0, f'<line class="now" x1="{NOW_X:.1f}" y1="{TOP_PAD-40}" x2="{NOW_X:.1f}" y2="{AX-4}"/>'
              f'<text class="nowt" x="{NOW_X-7:.1f}" y="{AX-9}" text-anchor="end">NOW</text>')
TOPY = TOP_PAD - 38 - (len(tiers['up']) - 1) * 29 - 36
HEIGHT = AX + 30 - TOPY
MAP = (f'<svg class="tube" viewBox="0 {TOPY:.0f} {WIDTH:.0f} {HEIGHT:.0f}" role="group" '
       f'aria-label="Research lines drawn as a transit map, 2004 to now. Each station is a work; select one for details.">' + ''.join(svg) + '</svg>')

# ------------------------------------------------------------------ other content
about = soup.select_one('#about .about-grid > div')
_md = soup.find('meta', attrs={'name': 'description'})
DESCRIPTION = _md['content'] if _md else 'Jim Clifford, Professor of History, University of Saskatchewan.'
portrait = soup.select_one('#about figure img')

def stats_line(stats_el, wip=False):
    if not stats_el:
        return ''
    spans = [sp for sp in stats_el.find_all('span', recursive=False)]
    stops = []
    for sp in spans:
        if 'wip-dot' in (sp.get('class') or []):
            continue
        strongs = sp.find_all('strong')
        if len(strongs) > 1:
            cur = None
            for node in sp.children:
                if getattr(node, 'name', None) == 'strong':
                    if cur:
                        stops.append((cur[0], cur[1].replace('·', '').strip()))
                    cur = [txt(node), '']
                elif cur is not None:
                    cur[1] += ' ' + (node.get_text(' ', strip=True) if hasattr(node, 'get_text') else str(node))
            if cur:
                stops.append((cur[0], cur[1].replace('·', '').strip()))
            continue
        st = sp.find('strong')
        num = txt(st) if st else ''
        if st:
            st.extract()
        stops.append((num, txt(sp)))
    if not stops and not wip:
        return ''
    if not wip and (len(stops) < 2 or not any(a for a, _ in stops)):
        return '<p class="plain">' + ' · '.join(esc((a + ' ' + b).strip()) for a, b in stops) + '</p>'
    n = len(stops) + (1 if wip else 0)
    cells = ''.join(f'<li><b>{esc(a)}</b><i></i><span>{esc(b)}</span></li>' for a, b in stops)
    if wip:
        cells += '<li class="build"><b></b><i></i><span>in progress</span></li>'
    return f'<ol class="stops{" wip" if wip else ""}" style="--n:{n}">{cells}</ol>'

def card(a):
    wip = 'proj-wip' in (a.get('class') or [])
    tag = txt(a.select_one('.tag'))
    title = inner(a.h4)
    p = inner(a.p)
    stats = stats_line(a.select_one('.stats'), wip)
    links = a.select_one('.links')
    if a.name == 'a':
        return (f'<a class="card{" wip" if wip else ""}" href="{esc(a["href"])}"><p class="lab">{esc(tag)}</p>'
                f'<h3>{title}</h3><p class="desc">{p}</p>{stats}</a>')
    lk = ''.join(f'<a href="{esc(x["href"])}">{esc(txt(x))}</a>' for x in links.find_all('a')) if links else ''
    return (f'<div class="card"><p class="lab">{esc(tag)}</p><h3>{title}</h3><p class="desc">{p}</p>{stats}'
            f'<p class="cardlinks">{lk}</p></div>')

proj_sec = soup.select_one('#projects')
proj_html = []
for el in proj_sec.find_all(['div'], recursive=False):
    cls = el.get('class') or []
    if 'proj-subhead' in cls:
        proj_html.append(f'<p class="sublab">{esc(txt(el.select_one(".proj-subhead-label")))}'
                         f'<span>{esc(txt(el.select_one(".proj-subhead-meta")))}</span></p>')
    elif 'proj-grid' in cls:
        proj_html.append('<div class="cards">' + ''.join(card(a) for a in el.find_all(['a', 'div'], class_='proj', recursive=False)) + '</div>')

talks = soup.select_one('#talks .proj-grid')
talks_html = '<div class="cards">' + ''.join(card(a) for a in talks.find_all(['a', 'div'], class_='proj', recursive=False)) + '</div>'

teach = []
for c in soup.select('#teaching .card'):
    h = c.h4
    a = h.find('a')
    teach.append(f'<a class="card" href="{esc(a["href"])}"><p class="lab">{esc(txt(c.select_one(".sub")))}</p>'
                 f'<h3>{esc(txt(h))}</h3><p class="desc">{inner(c.p)}</p></a>')

fund = []
for li in soup.select('#funding .funding-item'):
    t = li.select_one('.title')
    agencies = [txt(a) for a in t.select('.agency')]
    for a in t.select('.agency'):
        a.extract()
    role = txt(li.select_one('.role'))
    fund.append(f'<li class="{"pi" if role == "PI" else ""}"><span class="fy">{esc(txt(li.select_one(".yrs")))}</span><i></i>'
                f'<div><h3>{inner(t)}</h3>' + ''.join(f'<p>{esc(x)}</p>' for x in agencies) +
                f'</div><span class="role">{esc(role)}</span></li>')

contact = soup.select_one('#contact .contact-grid')

def pub_li(p):
    lines = sorted(set(p['tags']), key=lambda k: LINES[k][1])
    marker = 'ix' if len(lines) > 1 else 'one'
    chips = ''.join(f'<span class="lt l-{l}-t">{esc(LINES[l][0])}</span>' for l in lines)
    title = f'<a href="{esc(p["href"])}">{esc(p["title"])}</a>' if p['href'] else esc(p['title'])
    abstract = f'<details><summary>Abstract</summary><div>{p["abstract"]}</div></details>' if p['abstract'] else ''
    return (f'<li data-tags="{esc(" ".join(p["tags"]))}" style="--c: var(--{lines[0]})"><span class="py">{p["year"]}</span>'
            f'<i class="{marker}" style="--n:{len(lines)}"></i><div><h3>{title}</h3>'
            f'<p class="au">{esc(p["authors"])}</p><p class="ve">{p["venue"]}</p>'
            f'<p class="meta"><span class="ty">{esc(p["type"])}</span>{chips}</p>{abstract}</div></li>')

pubs_html = ''.join(pub_li(p) for p in pubs)
chips_html = ('<button class="chip on" data-f="all" aria-pressed="true">All lines</button>' +
              ''.join(f'<button class="chip" data-f="{k}" aria-pressed="false" style="--c: var(--{k})"><i></i>{esc(v[0])}</button>' for k, v in LINES.items()))
nix = sum(1 for st in stations if st['kind'] == 'ix')

SECTIONS = [('about', 'About'), ('publications', 'Publications'), ('projects', 'Digital Projects'),
            ('talks', 'Talks'), ('teaching', 'Teaching'), ('funding', 'Funding'), ('contact', 'Contact')]
nav = ''.join(f'<li><a href="#{k}" aria-label="{v}"><i></i><span>{v}</span></a></li>' for k, v in [('top', 'Overview')] + SECTIONS)

def head(n, lab, title):
    return f'<p class="label">{n:02d} · {esc(lab)}</p><h2>{esc(title)}</h2>'

page = f'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1"/>
<title>Jim Clifford — Digital &amp; Environmental Historian</title>
<meta name="description" content="{esc(DESCRIPTION)}"/>
<style>
@font-face {{ font-family: "Atkinson Next"; src: url("fonts/AtkinsonHyperlegibleNext-Regular.woff") format("woff"); font-weight: 400; }}
@font-face {{ font-family: "Atkinson Next"; src: url("fonts/AtkinsonHyperlegibleNext-Bold.woff") format("woff"); font-weight: 700; }}
:root {{
  --ground: #FDFCF9; --raised: #F6F4EE; --title: #22272B; --body: #404040; --second: #5C6166; --accent: #1F5F96; --rule: #D9D5CB;
  --neutral: #8C8880; --station: #FDFCF9; --ring: #22272B;
  --london: #A8462A; --ghost: #2F8F4A; --settler: #C99700; --dh: #1F5F96; --covid: #7B4FC4;
  --london-t: #A8462A; --ghost-t: #22753A; --settler-t: #7D6000; --dh-t: #1F5F96; --covid-t: #7B4FC4;
}}
html.dark {{
  --ground: #1C1B19; --raised: #24231F; --title: #E8DFCB; --body: #C4C3C0; --second: #9A9790; --accent: #6699D3; --rule: #3A3935;
  --neutral: #77746D; --station: #1C1B19; --ring: #E8DFCB;
  --london: #DC7559; --ghost: #6DBF7B; --settler: #E0B93A; --dh: #6699D3; --covid: #B195F0;
  --london-t: #DC7559; --ghost-t: #6DBF7B; --settler-t: #E0B93A; --dh-t: #6699D3; --covid-t: #B195F0;
}}
* {{ box-sizing: border-box; }}
html {{ scroll-behavior: smooth; }}
body {{ margin: 0; background: var(--ground); color: var(--body); font: 18px/1.5 "Atkinson Next", "Atkinson Hyperlegible", Arial, sans-serif; }}
a {{ color: var(--accent); text-decoration: none; }}
a:hover {{ text-decoration: underline; text-underline-offset: 3px; }}
b, strong {{ color: var(--title); font-weight: 700; }}
.page {{ display: grid; grid-template-columns: 250px minmax(0, 1fr); overflow-x: clip; max-width: 1440px; margin: 0 auto; }}

/* ---------- rail: the site as a line ---------- */
.rail {{ position: sticky; top: 0; height: 100vh; padding: 48px 28px 28px 40px; display: flex; flex-direction: column; }}
.rail .me {{ font-size: 22px; font-weight: 700; color: var(--title); margin: 0; }}
.rail .role {{ font-size: 14px; color: var(--second); margin: 2px 0 34px; line-height: 1.35; }}
.stops-nav {{ list-style: none; margin: 0; padding: 0; position: relative; }}
.stops-nav::before {{ content: ""; position: absolute; left: 7px; top: 10px; bottom: 10px; width: 5px; border-radius: 3px; background: var(--accent); }}
.stops-nav li {{ position: relative; }}
.stops-nav a {{ display: flex; align-items: center; gap: 16px; padding: 7px 0; color: var(--second); font-size: 16px; font-weight: 700; }}
.stops-nav a:hover {{ color: var(--title); text-decoration: none; }}
.stops-nav i {{ width: 19px; height: 19px; flex: none; border-radius: 50%; background: var(--station); border: 3px solid var(--ring); position: relative; transition: transform .15s; }}
.stops-nav a.on {{ color: var(--title); }}
.stops-nav a.on i {{ background: var(--ring); box-shadow: 0 0 0 3px var(--station) inset; transform: scale(1.25); }}
.rail .foot {{ margin-top: auto; font-size: 14px; color: var(--second); line-height: 1.5; }}
.mode {{ margin-top: 14px; font: 700 13px "Atkinson Next", Arial, sans-serif; letter-spacing: .1em; text-transform: uppercase; color: var(--second);
  background: none; border: 2px solid var(--rule); border-radius: 20px; padding: 6px 14px; cursor: pointer; }}
.mode:hover {{ color: var(--title); border-color: var(--title); }}

main {{ padding: 0 56px 120px 40px; min-width: 0; }}
section {{ padding: 88px 0 0; }}
.label {{ margin: 0 0 6px; font-size: 15px; font-weight: 700; letter-spacing: .12em; text-transform: uppercase; color: var(--second); }}
h2 {{ margin: 0 0 34px; font-size: 40px; line-height: 1.15; font-weight: 700; color: var(--title); letter-spacing: -.01em; }}
h3 {{ margin: 0; font-size: 19px; line-height: 1.3; color: var(--title); font-weight: 700; }}

/* ---------- hero ---------- */
.hero {{ padding-top: 56px; }}
.hero h1 {{ font-size: 76px; line-height: 1.02; margin: 4px 0 18px; color: var(--title); letter-spacing: -.015em; }}
.hero .sub {{ font-size: 28px; line-height: 1.3; margin: 0 0 22px; max-width: 26ch; }}
.hero .who {{ font-size: 19px; margin: 0; color: var(--second); }}
.hero .who b {{ color: var(--accent); }}
.hero .links {{ display: flex; flex-wrap: wrap; gap: 6px 22px; margin: 16px 0 0; font-weight: 700; font-size: 16px; }}
.mapwrap {{ margin: 54px 0 0; }}
.mapwrap .label {{ display: flex; justify-content: space-between; gap: 20px; flex-wrap: wrap; }}
.mapwrap .label span {{ font-weight: 400; letter-spacing: .04em; text-transform: none; }}
.mapscroll {{ overflow-x: auto; margin: 10px -20px 0; padding: 0 20px; }}
svg.tube {{ display: block; width: 100%; min-width: 1080px; height: auto; font-family: "Atkinson Next", Arial, sans-serif; }}
.tube .line {{ fill: none; stroke-width: 7; stroke-linecap: round; stroke-linejoin: round; transition: opacity .2s; }}
.tube .case {{ fill: none; stroke: var(--ground); stroke-width: 15; stroke-linecap: round; stroke-linejoin: round; }}
.tube .future {{ stroke-dasharray: 2 11; }}
.tube .term {{ stroke-width: 7; stroke-linecap: round; }}
{''.join(f'.tube .l-{k}{{stroke: var(--{k});}} .l-{k}-t{{fill: var(--{k}-t); color: var(--{k}-t);}}' for k in LINES)}
.tube .lname {{ font-size: 19px; font-weight: 700; letter-spacing: .08em; }}
.tube .st {{ fill: var(--station); stroke: var(--ring); stroke-width: 3; cursor: pointer; transition: opacity .2s; }}
.tube .st:hover, .tube .st.sel {{ fill: var(--ring); }}
.tube .st.fut {{ stroke-dasharray: 3 3; }}
.tube .hit {{ fill: transparent; pointer-events: all; cursor: pointer; }}
.tube .st:focus-visible {{ outline: 3px solid var(--accent); outline-offset: 3px; }}
.skip {{ position: absolute; left: -9999px; }}
.skip:focus {{ position: static; display: inline-block; margin: 8px 0 0; font-weight: 700; }}
.scrollhint {{ display: none; margin: 6px 0 0; font-size: 14px; color: var(--second); }}
.mapwrap.overflow .scrollhint {{ display: block; }}
@media (prefers-reduced-motion: reduce) {{
  html {{ scroll-behavior: auto; }}
  *, *::before, *::after {{ transition: none !important; animation: none !important; }}
}}
.tube .slabel {{ font-size: 19.5px; font-weight: 700; fill: var(--title); cursor: pointer; transition: opacity .2s; }}
.tube .slabel .yr {{ font-weight: 400; fill: var(--second); font-size: 16px; }}
.tube .leader {{ stroke: var(--neutral); stroke-width: 1; stroke-dasharray: 1 3; }}
.tube .now {{ stroke: var(--neutral); stroke-width: 1.5; stroke-dasharray: 5 5; }}
.tube .nowt {{ font-size: 15px; font-weight: 700; letter-spacing: .14em; fill: var(--second); }}
.tube .axis, .tube .tick {{ stroke: var(--rule); stroke-width: 1.5; }}
.tube .axt {{ font-size: 16px; fill: var(--second); }}
.tube.focus .ln-g:not(.hot) .line, .tube.focus .ln-g:not(.hot) .term {{ opacity: .14; }}
.tube.focus .st:not(.hot), .tube.focus .slabel:not(.hot), .tube.focus .ln-g:not(.hot) .lname {{ opacity: .25; }}
.mapwrap {{ position: relative; }}
.mapnote {{ margin: 14px 0 0; font-size: 15px; color: var(--second); max-width: 80ch; }}
.pop {{ position: absolute; z-index: 10; width: 360px; max-width: calc(100% - 8px); padding: 14px 40px 14px 18px; background: var(--ground);
  border: 1px solid var(--rule); border-left: 5px solid var(--c, var(--accent)); border-radius: 4px;
  box-shadow: 0 10px 28px rgba(0,0,0,.16), 0 2px 6px rgba(0,0,0,.08); }}
html.dark .pop {{ box-shadow: 0 10px 28px rgba(0,0,0,.5); }}
.pop[hidden] {{ display: none; }}
.pop .py {{ font-size: 20px; font-weight: 700; color: var(--accent); line-height: 1.1; margin: 0 0 6px; text-align: left; padding: 0; }}
.pop h3 {{ font-size: 16px; line-height: 1.3; }}
.pop h3 a {{ color: var(--title); }}
.pop h3 a:hover {{ color: var(--accent); }}
.pop p {{ margin: 3px 0 0; font-size: 14px; color: var(--second); }}
.pop .item + .item {{ margin-top: 10px; padding-top: 10px; border-top: 1px solid var(--rule); }}
.pop .lines {{ margin-top: 10px; display: flex; gap: 12px; flex-wrap: wrap; }}
.pop .x {{ position: absolute; top: 8px; right: 8px; width: 28px; height: 28px; border: 0; border-radius: 50%; background: none;
  color: var(--second); font: 700 20px/1 "Atkinson Next", Arial, sans-serif; cursor: pointer; }}
.pop .x:hover {{ background: var(--raised); color: var(--title); }}
.key {{ display: flex; flex-wrap: wrap; gap: 8px 26px; margin: 14px 0 0; font-size: 14px; color: var(--second); }}
.key svg {{ vertical-align: -5px; margin-right: 6px; }}
.lt {{ font-size: 12px; font-weight: 700; letter-spacing: .08em; text-transform: uppercase; }}

/* ---------- about ---------- */
.about {{ display: grid; grid-template-columns: minmax(0, 1fr) 300px; gap: 56px; align-items: start; }}
.about p {{ margin: 0 0 18px; max-width: 64ch; }}
.about figure {{ margin: 0; }}
.about img {{ width: 100%; aspect-ratio: 4/5; object-fit: cover; border-radius: 4px; border: 1px solid var(--rule); display: block; }}
.about figcaption {{ font-size: 14px; color: var(--second); margin-top: 8px; }}

/* ---------- publications: one long line, interchanges where threads meet ---------- */
.chips {{ display: flex; flex-wrap: wrap; gap: 8px; margin: 0 0 30px; }}
.chip {{ font: 700 14px "Atkinson Next", Arial, sans-serif; color: var(--title); background: none; border: 2px solid var(--rule);
  border-radius: 22px; padding: 6px 14px 6px 10px; cursor: pointer; display: inline-flex; align-items: center; gap: 8px; }}
.chip i {{ width: 22px; height: 6px; border-radius: 3px; background: var(--c); }}
.chip[data-f="all"] {{ padding-left: 14px; }}
.chip.on {{ border-color: var(--title); background: var(--title); color: var(--ground); }}
.count {{ font-size: 14px; color: var(--second); align-self: center; margin-left: 6px; }}
.publist {{ list-style: none; margin: 0; padding: 0; position: relative; }}
.publist::before {{ content: ""; position: absolute; left: 95px; top: 12px; bottom: 12px; width: 5px; border-radius: 3px; background: var(--rule); }}
.publist li {{ display: grid; grid-template-columns: 70px 50px minmax(0, 1fr); gap: 0 0; padding: 0 0 30px; position: relative; }}
.publist li.hide {{ display: none; }}
.py {{ font-size: 21px; font-weight: 700; color: var(--title); text-align: right; padding-right: 4px; line-height: 1.25; }}
.publist i {{ justify-self: center; margin-top: 2px; background: var(--station); border: 3px solid var(--ring); position: relative; z-index: 1; }}
.publist i.one {{ width: 20px; height: 20px; border-radius: 50%; box-shadow: 0 0 0 4px var(--ground); }}
.publist i.ix {{ width: 20px; height: calc(20px + (var(--n) - 1) * 12px); border-radius: 10px; box-shadow: 0 0 0 4px var(--ground); }}
.publist h3 a {{ color: var(--title); }}
.publist h3 a:hover {{ color: var(--accent); }}
.publist p {{ margin: 3px 0 0; font-size: 16px; }}
.publist .au {{ color: var(--body); }}
.publist .ve {{ color: var(--second); }}
.publist .meta {{ display: flex; flex-wrap: wrap; gap: 4px 16px; margin-top: 8px; }}
.publist .ty {{ font-size: 12px; font-weight: 700; letter-spacing: .08em; text-transform: uppercase; color: var(--second); }}
details {{ margin-top: 6px; font-size: 16px; }}
summary {{ cursor: pointer; color: var(--accent); font-weight: 700; font-size: 14px; }}
details div {{ margin-top: 6px; max-width: 70ch; color: var(--body); }}

/* ---------- cards with numbers as stations (slide 4) ---------- */
.sublab {{ margin: 40px 0 18px; font-size: 15px; font-weight: 700; letter-spacing: .12em; text-transform: uppercase; color: var(--title); display: flex; gap: 16px; align-items: baseline; flex-wrap: wrap; }}
.sublab:first-of-type {{ margin-top: 0; }}
.sublab span {{ font-weight: 400; letter-spacing: .02em; text-transform: none; color: var(--second); }}
.cards {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); gap: 18px; }}
.card {{ display: flex; flex-direction: column; padding: 22px 24px 20px; background: var(--raised); border-radius: 4px; color: var(--body); border: 1px solid transparent; }}
a.card:hover {{ text-decoration: none; border-color: var(--rule); }}
a.card:hover h3 {{ color: var(--accent); }}
.card .lab {{ margin: 0 0 8px; font-size: 13px; font-weight: 700; letter-spacing: .12em; text-transform: uppercase; color: var(--second); }}
.card .desc {{ margin: 8px 0 0; font-size: 16px; line-height: 1.45; }}
.card .cardlinks {{ margin: 14px 0 0; display: flex; flex-direction: column; gap: 4px; font-weight: 700; font-size: 15px; }}
.stops {{ list-style: none; margin: auto 0 0; padding: 22px 0 0; display: grid; grid-template-columns: repeat(var(--n), minmax(0, 1fr)); position: relative; }}
.stops::before {{ content: ""; position: absolute; left: calc(50% / var(--n)); right: calc(50% / var(--n)); top: calc(22px + 1.25em + 7px); height: 5px; border-radius: 3px; background: var(--accent); }}
.stops.wip::before {{ background: none; border-top: 5px dotted var(--neutral); height: 0; right: calc(50% / var(--n)); }}
.stops li {{ display: flex; flex-direction: column; align-items: center; text-align: center; position: relative; min-width: 0; }}
.stops b {{ font-size: 17px; color: var(--accent); line-height: 1.25em; height: 1.25em; white-space: nowrap; }}
.stops i {{ width: 17px; height: 17px; border-radius: 50%; background: var(--station); border: 3px solid var(--ring); margin: 3px 0 4px; position: relative; z-index: 1; }}
.stops span {{ font-size: 13px; color: var(--second); line-height: 1.25; padding: 0 2px; }}
.stops .build i {{ border-color: var(--neutral); border-style: dashed; }}
.stops .build span {{ font-weight: 700; color: var(--second); }}
.card.wip .stops b {{ color: var(--second); }}
.card .plain {{ margin: auto 0 0; padding-top: 16px; font-size: 13px; font-weight: 700; letter-spacing: .1em; text-transform: uppercase; color: var(--accent); }}

/* ---------- funding ---------- */
.fund {{ list-style: none; margin: 0; padding: 0; position: relative; }}
.fund::before {{ content: ""; position: absolute; left: 115px; top: 12px; bottom: 12px; width: 5px; border-radius: 3px; background: var(--rule); }}
.fund li {{ display: grid; grid-template-columns: 90px 50px minmax(0, 1fr) auto; padding: 0 0 22px; align-items: start; }}
.fund .fy {{ font-weight: 700; color: var(--title); text-align: right; font-size: 17px; padding-top: 1px; }}
.fund i {{ justify-self: center; width: 18px; height: 18px; border-radius: 50%; background: var(--station); border: 3px solid var(--ring); position: relative; z-index: 1; box-shadow: 0 0 0 4px var(--ground); margin-top: 3px; }}
.fund li.pi i {{ background: var(--ring); box-shadow: 0 0 0 3px var(--station) inset, 0 0 0 4px var(--ground); }}
.fund h3 {{ font-size: 17px; }}
.fund h3 a {{ color: var(--title); }}
.fund p {{ margin: 2px 0 0; font-size: 15px; color: var(--second); }}
.fund .role {{ font-size: 12px; font-weight: 700; letter-spacing: .1em; text-transform: uppercase; color: var(--second); border: 2px solid var(--rule); border-radius: 14px; padding: 2px 10px; margin-left: 16px; white-space: nowrap; }}
.fund li.pi .role {{ color: var(--ground); background: var(--accent); border-color: var(--accent); }}

/* ---------- contact ---------- */
.contact {{ display: grid; grid-template-columns: 1fr 1fr; gap: 0 56px; margin: 0; }}
.contact dt {{ font-size: 13px; font-weight: 700; letter-spacing: .12em; text-transform: uppercase; color: var(--second); margin-top: 14px; }}
.contact dd {{ margin: 4px 0 0; }}
.contact dd[style] {{ font-size: inherit !important; }}
footer {{ margin-top: 80px; padding-top: 18px; border-top: 1px solid var(--rule); font-size: 14px; color: var(--second); }}

/* the station line stays down the left side at every width; nothing is pinned across the top */
@media (max-width: 1100px) {{
  .page {{ grid-template-columns: 200px minmax(0, 1fr); }}
  .rail {{ padding: 36px 16px 24px 24px; }}
  .rail .role {{ display: none; }}
  .rail .me {{ margin-bottom: 26px; }}
  main {{ padding: 0 28px 100px 16px; }}
  .hero h1 {{ font-size: 60px; }}
  .hero .sub {{ font-size: 24px; }}
  .about {{ grid-template-columns: 1fr; }}
  .about figure {{ max-width: 280px; }}
}}
@media (max-width: 700px) {{
  .page {{ grid-template-columns: 50px minmax(0, 1fr); }}
  .rail {{ padding: 22px 0 18px 14px; align-items: flex-start; }}
  .rail .me {{ display: none; }}
  .stops-nav a {{ padding: 12px 14px 12px 0; min-width: 44px; }}
  .stops-nav a span {{ position: absolute; left: 34px; white-space: nowrap; background: var(--title); color: var(--ground); font-size: 13px;
    padding: 3px 9px; border-radius: 12px; opacity: 0; pointer-events: none; transition: opacity .15s; z-index: 3; }}
  .stops-nav a:hover span, .stops-nav a:focus span {{ opacity: 1; }}
  .rail .foot {{ font-size: 0; }}
  .rail .foot a, .rail .foot br {{ display: none; }}
  .mode {{ font-size: 0; width: 32px; height: 32px; padding: 0; margin: 0; border-radius: 50%; border: 3px solid var(--ring);
    background: linear-gradient(90deg, var(--ring) 50%, transparent 50%); }}
  main {{ padding: 0 16px 80px 12px; }}
  .hero {{ padding-top: 28px; }}
  .hero .label {{ font-size: 13px; }}
  .hero h1 {{ font-size: 44px; }}
  .hero .sub {{ font-size: 21px; }}
  h2 {{ font-size: 32px; }}
  section {{ padding-top: 64px; }}
  .cards {{ grid-template-columns: 1fr; }}
  .contact {{ grid-template-columns: 1fr; }}
  .publist::before {{ left: 71px; }}
  .publist li {{ grid-template-columns: 50px 42px minmax(0, 1fr); }}
  .py {{ font-size: 17px; }}
  .fund li {{ grid-template-columns: 62px 36px minmax(0, 1fr); }}
  .fund::before {{ left: 78px; }}
  .fund .fy {{ font-size: 14px; }}
  .fund .role {{ grid-column: 3; justify-self: start; margin: 6px 0 0; }}
}}
</style>
<script>
(function() {{
  var s = null; try {{ s = localStorage.getItem('tube-mode'); }} catch (e) {{}}
  if (s === 'dark' || (!s && matchMedia('(prefers-color-scheme: dark)').matches)) document.documentElement.classList.add('dark');
}})();
</script>
</head>
<body>
<div class="page">
  <aside class="rail">
    <p class="me">Jim Clifford</p>
    <p class="role">Professor of History<br/>University of Saskatchewan</p>
    <ol class="stops-nav" id="nav">{nav}</ol>
    <div class="foot">
      <a href="mailto:jim.clifford@usask.ca">jim.clifford@usask.ca</a><br/>Treaty 6 Territory · Saskatoon
      <br/><button class="mode" id="mode" type="button" aria-pressed="false">Dark mode</button>
    </div>
  </aside>

  <main>
    <section class="hero" id="top">
      <p class="label">Digital &amp; environmental historian · University of Saskatchewan</p>
      <h1>Jim Clifford</h1>
      <p class="sub">Mapping the distant landscapes that sustained industrial cities.</p>
      <p class="who"><b>Co-Editor, Historical Methods</b> · Historical GIS Lab · Dyslexic</p>
      <p class="links">
        <a href="https://scholar.google.ca/citations?user=RBhCqv0AAAAJ">Google Scholar</a>
        <a href="https://orcid.org/0000-0003-2004-5161">ORCID</a>
        <a href="https://hgis.usask.ca/">HGIS Lab</a>
        <a href="https://www.tandfonline.com/journals/vhim20">Historical Methods</a>
      </p>

      <div class="mapwrap">
        <p class="label">Research lines, 2004 – now <span>Interchanges are works that bring lines together · select any station</span></p>
        <a class="skip" href="#about">Skip the research map</a>
        <div class="mapscroll">{MAP}</div>
        <p class="scrollhint">Scroll sideways for earlier years.</p>
        <div class="pop" id="pop" role="dialog" aria-label="Station details" hidden></div>
        <p class="mapnote"><b>{nix} interchanges</b> where research lines meet. Each is a publication or project that belongs to two or three lines. Busy years are stretched, as a tube map stretches the city centre.</p>
        <p class="key">
          <span><svg width="22" height="22"><circle cx="11" cy="11" r="6" fill="var(--station)" stroke="var(--ring)" stroke-width="3"/></svg>publication, project or milestone</span>
          <span><svg width="20" height="30"><rect x="2" y="2" width="16" height="26" rx="8" fill="var(--station)" stroke="var(--ring)" stroke-width="3"/></svg>interchange: one work, several lines</span>
          <span><svg width="40" height="22"><path d="M4,11 L36,11" stroke="var(--neutral)" stroke-width="6" stroke-dasharray="2 9" stroke-linecap="round"/></svg>forthcoming</span>
        </p>
      </div>
    </section>

    <section id="about">
      {head(2, 'Biography', 'About')}
      <div class="about">
        <div>{inner(about)}</div>
        <figure><img src="{esc(portrait["src"])}" alt="Jim Clifford" width="600" height="750"/><figcaption>Jim Clifford · Saskatoon</figcaption></figure>
      </div>
    </section>

    <section id="publications">
      {head(3, 'Every line, every station', 'Selected Publications')}
      <div class="chips" id="chips">{chips_html}<span class="count" id="count"></span></div>
      <ol class="publist" id="publist">{pubs_html}</ol>
    </section>

    <section id="projects">
      {head(4, 'Maps · archives · tools', 'Digital Projects')}
      {''.join(proj_html)}
    </section>

    <section id="talks">
      {head(5, 'Lectures · conferences · slides', 'Talks')}
      {talks_html}
    </section>

    <section id="teaching">
      {head(6, 'Courses & awards', 'Teaching')}
      <div class="cards">{''.join(teach)}</div>
    </section>

    <section id="funding">
      {head(7, 'Grants & partnerships', 'Research Funding')}
      <ol class="fund">{''.join(fund)}</ol>
    </section>

    <section id="contact">
      {head(8, 'Office · correspondence', 'Contact')}
      <dl class="contact">{inner(contact)}</dl>
      <footer>© Jim Clifford · Department of History · University of Saskatchewan<br/>Design drawn from the slides for <a href="https://jimclifford.ca/ssha-2026/">Mapping the Colonial Administrative State</a> (SSHA 2026) · Set in Atkinson Hyperlegible Next, Braille Institute · Press <b>d</b> for dark mode</footer>
    </section>
  </main>
</div>
<script>
const DATA = {json.dumps(data, ensure_ascii=False)};
const NAMES = {json.dumps({k: v[0] for k, v in LINES.items()})};
// ---- dark mode
const root = document.documentElement, modeBtn = document.getElementById('mode');
function syncMode() {{ const d = root.classList.contains('dark'); modeBtn.textContent = d ? 'Light mode' : 'Dark mode'; modeBtn.setAttribute('aria-pressed', d ? 'true' : 'false'); }}
function setMode(dark) {{ root.classList.toggle('dark', dark); try {{ localStorage.setItem('tube-mode', dark ? 'dark' : 'light'); }} catch (e) {{}} syncMode(); }}
syncMode();
modeBtn.onclick = () => setMode(!root.classList.contains('dark'));
addEventListener('keydown', e => {{ if (e.key === 'd' && !e.metaKey && !e.ctrlKey && !e.altKey && !/INPUT|TEXTAREA|SELECT/.test(e.target.tagName)) setMode(!root.classList.contains('dark')); }});
// ---- nav: the station for the section at the reading line; the last one at the bottom of the page
const navLinks = [...document.querySelectorAll('#nav a')];
const secs = navLinks.map(a => document.querySelector(a.hash)).filter(Boolean);
function track() {{
  let cur = secs[0];
  for (const sec of secs) if (sec.getBoundingClientRect().top <= innerHeight * 0.3) cur = sec;
  if (innerHeight + scrollY >= document.documentElement.scrollHeight - 2) cur = secs[secs.length - 1];
  navLinks.forEach(a => {{ const on = a.hash === '#' + cur.id; a.classList.toggle('on', on); if (on) a.setAttribute('aria-current', 'true'); else a.removeAttribute('aria-current'); }});
}}
addEventListener('scroll', track, {{ passive: true }}); addEventListener('resize', track); track();
// ---- map: popup card at the station
const tube = document.querySelector('svg.tube'), wrap = document.querySelector('.mapwrap'), pop = document.getElementById('pop'),
      scroller = document.querySelector('.mapscroll');
let pinned = false, current = null, hideT = null, opener = null;
function esc(s) {{ const d = document.createElement('div'); d.textContent = s; return d.innerHTML; }}
function stationEl(i) {{ return tube.querySelector('.st[data-i="' + i + '"]'); }}
function place() {{
  if (current === null) return;
  const r = stationEl(current).getBoundingClientRect(), w = wrap.getBoundingClientRect();
  const pw = pop.offsetWidth, ph = pop.offsetHeight;
  let x = r.left + r.width / 2 - w.left - pw / 2;
  x = Math.max(4, Math.min(x, w.width - pw - 4));
  const above = r.top - ph - 12 >= 8 || r.bottom + ph + 12 > innerHeight;
  const y = above ? r.top - w.top - ph - 12 : r.bottom - w.top + 12;
  pop.style.left = x + 'px'; pop.style.top = y + 'px';
}}
function show(i) {{
  clearTimeout(hideT);
  const s = DATA[i];
  current = i;
  tube.classList.add('focus');
  tube.querySelectorAll('.ln-g').forEach(g => g.classList.toggle('hot', s.lines.includes(g.dataset.line)));
  tube.querySelectorAll('.st, .slabel').forEach(el => el.classList.toggle('hot', el.dataset.i == i));
  tube.querySelectorAll('.st').forEach(el => el.classList.toggle('sel', el.dataset.i == i));
  pop.style.setProperty('--c', 'var(--' + s.lines[0] + ')');
  pop.setAttribute('aria-label', s.year + ': ' + s.items.map(it => it.title).join('; '));
  pop.innerHTML = '<button class="x" type="button" aria-label="Close">&times;</button><p class="py">' + s.year + '</p>' +
     s.items.map(it => '<div class="item"><h3>' + (it.href ? '<a href="' + esc(it.href) + '">' + esc(it.title) + ' &#8599;</a>' : esc(it.title)) + '</h3>' +
       (it.sub ? '<p>' + esc(it.sub.replace(/&amp;/g, '&')) + '</p>' : '') + '</div>').join('') +
     '<p class="lines">' + s.lines.map(l => '<span class="lt l-' + l + '-t">' + NAMES[l] + '</span>').join('') + '</p>';
  pop.querySelector('.x').onclick = () => close(true);
  pop.hidden = false;
  place();
}}
function hide(force) {{
  if (pinned && !force) return;
  pop.hidden = true; current = null;
  tube.classList.remove('focus');
  tube.querySelectorAll('.st').forEach(el => el.classList.remove('sel'));
}}
function close(refocus) {{
  const back = opener;
  pinned = false; hide(true); opener = null;
  if (refocus && back) back.focus({{ preventScroll: true }});
}}
function later() {{ clearTimeout(hideT); hideT = setTimeout(() => hide(), 280); }}
tube.querySelectorAll('.st, .slabel, .hit').forEach(el => {{
  const i = +el.dataset.i;
  el.addEventListener('mouseenter', () => {{ if (!pinned) show(i); }});
  el.addEventListener('mouseleave', later);
  el.addEventListener('click', e => {{ e.stopPropagation(); pinned = true; opener = stationEl(i); show(i); }});
}});
tube.querySelectorAll('.st').forEach(el => {{
  const i = +el.dataset.i;
  el.addEventListener('focus', () => {{ if (!pinned) show(i); }});
  el.addEventListener('blur', e => {{ if (!pinned && !pop.contains(e.relatedTarget)) hide(); }});
  el.addEventListener('keydown', e => {{
    if (e.key === 'Enter' || e.key === ' ') {{
      e.preventDefault(); pinned = true; opener = el; show(i);
      (pop.querySelector('a') || pop.querySelector('.x')).focus({{ preventScroll: true }});
    }}
  }});
}});
pop.addEventListener('mouseenter', () => clearTimeout(hideT));
pop.addEventListener('mouseleave', later);
pop.addEventListener('click', e => e.stopPropagation());
pop.addEventListener('focusout', e => {{ if (!pop.contains(e.relatedTarget) && e.relatedTarget !== opener) close(false); }});
document.addEventListener('click', () => close(false));
addEventListener('keydown', e => {{ if (e.key === 'Escape' && !pop.hidden) close(pop.contains(document.activeElement) || document.activeElement === opener); }});
scroller.addEventListener('scroll', () => pinned ? place() : hide());
addEventListener('resize', place);
// narrow screens: open the map at the recent end and say it scrolls
function fitMap() {{
  const over = scroller.scrollWidth > scroller.clientWidth + 4;
  wrap.classList.toggle('overflow', over);
  if (over && !fitMap.done) {{ scroller.scrollLeft = scroller.scrollWidth; fitMap.done = true; }}
}}
fitMap(); addEventListener('resize', fitMap);
// ---- publication filter by line
const chips = [...document.querySelectorAll('#chips .chip')], items = [...document.querySelectorAll('#publist li')], count = document.getElementById('count');
function filter(f) {{
  chips.forEach(c => {{ const on = c.dataset.f === f; c.classList.toggle('on', on); c.setAttribute('aria-pressed', on ? 'true' : 'false'); }});
  let n = 0;
  items.forEach(li => {{ const on = f === 'all' || li.dataset.tags.split(' ').includes(f); li.classList.toggle('hide', !on); n += on; }});
  count.textContent = n + ' of ' + items.length;
}}
chips.forEach(c => c.onclick = () => filter(c.dataset.f));
filter('all');
</script>
</body>
</html>
'''
open(OUT, 'w', encoding='utf-8').write(page)
ov = []
_segs = {l: [(a, b) for a, b in zip(r[0], r[0][1:]) if abs(a[1] - b[1]) < 0.5 and b[0] - a[0] > 2] for l, r in routes.items()}
_ls = list(_segs)
for i, l1 in enumerate(_ls):
    for l2 in _ls[i + 1:]:
        for a, b in _segs[l1]:
            for c, d in _segs[l2]:
                if abs(a[1] - c[1]) < GAP - 0.5 and min(b[0], d[0]) - max(a[0], c[0]) > 4:
                    ov.append((l1, l2, round(max(a[0], c[0])), round(min(b[0], d[0])), round(a[1]), round(c[1])))
if ov:
    sys.exit(f'lines drawn on top of each other: {ov}')
print('overlaps: none')
print('wrote', OUT, 'stations', len(stations), 'interchanges', nix, 'width', round(WIDTH), 'height', round(HEIGHT))
