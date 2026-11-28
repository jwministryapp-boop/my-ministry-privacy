from datetime import date
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


# Проверяем наличие скриншотов в папке screenshots/Duo (iPhone Duo)
DUO_DIR = os.path.join(BASE, "screenshots", "Duo")
DUO_FILES = []
if os.path.isdir(DUO_DIR):
    DUO_FILES = sorted([
        fn for fn in os.listdir(DUO_DIR)
        if fn.lower().endswith((".jpg", ".jpeg", ".png", ".webp"))
    ])


def get_ga_script():
    ga_id = CFG.get("ga_measurement_id", "").strip()
    if not ga_id or "XXXX" in ga_id:
        return ""
    if ga_id.startswith("GTM-"):
        return f"""<!-- Google Tag Manager -->
  <script>
    window.dataLayer = window.dataLayer || [];
    window.dataLayer.push({{'gtm.start': new Date().getTime(), event: 'gtm.js'}});
    function gtag(){{dataLayer.push(arguments);}}
    gtag('js', new Date());
  </script>
  <script async src="https://www.googletagmanager.com/gtm.js?id={ga_id}"></script>"""
    return f"""<!-- Google Analytics 4 -->
  <script async src="https://www.googletagmanager.com/gtag/js?id={ga_id}"></script>
  <script>
    window.dataLayer = window.dataLayer || [];
    function gtag(){{dataLayer.push(arguments);}}
    gtag('js', new Date());
    gtag('config', '{ga_id}');
  </script>"""

def render(code, d, is_root=False):
    prefix = "." if is_root else ".."
    base_url = CFG["base_url"]
    canonical = f"{base_url}/" if (is_root or code == "en") else f"{base_url}/{code}/"

    hreflangs = [f'<link rel="alternate" hreflang="x-default" href="{base_url}/" />']
    for lc in CFG["supported_langs"]:
        h_url = f"{base_url}/" if lc == "en" else f"{base_url}/{lc}/"
        hreflangs.append(f'<link rel="alternate" hreflang="{lc}" href="{h_url}" />')

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


    # iPhone Duo screenshots
    duo_btn_html = ""
    duo_shots_html = []
    if DUO_FILES:
        duo_lbl = d.get("filter_duo", "iPhone Duo")
        duo_btn_html = f'<button class="filter-btn" onclick="filterScreenshots(\'duo\', this)">{duo_lbl} ({len(DUO_FILES)})</button>'
        for idx, dfile in enumerate(DUO_FILES, 1):
            dsrc = f"{prefix}/screenshots/Duo/{quote(dfile)}"
            schema_shots.append(f"{base_url}/screenshots/Duo/{quote(dfile)}")
            duo_shots_html.append(f"""<article class="shot-card duo-card" data-theme-shot="duo">
              <div class="duo-frame"><img src="{dsrc}" alt="iPhone Duo — #{idx} — JW Ministry" loading="lazy" /></div>
              <div class="shot-meta"><h3>iPhone Duo • #{idx}</h3><p>JW Ministry — Adaptive Foldable Layout</p></div>
            </article>""")

    f_badges = d.get("feature_badges", [])
    feats_html = []
    for idx, feat_item in enumerate(d["features"]):
        ft, fd = feat_item[-2], feat_item[-1]
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
    reviews_html = [f'<article class="review-card"><div class="review-stars" aria-label="5 out of 5 stars">★★★★★</div><p class="review-text">“{rt}”</p><div class="review-author">{ra}</div></article>' for ra, rt in d.get("reviews", [])]
    wn_items_html = [f"<li>{item}</li>" for item in d.get("wn_items", [])]
    wn_items_18_html = [f"<li>{item}</li>" for item in d.get("wn_items_18", [])]

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
            "offers": {"@type": "Offer", "price": "0", "priceCurrency": "USD"},
            "aggregateRating": {"@type": "AggregateRating", "ratingValue": "5.0", "bestRating": "5", "ratingCount": "28"}
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
        redirect_js = """<script>(function(){try{var ua=(navigator.userAgent||'').toLowerCase();if(/bot|google|yandex|bing|duckduck|baidu|slurp|crawler|spider|applebot|facebook|embedly|quora|pinterest|slack|vkshare|telegram|whatsapp/i.test(ua)||navigator.webdriver)return;if(sessionStorage.getItem('jw_lang_selected'))return;var l=(navigator.language||'en').toLowerCase(),t=null;var map={'uk':'uk','ru':'ru','be':'ru','es':'es','de':'de','pt':'pt','fr':'fr','it':'it','pl':'pl','ja':'ja','ko':'ko','zh':'zh','nl':'nl','ro':'ro','cs':'cs','sk':'sk','hu':'hu','el':'el','tr':'tr','id':'id','th':'th','hi':'hi','da':'da','sv':'sv','nb':'nb','no':'nb','nn':'nb','fi':'fi','hr':'hr'};var p2=l.slice(0,2);if(map[p2]&&map[p2]!=='en')t=map[p2];if(t){sessionStorage.setItem('jw_lang_selected','1');window.location.replace('./'+t+'/index.html');}}catch(e){}})();</script>"""

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
        "{{DUO_FILTER_BTN}}": duo_btn_html,
        "{{DUO_SHOTS_GRID}}": "\n          ".join(duo_shots_html),
        "{{FEATURES_GRID}}": "\n          ".join(feats_html),
        "{{COMPARISON_TABLE}}": comp_table_html,
        "{{SEO_PILLARS_GRID}}": "\n          ".join(seo_pillars_html),
        "{{SEO_TAGS_CLOUD}}": "\n            ".join(seo_tags_html),
        "{{LANG_BADGES}}": "\n            ".join(badges_html),
        "{{FAQ_LIST}}": "\n          ".join(faqs_html),
        "{{REVIEWS_GRID}}": "\n          ".join(reviews_html),
        "{{WN_LIST_ITEMS}}": "\n            ".join(wn_items_html),
        "{{WN_LIST_ITEMS_18}}": "\n            ".join(wn_items_18_html),
        "{{GA_SCRIPT}}": get_ga_script(),
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
page_entries = [("", LANGS["en"])] + [(c, LANGS[c]) for c in CFG["supported_langs"] if c != "en"]
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
    url_blocks.append(f"  <url>\n    <loc>{loc}</loc>\n    <lastmod>{date.today().isoformat()}</lastmod>\n    <changefreq>weekly</changefreq>\n    <priority>{prio}</priority>\n{imgs_joined}\n  </url>")

