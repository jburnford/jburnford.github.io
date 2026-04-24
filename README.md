# jimclifford.ca

Personal academic site for Jim Clifford — Associate Professor of History, University of Saskatchewan.

Hosted on GitHub Pages from this repo (`jburnford/jburnford.github.io`) and served at **https://jimclifford.ca** (apex) and **https://www.jimclifford.ca**.

---

## Stack

- **Static site**, no build step. Plain HTML + inline CSS + inline vanilla JS.
- Fonts: Roboto Slab (headlines), Work Sans (body), JetBrains Mono (metadata) — pulled from Google Fonts.
- No frameworks, no package manager, no CI. Edit a file, commit, push — GitHub Pages redeploys within ~1 minute.

## Repo layout

```
index.html            # the main portfolio page (single-file site)
CNAME                 # jimclifford.ca — do not delete
remember-lives.html   # COVID-19 memorial sub-page
history-496.html      # HIST 496 course page
blog-archive.html     # archived older blog
blog/                 # blog posts (legacy)
images/               # photos used by index.html + sub-pages
  jim-clifford.jpg    # portrait (600x750, ~98 KB)
blog-images/          # images for archived blog posts
README.md             # this file
```

Project sub-sites (Dry Rot, Joseph Banks KG, Philosophical Transactions, India Office List, Early Encyclopaedia Britannica, London Industry Map, HGIS to LOD Workshop) live in **separate repos** under the same GitHub account and are served as subpaths (e.g. `https://jimclifford.ca/dry-rot-history/`). They are not in this repo.

## Deploying changes

```
# edit
vim index.html

# commit and push
git add index.html
git commit -m "..."
git push origin master
```

GitHub Pages rebuilds automatically. Live within 1–2 minutes; sometimes 5 if cache-busting is slow.

## Custom domain (DNS)

Registered at **Netfirms Canada**. DNS records currently:

| Type  | Name  | Content                  |
|-------|-------|--------------------------|
| A     | `@`   | `185.199.108.153`        |
| A     | `@`   | `185.199.109.153`        |
| A     | `@`   | `185.199.110.153`        |
| A     | `@`   | `185.199.111.153`        |
| CNAME | `www` | `jburnford.github.io.`   |

If the four A records ever change, those are GitHub Pages' published IPs — check https://docs.github.com/en/pages/configuring-a-custom-domain-for-your-github-pages-site for updates.

**Do not delete `CNAME`** from the repo root. If you do, GitHub strips the custom domain from the repo settings and the site falls back to `jburnford.github.io`.

### Note on Netfirms quirks

Netfirms' SOA serial for this zone is stuck at `2011042724` and does not auto-increment on edits. Their nameserver cluster is mildly inconsistent — when editing records, expect some resolvers to lag behind the change by 15–30 minutes. The records still propagate; just budget extra time before declaring a problem.

## Common edits

### Add a publication

Publications are in the `<ul class="pub-list" id="publist">` block. Each entry:

```html
<li class="pub" data-tags="london ghost">
  <div class="yr">2025</div>
  <div class="body">
    <h4>Title goes here</h4>
    <div class="authors mono">Clifford, J. &amp; Co-author, A.</div>
    <div class="venue">Journal Name</div>
    <div class="abstract">Optional abstract with <a href="https://doi.org/...">DOI &rarr;</a></div>
  </div>
  <div class="type">Article</div>
</li>
```

`data-tags` drives the filter chips. Available tags: `london`, `ghost`, `dh`, `settler`, `covid`. Multiple tags are space-separated. Add `featured` to the `class` (e.g. `class="pub featured"`) to star the item.

Then update the `<span class="meta" id="pubmeta">N items</span>` count and `<span class="pubs-count" id="pubcount">showing N</span>` if item count changes.

### Add a digital project card

Two grids: *Completed & Active* and *Works in Progress* (the second grid uses `class="proj proj-wip"` on each card to get the hatched background and pulsing dot).

```html
<a class="proj" href="https://...">
  <div class="tag">Category Label</div>
  <h4>Project Name</h4>
  <p>Short description.</p>
  <div class="stats"><span><strong>2024</strong></span><span>Active</span></div>
  <span class="go">↗</span>
</a>
```

### Update the research-threads timeline (the SVG in the hero)

