#!/usr/bin/env python3
import os
import json
from urllib.parse import quote

BASE = os.path.dirname(os.path.abspath(__file__))
SVG_ICONS = {"timer": "<svg viewBox=\"0 0 24 24\" width=\"22\" height=\"22\" fill=\"none\" stroke=\"currentColor\" stroke-width=\"2\" stroke-linecap=\"round\" stroke-linejoin=\"round\"><circle cx=\"12\" cy=\"13\" r=\"8\"/><path d=\"M12 9v4l2.5 2.5\"/><path d=\"M9 2h6\"/></svg>", "book": "<svg viewBox=\"0 0 24 24\" width=\"22\" height=\"22\" fill=\"none\" stroke=\"currentColor\" stroke-width=\"2\" stroke-linecap=\"round\" stroke-linejoin=\"round\"><path d=\"M4 19.5A2.5 2.5 0 0 1 6.5 17H20\"/><path d=\"M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z\"/></svg>", "chart": "<svg viewBox=\"0 0 24 24\" width=\"22\" height=\"22\" fill=\"none\" stroke=\"currentColor\" stroke-width=\"2\" stroke-linecap=\"round\" stroke-linejoin=\"round\"><path d=\"M18 20V10\"/><path d=\"M12 20V4\"/><path d=\"M6 20v-6\"/></svg>", "calendar": "<svg viewBox=\"0 0 24 24\" width=\"22\" height=\"22\" fill=\"none\" stroke=\"currentColor\" stroke-width=\"2\" stroke-linecap=\"round\" stroke-linejoin=\"round\"><rect x=\"3\" y=\"4\" width=\"18\" height=\"18\" rx=\"3\"/><line x1=\"16\" y1=\"2\" x2=\"16\" y2=\"6\"/><line x1=\"8\" y1=\"2\" x2=\"8\" y2=\"6\"/><line x1=\"3\" y1=\"10\" x2=\"21\" y2=\"10\"/></svg>", "map": "<svg viewBox=\"0 0 24 24\" width=\"22\" height=\"22\" fill=\"none\" stroke=\"currentColor\" stroke-width=\"2\" stroke-linecap=\"round\" stroke-linejoin=\"round\"><polygon points=\"1 6 1 22 8 18 16 22 23 18 23 2 16 6 8 2 1 6\"/><line x1=\"8\" y1=\"2\" x2=\"8\" y2=\"18\"/><line x1=\"16\" y1=\"6\" x2=\"16\" y2=\"22\"/></svg>", "shield": "<svg viewBox=\"0 0 24 24\" width=\"22\" height=\"22\" fill=\"none\" stroke=\"currentColor\" stroke-width=\"2\" stroke-linecap=\"round\" stroke-linejoin=\"round\"><path d=\"M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z\"/><path d=\"M9 12l2 2 4-4\"/></svg>"}
FEATURE_ICON_KEYS = ["timer", "book", "chart", "calendar", "map", "shield"]


with open(os.path.join(BASE, "config.json"), "r", encoding="utf-8") as f:
    CFG = json.load(f)

with open(os.path.join(BASE, "templates/page.html"), "r", encoding="utf-8") as f:
    TEMPLATE = f.read()

LANGS = {}
for code in CFG["supported_langs"]:
    with open(os.path.join(BASE, f"locales/{code}.json"), "r", encoding="utf-8") as f:
        LANGS[code] = json.load(f)

# Проверяем наличие скриншотов в папке screenshots/iPad
IPAD_DIR = os.path.join(BASE, "screenshots", "iPad")
IPAD_FILES = []
if os.path.isdir(IPAD_DIR):
    IPAD_FILES = sorted([
        fn for fn in os.listdir(IPAD_DIR)
        if fn.lower().endswith((".jpg", ".jpeg", ".png", ".webp"))
    ])