today_iso = date.today().isoformat()
url_blocks.append(f"  <url>\n    <loc>{base_url}/pioneer-calculator/</loc>\n    <lastmod>{today_iso}</lastmod>\n    <changefreq>monthly</changefreq>\n    <priority>0.9</priority>\n  </url>")
url_blocks.append(f"  <url>\n    <loc>{base_url}/ru/pioneer-calculator/</loc>\n    <lastmod>{today_iso}</lastmod>\n    <changefreq>monthly</changefreq>\n    <priority>0.9</priority>\n  </url>")
url_blocks.append(f"  <url>\n    <loc>{base_url}/bible-reading-schedule/</loc>\n    <lastmod>{today_iso}</lastmod>\n    <lastmod>{date.today().isoformat()}</lastmod>\n    <changefreq>weekly</changefreq>\n    <priority>0.9</priority>\n  </url>")
url_blocks.append(f"  <url>\n    <loc>{base_url}/ru/bible-reading-schedule/</loc>\n    <lastmod>{today_iso}</lastmod>\n    <lastmod>{date.today().isoformat()}</lastmod>\n    <changefreq>weekly</changefreq>\n    <priority>0.9</priority>\n  </url>")
url_blocks.append(f"  <url>\n    <loc>{base_url}/privacy-policy.html</loc>\n    <lastmod>{today_iso}</lastmod>\n    <changefreq>monthly</changefreq>\n    <priority>0.5</priority>\n  </url>")
for lc in CFG["supported_langs"]:
    if lc != "en":
        url_blocks.append(f"  <url>\n    <loc>{base_url}/{lc}/privacy-policy.html</loc>\n    <lastmod>{today_iso}</lastmod>\n    <changefreq>monthly</changefreq>\n    <priority>0.5</priority>\n  </url>")

