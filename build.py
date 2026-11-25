#!/usr/bin/env python3
import os
import json
from urllib.parse import quote

BASE = os.path.dirname(os.path.abspath(__file__))

with open(os.path.join(BASE, "config.json"), "r", encoding="utf-8") as f:
    CFG = json.load(f)

with open(os.path.join(BASE, "templates/page.html"), "r", encoding="utf-8") as f:
    TEMPLATE = f.read()

LANGS = {}
for code in CFG["supported_langs"]:
    with open(os.path.join(BASE, f"locales/{code}.json"), "r", encoding="utf-8") as f:
        LANGS[code] = json.load(f)

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
          <div class="iphone-frame"><img src="{src}" alt="{stitle} — JW Ministry" loading="lazy" width="320" height="690" /></div>
          <div class="shot-meta"><h3>{stitle}</h3><p>{sdesc}</p></div>
        </article>""")

    feats_html = [f'<div class="feat-card"><div class="feat-icon">{ic}</div><h3>{ft}</h3><p>{fd}</p></div>' for ic, ft, fd in d["features"]]
    seo_pillars_html = [f'<article class="seo-card"><h3>{pt}</h3><p>{pd}</p></article>' for pt, pd in d.get("seo_pillars", [])]
    seo_tags_html = [f'<span class="seo-tag">{tg}</span>' for tg in d.get("seo_tags", [])]
    badges_html = [f'<span class="loc-badge">{ln}</span>' for ln in CFG["all_35_languages"]]
    faqs_html = [f'<details class="faq-item"><summary>{q}</summary><p>{a}</p></details>' for q, a in d["faqs"]]

    schema = [
        {
            "@context": "https://schema.org",
            "@type": "MobileApplication",
            "name": "JW Ministry (Ministry Planner)",
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
        "{{FEATURES_GRID}}": "\n          ".join(feats_html),
        "{{SEO_PILLARS_GRID}}": "\n          ".join(seo_pillars_html),
        "{{SEO_TAGS_CLOUD}}": "\n            ".join(seo_tags_html),
        "{{LANG_BADGES}}": "\n            ".join(badges_html),
        "{{FAQ_LIST}}": "\n          ".join(faqs_html),
        "{{APP_STORE_ID}}": CFG["app_store_id"],
        "{{APP_STORE_URL}}": CFG["app_store_url"],
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

print("✅ Сборка завершена: index.html + 6 языковых папок успешно обновлены!")