def render(code, d, is_root=False):
    prefix = "." if is_root else ".."
    base_url = CFG["base_url"]
    canonical = f"{base_url}/" if is_root else f"{base_url}/{code}/"

    hreflangs = [f'<link rel="alternate" hreflang="x-default" href="{base_url}/" />']
    for lc in CFG["supported_langs"]:
        hreflangs.append(f'<link rel="alternate" hreflang="{lc}" href="{base_url}/{lc}/" />')

    pills = []
    for lc, ld in LANGS.items():
        act = "active" if lc == code else ""
        pills.append(f'<a href="{prefix}/{lc}/index.html" class="lang-pill {act}"><span>{ld["flag"]}</span> {ld["name"]}</a>')

    shot_folder = d["shot_folder"]
    if not os.path.isdir(os.path.join(BASE, "screenshots", shot_folder)):
        shot_folder = "English"
    enc_folder = quote(shot_folder)

    shots_html, schema_shots = [], []
    for fname, stitle, sdesc in d["shots"]:
        src = f"{prefix}/screenshots/{enc_folder}/{fname}"
        schema_shots.append(f"{base_url}/screenshots/{enc_folder}/{fname}")
        t_attr = 'data-theme-shot="dark"' if fname in ("7.jpg", "8.jpg") else 'data-theme-shot="light"'
        shots_html.append(f"""<article class="shot-card" {t_attr}>
          <div class="iphone-frame"><img data-shot-file="{fname}" src="{src}" alt="{stitle} — JW Ministry" loading="lazy" width="320" height="690" /></div>
          <div class="shot-meta"><h3>{stitle}</h3><p>{sdesc}</p></div>
        </article>""")

    # iPad screenshots
    ipad_btn_html = ""
    ipad_shots_html = []
    if IPAD_FILES:
        ipad_lbl = d.get("filter_ipad", "iPad")
        ipad_btn_html = f'<button class="filter-btn" onclick="filterScreenshots(\'ipad\', this)">{ipad_lbl} ({len(IPAD_FILES)})</button>'
        shot_lookup = {fn: (st, sd) for fn, st, sd in d["shots"]}
        for idx, ifile in enumerate(IPAD_FILES, 1):
            isrc = f"{prefix}/screenshots/iPad/{quote(ifile)}"
            schema_shots.append(f"{base_url}/screenshots/iPad/{quote(ifile)}")
            ititle, idesc = shot_lookup.get(ifile, (f"iPad — #{idx}", "JW Ministry — iPadOS"))
            ipad_shots_html.append(f"""<article class="shot-card ipad-card" data-theme-shot="ipad">
              <div class="ipad-frame"><img src="{isrc}" alt="{ititle} — iPad" loading="lazy" /></div>
              <div class="shot-meta"><h3>iPad • {ititle}</h3><p>{idesc}</p></div>
            </article>""")

    f_badges = d.get("feature_badges", [])
    feats_html = []
    for idx, (_, ft, fd) in enumerate(d["features"]):
        svg_ic = SVG_ICONS[FEATURE_ICON_KEYS[idx % len(FEATURE_ICON_KEYS)]]
        kicker = f_badges[idx] if idx < len(f_badges) else ""
        feats_html.append(f'''<div class="feat-card">
          <div class="feat-top">
            <div class="feat-icon">{svg_ic}</div>
            <span class="feat-kicker">{kicker}</span>
          </div>
          <h3>{ft}</h3>
          <p>{fd}</p>
        </div>''')

    p_badges = d.get("pillar_badges", [])
    p_checks = d.get("pillar_Checklists", [])
    check_svg = '<svg viewBox="0 0 20 20" fill="currentColor"><path fill-rule="evenodd" d="M16.704 4.153a.75.75 0 01.143 1.052l-8 10.5a.75.75 0 01-1.127.075l-4.5-4.5a.75.75 0 011.06-1.06l3.894 3.893 7.48-9.817a.75.75 0 011.05-.143z" clip-rule="evenodd"/></svg>'
    seo_pillars_html = []
    for idx, (pt, pd) in enumerate(d.get("seo_pillars", [])):
        pkicker = p_badges[idx] if idx < len(p_badges) else ""
        c_items = p_checks[idx] if idx < len(p_checks) else []
        li_html = "".join([f"<li>{check_svg}<span>{ci}</span></li>" for ci in c_items])
        ul_block = f'<ul class="pillar-list">{li_html}</ul>' if li_html else ""
        seo_pillars_html.append(f'''<article class="seo-card">
          <span class="pillar-kicker">{pkicker}</span>
          <h3>{pt}</h3>
          <p>{pd}</p>
          {ul_block}
        </article>''')
    seo_tags_html = [f'<span class="seo-tag">{tg}</span>' for tg in d.get("seo_tags", [])]

    # Interactive 35 Language Badges
    badges_html = []
    for disp_name, folder_name in CFG.get("lang_folder_map", []):
        active_cls = "active-shot-lang" if folder_name == shot_folder else ""
        safe_folder = folder_name.replace("'", "\\'")
        safe_disp = disp_name.replace("'", "\\'")
        badges_html.append(
            f'<span class="loc-badge {active_cls}" onclick="switchScreenshotLanguage(\'{safe_folder}\', \'{safe_disp}\', this)" title="Preview {disp_name} screenshots">{disp_name}</span>'
        )

    # Comparison Table
    headers = d.get("comp_headers", ["Feature", "Paper", "Old Apps", "JW Ministry 1.8"])
    rows = d.get("comp_rows", [])
    th_cells = "".join([f'<th class="{"highlight-col" if i==3 else ""}">{h}</th>' for i, h in enumerate(headers)])
    tr_list = []
    for r in rows:
        tds = "".join([f'<td class="{"highlight-col" if i==3 else ""}">{c}</td>' for i, c in enumerate(r)])
        tr_list.append(f"<tr>{tds}</tr>")
    comp_table_html = f'<table class="comp-table"><thead><tr>{th_cells}</tr></thead><tbody>{"".join(tr_list)}</tbody></table>'

    faqs_html = [f'<details class="faq-item"><summary>{q}</summary><p>{a}</p></details>' for q, a in d["faqs"]]
    wn_items_html = [f"<li>{item}</li>" for item in d.get("wn_items", [])]

    schema = [
        {
            "@context": "https://schema.org",
            "@type": "MobileApplication",
            "name": "JW Ministry",
            "operatingSystem": "iOS 16.0 or later, iPadOS 16.0 or later",
            "applicationCategory": "LifestyleApplication",
            "url": canonical,
            "downloadUrl": CFG["app_store_url"],
            "inLanguage": CFG["supported_langs"],
            "description": d["description"],
            "softwareVersion": CFG["version"],
            "screenshot": schema_shots,
            "offers": {"@type": "Offer", "price": "0", "priceCurrency": "USD"}
        },
        {
            "@context": "https://schema.org",
            "@type": "FAQPage",
            "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in d["faqs"]]
        },
        {
            "@context": "https://schema.org",
            "@type": "HowTo",
            "name": d.get("howto_name", "How to Track Field Service Hours"),
            "step": [
                {"@type": "HowToStep", "position": idx, "name": st_name, "text": st_txt}
                for idx, (st_name, st_txt) in enumerate(d.get("howto_steps", []), 1)
            ]
        },
        {
            "@context": "https://schema.org",
            "@type": "BreadcrumbList",
            "itemListElement": [
                {"@type": "ListItem", "position": 1, "name": "JW Ministry", "item": f"{base_url}/"},
                {"@type": "ListItem", "position": 2, "name": d["name"], "item": canonical}
            ]
        }
    ]

    redirect_js = ""
    if is_root:
        redirect_js = """<script>(function(){try{if(sessionStorage.getItem('jw_lang_selected'))return;var l=(navigator.language||'en').toLowerCase(),t=null;if(l.startsWith('ru')||l.startsWith('uk')||l.startsWith('be'))t='ru';else if(l.startsWith('es'))t='es';else if(l.startsWith('de'))t='de';else if(l.startsWith('pt'))t='pt';else if(l.startsWith('fr'))t='fr';if(t){sessionStorage.setItem('jw_lang_selected','1');window.location.replace('./'+t+'/index.html');}}catch(e){}})();</script>"""

    replacements = {
        "{{PREFIX}}": prefix,
        "{{CANONICAL_URL}}": canonical,
        "{{HREFLANG_TAGS}}": "\n  ".join(hreflangs),
        "{{LANG_PILLS}}": "\n        ".join(pills),
        "{{JSON_LD}}": json.dumps(schema, ensure_ascii=False, indent=2),
        "{{AUTO_REDIRECT_SCRIPT}}": redirect_js,
        "{{OG_IMAGE_URL}}": f"{base_url}/screenshots/{enc_folder}/1.jpg",
        "{{HERO_IMG_LEFT}}": f"{prefix}/screenshots/{enc_folder}/4.jpg",
        "{{HERO_IMG_CENTER}}": f"{prefix}/screenshots/{enc_folder}/1.jpg",
        "{{HERO_IMG_RIGHT}}": f"{prefix}/screenshots/{enc_folder}/3.jpg",
        "{{SHOTS_GRID}}": "\n          ".join(shots_html),
        "{{IPAD_FILTER_BTN}}": ipad_btn_html,
        "{{IPAD_SHOTS_GRID}}": "\n          ".join(ipad_shots_html),
        "{{FEATURES_GRID}}": "\n          ".join(feats_html),
        "{{COMPARISON_TABLE}}": comp_table_html,
        "{{SEO_PILLARS_GRID}}": "\n          ".join(seo_pillars_html),
        "{{SEO_TAGS_CLOUD}}": "\n            ".join(seo_tags_html),
        "{{LANG_BADGES}}": "\n            ".join(badges_html),
        "{{FAQ_LIST}}": "\n          ".join(faqs_html),
        "{{WN_LIST_ITEMS}}": "\n            ".join(wn_items_html),
        "{{APP_STORE_ID}}": CFG["app_store_id"],
        "{{APP_STORE_URL}}": CFG["app_store_url"],
        "{{APP_STORE_URL_ENCODED}}": quote(CFG["app_store_url"], safe=""),
        "{{BOOSTY_URL}}": CFG["boosty_url"],
        "{{PATREON_URL}}": CFG["patreon_url"],
        "{{USDT_TRC20}}": CFG["usdt_trc20"],
        "{{TON_ADDRESS}}": CFG["ton_address"],
        "{{CONTACT_EMAIL}}": CFG["contact_email"],
        "{{GITHUB_ISSUES_URL}}": CFG["github_issues_url"]
    }
    for k, v in d.items():
        if isinstance(v, str):
            replacements["{{" + k.upper() + "}}"] = v

    html = TEMPLATE
    for k, v in replacements.items():
        html = html.replace(k, v)
    return html