sitemap_content = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:image="http://www.google.com/schemas/sitemap-image/1.1">\n' + "\n".join(url_blocks) + "\n</urlset>\n"
with open(os.path.join(BASE, "sitemap.xml"), "w", encoding="utf-8") as f:
    f.write(sitemap_content)
print("✅ Расширенный Image Sitemap (sitemap.xml) и llms.txt успешно обновлены!")


# Генерируем локализованные страницы privacy-policy.html для всех 6 языков и корня
with open(os.path.join(BASE, "templates/privacy.html"), "r", encoding="utf-8") as f:
    PRIV_TPL = f.read()

def render_privacy(code, d, is_root=False):
    prefix = "." if is_root else ".."
    base_url = CFG["base_url"]
    p = d["privacy_page"]
    canonical = f"{base_url}/privacy-policy.html" if (is_root or code == "en") else f"{base_url}/{code}/privacy-policy.html"

    hreflangs = [f'<link rel="alternate" hreflang="x-default" href="{base_url}/privacy-policy.html" />']
    for lc in CFG["supported_langs"]:
        hu = f"{base_url}/privacy-policy.html" if lc == "en" else f"{base_url}/{lc}/privacy-policy.html"
        hreflangs.append(f'<link rel="alternate" hreflang="{lc}" href="{hu}" />')

    pills = []
    for lc, ld in LANGS.items():
        act = "active" if lc == code else ""
        pills.append(f'<a href="{prefix}/{lc}/privacy-policy.html" class="lang-pill {act}"><span>{ld["flag"]}</span> {ld["name"]}</a>')

    red_js = ""
    if is_root:
        red_js = """<script>(function(){try{var ua=(navigator.userAgent||'').toLowerCase();if(/bot|google|yandex|bing|duckduck|crawler|spider|applebot/i.test(ua)||navigator.webdriver)return;if(sessionStorage.getItem('jw_priv_lang'))return;var l=(navigator.language||'en').toLowerCase(),t=null;var map={'uk':'uk','ru':'ru','be':'ru','es':'es','de':'de','pt':'pt','fr':'fr','it':'it','pl':'pl','ja':'ja','ko':'ko','zh':'zh','nl':'nl','ro':'ro','cs':'cs','sk':'sk','hu':'hu','el':'el','tr':'tr','id':'id','th':'th','hi':'hi','da':'da','sv':'sv','nb':'nb','no':'nb','nn':'nb','fi':'fi','hr':'hr'};var p2=l.slice(0,2);if(map[p2]&&map[p2]!=='en')t=map[p2];if(t){sessionStorage.setItem('jw_priv_lang','1');window.location.replace('./'+t+'/privacy-policy.html');}}catch(e){}})();</script>"""

    rep = {
        "{{PREFIX}}": prefix,
        "{{HTML_LANG}}": d["html_lang"],
        "{{FLAG}}": d["flag"],
        "{{NAME}}": d["name"],
        "{{P_TITLE}}": p["page_title"],
        "{{P_DESC}}": p["meta_desc"],
        "{{P_CANONICAL}}": canonical,
        "{{P_HREFLANGS}}": "\n  ".join(hreflangs),
        "{{P_LANG_PILLS}}": "\n            ".join(pills),
        "{{P_REDIRECT_JS}}": red_js,
        "{{P_BACK_HOME}}": p["back_home"],
        "{{P_SUP_TITLE}}": p["sup_title"],
        "{{P_SUP_DESC}}": p["sup_desc"],
        "{{P_SUP_ISSUES}}": p["sup_issues"],
        "{{P_SUP_STORE}}": p["sup_store"],
        "{{P_UPDATED}}": p["updated"],
        "{{P_H1}}": p["h1"],
        "{{P_INTRO}}": p["intro"],
        "{{P_S1_T}}": p["s1_t"],
        "{{P_S1_P}}": p["s1_p"],
        "{{P_S1_UL}}": "".join([f"<li>{x}</li>" for x in p["s1_ul"]]),
        "{{P_S2_T}}": p["s2_t"],
        "{{P_S2_UL}}": "".join([f"<li>{x}</li>" for x in p["s2_ul"]]),
        "{{P_S3_T}}": p["s3_t"],
        "{{P_S3_UL}}": "".join([f"<li>{x}</li>" for x in p["s3_ul"]]),
        "{{P_S4_T}}": p["s4_t"],
        "{{P_S4_P}}": p["s4_p"],
        "{{P_S5_T}}": p["s5_t"],
        "{{P_S5_P}}": p["s5_p"],
        "{{CONTACT_EMAIL}}": CFG["contact_email"],
        "{{GITHUB_ISSUES_URL}}": CFG["github_issues_url"],
        "{{APP_STORE_URL}}": CFG["app_store_url"],
        "{{GA_SCRIPT}}": get_ga_script()
    }
    html = PRIV_TPL
    for k, v in rep.items():
        html = html.replace(k, v)
    return html