Each of the five threads (`Industrial London`, `Ghost Acres`, `Digital Humanities`, `Settler Colonialism`, `Pandemic`) is a `<g class="thread-row">` inside `<svg class="themes-svg">`. Threads are Gantt-style bars with milestone dots.

**Position math** — the x-axis runs `2005 → 2026` from `x=197.3` to `x=979.9`. One year = ~37.27 units. To place a dot at year Y: `x = 309.1 + (Y - 2008) * 37.27`. A few prebaked positions:

```
2008:309.1   2010:383.6   2012:458.2   2015:570.0   2016:607.3
2017:644.5   2020:756.3   2021:793.6   2022:830.9   2023:868.2
2024:905.4   2025:942.7   2026:980.0
```

Each thread has a fixed `cy` (center y): Industrial London 58, Ghost Acres 96, DH 134, Settler Col. 172, Pandemic 210.

To add a milestone dot with a hover popup:

```html
<circle class="dot" cx="907.4" cy="96" r="3" fill="oklch(0.50 0.12 60)" tabindex="0" role="button"
        data-pop="1" data-year="2024" data-title="Paper title"
        data-sub="Chapter · Publisher · Authors"
        data-href="https://doi.org/..."/>
```

The popup JS at the bottom of `index.html` wires up any `[data-pop]` element automatically — hover shows the popup, click opens `data-href` in a new tab, keyboard Enter/Space also triggers.

A couple of "anchor" milestones also have a text label next to the dot for visual orientation (e.g. "West Ham published", "Soap Industry"). Keep those as-is unless the rearrangement warrants it.

### Swap the headshot

Replace `images/jim-clifford.jpg` (currently 600×750 px, progressive JPEG, ~98 KB). If you drop in a larger source image, resize first:

```python
from PIL import Image, ImageOps
im = ImageOps.exif_transpose(Image.open('src.jpg'))
# cover-fit crop to 600x750
tw, th = 600, 750
sw, sh = im.size
s = max(tw/sw, th/sh)
im = im.resize((int(sw*s), int(sh*s)), Image.LANCZOS)
l, t = (im.size[0]-tw)//2, (im.size[1]-th)//2
im = im.crop((l, t, l+tw, t+th))
im.save('images/jim-clifford.jpg', 'JPEG', quality=85, optimize=True, progressive=True)
```

## Current status (as of April 2026)

- **Custom domain live:** `https://jimclifford.ca` served with a Let's Encrypt cert (auto-renewed by GitHub). HTTPS working for both apex and `www`.
- **"Enforce HTTPS"** should be enabled in the repo Pages settings. If the toggle gets unchecked, re-enable it at https://github.com/jburnford/jburnford.github.io/settings/pages.
- **Project sub-sites** (old `jburnford.github.io/<name>/` URLs) auto-redirect to `jimclifford.ca/<name>/`.
- **Headshot** is local. No external image dependencies.
- **Timeline** uses a custom HTML popup layer over the SVG. Hover, focus, and click all work; mobile requires a tap-then-tap pattern.

## Design origin

The current design came from a Claude Design (claude.ai/design) handoff bundle in April 2026. The original bundle + the chat transcript that drove the design decisions are preserved at:

- Bundle source: design URL used was `https://api.anthropic.com/v1/design/h/hGEUbOBWeVNmbHZK1qxeaQ`
- Chat transcript: included in the bundle at `website/chats/chat1.md`

Read that transcript before any major redesign — it captures the user's actual preferences (warm slab typography, no map, research-threads timeline, scholarly cool palette, etc.) which aren't self-evident from the code.

## Working with Claude on this site

If you're picking this up with a new Claude session:

1. The user wants **terse responses**, **no premature abstractions**, and **no trailing summaries** — just tell them what changed.
2. The user asks to "push" explicitly when they want a commit pushed; don't push preemptively.
3. Publication metadata is authoritative against Crossref / publisher pages — always verify DOIs and author order before editing entries.
4. For the timeline, **one primary thread per item** is the rule (no duplicated dots across threads). When an item fits multiple threads, pick the one that best captures the work's core focus.
5. The local working directory is `/home/jic823/website/`; this is also a git repo that pushes to `git@github.com:jburnford/jburnford.github.io.git`.