with open(os.path.join(BASE, "index.html"), "w", encoding="utf-8") as f:
    f.write(render("en", LANGS["en"], is_root=True))

for code, data in LANGS.items():
    out_dir = os.path.join(BASE, code)
    os.makedirs(out_dir, exist_ok=True)
    with open(os.path.join(out_dir, "index.html"), "w", encoding="utf-8") as f:
        f.write(render(code, data, is_root=False))

print(f"✅ Сборка V2 завершена! Найдено скриншотов iPad: {len(IPAD_FILES)}; подключено интерактивных языковых папок: {len(CFG['lang_folder_map'])}.")


# Генерируем расширенный sitemap.xml с поддержкой Google Images (xmlns:image) и hreflang
base_url = CFG["base_url"]
url_blocks = []
page_entries = [("", LANGS["en"])] + [(c, LANGS[c]) for c in CFG["supported_langs"]]
for sub, ldata in page_entries:
    loc = f"{base_url}/" if sub == "" else f"{base_url}/{sub}/"
    sfolder = quote(ldata["shot_folder"])
    img_tags = []
    for fn, stitle, _ in ldata["shots"]:
        img_url = f"{base_url}/screenshots/{sfolder}/{fn}"
        safe_title = stitle.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        img_tags.append(f"    <image:image>\n      <image:loc>{img_url}</image:loc>\n      <image:title>{safe_title} — JW Ministry</image:title>\n    </image:image>")
    imgs_joined = "\n".join(img_tags)
    prio = "1.0" if sub == "" else "0.95"
    url_blocks.append(f"  <url>\n    <loc>{loc}</loc>\n    <changefreq>weekly</changefreq>\n    <priority>{prio}</priority>\n{imgs_joined}\n  </url>")

url_blocks.append(f"  <url>\n    <loc>{base_url}/privacy-policy.html</loc>\n    <changefreq>monthly</changefreq>\n    <priority>0.5</priority>\n  </url>")

sitemap_content = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:image="http://www.google.com/schemas/sitemap-image/1.1">\n' + "\n".join(url_blocks) + "\n</urlset>\n"
with open(os.path.join(BASE, "sitemap.xml"), "w", encoding="utf-8") as f:
    f.write(sitemap_content)
print("✅ Расширенный Image Sitemap (sitemap.xml) и llms.txt успешно обновлены!")