with open(os.path.join(BASE, "privacy-policy.html"), "w", encoding="utf-8") as f:
    f.write(render_privacy("en", LANGS["en"], is_root=True))

for code, data in LANGS.items():
    with open(os.path.join(BASE, code, "privacy-policy.html"), "w", encoding="utf-8") as f:
        f.write(render_privacy(code, data, is_root=False))

print("✅ Политика конфиденциальности и Поддержка сгенерированы на всех 6 языках!")


# Генерируем посадочные страницы «График чтения Библии» для всех 27 языков
with open(os.path.join(BASE, "templates/bible_schedule.html"), "r", encoding="utf-8") as f:
    BIBLE_TPL = f.read()

def render_bible_page(code, d, is_root=False):
    prefix = ".." if is_root else "../.."
    home_link = "../" if is_root else "../"
    priv_link = "../privacy-policy.html"
    canonical = f"{base_url}/bible-reading-schedule/" if (is_root or code == "en") else f"{base_url}/{code}/bible-reading-schedule/"

    hreflangs = [f'<link rel="alternate" hreflang="x-default" href="{base_url}/bible-reading-schedule/" />']
    for lc in CFG["supported_langs"]:
        hu = f"{base_url}/bible-reading-schedule/" if lc == "en" else f"{base_url}/{lc}/bible-reading-schedule/"
        hreflangs.append(f'<link rel="alternate" hreflang="{lc}" href="{hu}" />')

    pills = []
    for lc, ld in LANGS.items():
        act = "active" if lc == code else ""
        href = f"{prefix}/bible-reading-schedule/index.html" if lc == "en" else f"{prefix}/{lc}/bible-reading-schedule/index.html"
        pills.append(f'<a href="{href}" class="lang-pill {act}"><span>{ld["flag"]}</span> {ld["name"]}</a>')

    bp = d.get("bible_page", LANGS["en"]["bible_page"])
    sfolder = d["shot_folder"]
    if not os.path.isdir(os.path.join(BASE, "screenshots", sfolder)):
        sfolder = "English"

    cards = "".join([f'<div class="feat-card"><h3>{rt}</h3><p>{rd}</p></div>' for rt, rd in bp["routes"]])
    html = BIBLE_TPL
    reps = {
        "{{LANG}}": d["html_lang"], "{{PREFIX}}": prefix, "{{HOME_LINK}}": home_link,
        "{{PRIV_LINK}}": priv_link, "{{PRIV_LABEL}}": d.get("footer_privacy", "Privacy Policy"),
        "{{FLAG}}": d["flag"], "{{NAME}}": d["name"],
        "{{CANONICAL}}": canonical, "{{HREFLANGS}}": "\n  ".join(hreflangs),
        "{{LANG_PILLS}}": "\n            ".join(pills),
        "{{BADGE}}": d.get("badge", "JW Ministry 2.0.1"),
        "{{TITLE}}": bp["title"], "{{DESC}}": bp["desc"], "{{H1}}": bp["h1"],
        "{{INTRO}}": bp["intro"], "{{CTA}}": d.get("cta_appstore", "Download on the App Store"),
        "{{BACK_HOME}}": d.get("privacy_page", {}).get("back_home", "Home"),
        "{{ALL_FEATURES}}": d.get("nav_features", "Features"),
        "{{SHOT_FOLDER}}": quote(sfolder),
        "{{SHOT1_T}}": bp["s1_t"], "{{SHOT1_D}}": bp["s1_d"],
        "{{SHOT2_T}}": bp["s2_t"], "{{SHOT2_D}}": bp["s2_d"],
        "{{ROUTES_TITLE}}": bp["routes_title"], "{{ROUTES_CARDS}}": cards,
        "{{APP_STORE_URL}}": CFG["app_store_url"], "{{GA_SCRIPT}}": get_ga_script()
    }
    for k, v in reps.items():
        html = html.replace(k, v)
    return html

os.makedirs(os.path.join(BASE, "bible-reading-schedule"), exist_ok=True)
with open(os.path.join(BASE, "bible-reading-schedule", "index.html"), "w", encoding="utf-8") as f:
    f.write(render_bible_page("en", LANGS["en"], is_root=True))

for code, data in LANGS.items():
    out_dir = os.path.join(BASE, code, "bible-reading-schedule")
    os.makedirs(out_dir, exist_ok=True)
    with open(os.path.join(out_dir, "index.html"), "w", encoding="utf-8") as f:
        f.write(render_bible_page(code, data, is_root=False))

print("✅ Посадочные страницы bible-reading-schedule сгенерированы на всех 27 языках!")


# Генерируем интерактивный Калькулятор часов пионера (EN и RU)
with open(os.path.join(BASE, "templates/pioneer_calc.html"), "r", encoding="utf-8") as f:
    CALC_TPL = f.read()

# === Pioneer Calculator (all supported langs) ===
SITE_URL = CFG.get("site_url", "https://jwministry.org").rstrip("/")
calc_tpl_file = os.path.join(BASE, "templates/pioneer_calc.html")
if os.path.exists(calc_tpl_file):
    with open(calc_tpl_file, "r", encoding="utf-8") as f:
        calc_tpl = f.read()
    for code in CFG["supported_langs"]:
        with open(os.path.join(BASE, f"locales/{code}.json"), "r", encoding="utf-8") as _f: d = json.load(_f)
        cp = d.get("calc_page")
        if not cp:
            continue
        is_root = (code == "en")
        out_dir = os.path.join(BASE, "pioneer-calculator" if is_root else f"{code}/pioneer-calculator")
        os.makedirs(out_dir, exist_ok=True)
        canonical = f"{SITE_URL}/pioneer-calculator/" if is_root else f"{SITE_URL}/{code}/pioneer-calculator/"
        home_url = "/" if is_root else f"/{code}/"
        bible_url = "/bible-reading-schedule/" if is_root else f"/{code}/bible-reading-schedule/"
        hreflangs = [f'<link rel="alternate" hreflang="x-default" href="{SITE_URL}/pioneer-calculator/">']
        lang_links = []
        for lc in CFG["supported_langs"]:
            with open(os.path.join(BASE, f"locales/{lc}.json"), "r", encoding="utf-8") as _lf: ld = json.load(_lf)
            lurl = f"{SITE_URL}/pioneer-calculator/" if lc == "en" else f"{SITE_URL}/{lc}/pioneer-calculator/"
            lhref = "/pioneer-calculator/" if lc == "en" else f"/{lc}/pioneer-calculator/"
            hreflangs.append(f'<link rel="alternate" hreflang="{ld.get("html_lang", lc)}" href="{lurl}">')
            active_style = 'background:#f3ecff;font-weight:700;' if lc == code else ''
            lang_links.append(f'<a href="{lhref}" style="text-decoration:none;color:#1f2937;padding:6px 8px;border-radius:8px;font-size:13px;white-space:nowrap;{active_style}">{ld.get("flag","")} {ld.get("name", lc)}</a>')
        page_html = calc_tpl
        repl = {
            "{{HTML_LANG}}": d.get("html_lang", code),
            "{{TITLE}}": cp["title"],
            "{{DESC}}": cp["desc"],
            "{{CANONICAL}}": canonical,
            "{{HREFLANGS}}": "\n  ".join(hreflangs),
            "{{GA_SCRIPT}}": get_ga_script() if "get_ga_script" in globals() else "",
            "{{HOME_URL}}": home_url,
            "{{BIBLE_URL}}": bible_url,
            "{{APP_STORE_URL}}": CFG.get("app_store_url", "https://apps.apple.com/us/app/jw-ministry/id6756040136"),
            "{{CURRENT_LANG_LABEL}}": f'{d.get("flag","")} {d.get("name", code)}',
            "{{LANG_LINKS}}": "\n".join(lang_links),
            "{{H1}}": cp["h1"],
            "{{INTRO}}": cp["intro"],
            "{{LABEL_GOAL}}": cp["label_goal"],
            "{{OPT_15}}": cp["opt_15"],
            "{{OPT_30}}": cp["opt_30"],
            "{{OPT_50}}": cp["opt_50"],
            "{{OPT_90}}": cp["opt_90"],
            "{{OPT_100}}": cp["opt_100"],
            "{{LABEL_DAYS}}": cp["label_days"],
            "{{RES_WEEK}}": cp["res_week"],
            "{{RES_DAY}}": cp["res_day"],
            "{{RES_YEAR}}": cp["res_year"],
            "{{UNIT_H}}": cp["unit_h"],
            "{{CTA_APP}}": cp["cta_app"],
            "{{CTA_BIBLE}}": cp["cta_bible"],
        }
        for k, v in repl.items():
            page_html = page_html.replace(k, str(v))
        with open(os.path.join(out_dir, "index.html"), "w", encoding="utf-8") as f:
            f.write(page_html)

# === Internal Linking Bar (Tools) ===
for code in CFG["supported_langs"]:
    with open(os.path.join(BASE, f"locales/{code}.json"), "r", encoding="utf-8") as _f:
        _d = json.load(_f)
    _cp = _d.get("calc_page", {})
    _bible_lbl = _cp.get("cta_bible", "Bible Reading Schedule")
    _calc_lbl = _cp.get("h1", "Pioneer Schedule Calculator")
    _bible_href = "/bible-reading-schedule/" if code == "en" else f"/{code}/bible-reading-schedule/"
    _calc_href = "/pioneer-calculator/" if code == "en" else f"/{code}/pioneer-calculator/"
    _idx_path = os.path.join(BASE, "index.html" if code == "en" else f"{code}/index.html")
    if os.path.exists(_idx_path):
        with open(_idx_path, "r", encoding="utf-8") as _hf:
            _html = _hf.read()
        if "jw-tools-bar" not in _html and "<footer" in _html:
            _bar = f"""
  <section class="jw-tools-bar" style="max-width:960px;margin:0 auto 36px;padding:0 20px;text-align:center;">
    <div style="display:flex;flex-wrap:wrap;justify-content:center;gap:12px;">
      <a href="{_bible_href}" style="display:inline-flex;align-items:center;gap:8px;padding:12px 20px;border-radius:14px;background:rgba(107,66,176,0.08);border:1px solid rgba(107,66,176,0.22);color:#4A2588;font-weight:600;font-size:15px;text-decoration:none;transition:all .2s ease;">📖 {_bible_lbl} →</a>
      <a href="{_calc_href}" style="display:inline-flex;align-items:center;gap:8px;padding:12px 20px;border-radius:14px;background:rgba(107,66,176,0.08);border:1px solid rgba(107,66,176,0.22);color:#4A2588;font-weight:600;font-size:15px;text-decoration:none;transition:all .2s ease;">⏱ {_calc_lbl} →</a>
    </div>
  </section>
"""
            _html = _html.replace("<footer", _bar + "<footer", 1)
            with open(_idx_path, "w", encoding="utf-8") as _hf:
                _hf.write(_html)
print(f"✅ Перелинковка на График чтения и Калькулятор добавлена на все {len(CFG['supported_langs'])} главных страниц!")
# === End Internal Linking Bar ===
