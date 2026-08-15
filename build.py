#!/usr/bin/env python3
"""
Yugmantra Organic — static site builder.
Emits index.html, shop.html, story.html, product-*.html, checkout.html,
thank-you.html, payment-failed.html from shared partials.

Run:  python3 build.py
"""
import os, json, re, html

ROOT = os.path.dirname(os.path.abspath(__file__))

# ---------------------------------------------------------------- catalogue
# Mirrors assets/js/catalog.js so pages can be pre-rendered.
def _load_catalog():
    """catalog.js is the single source of truth — evaluate it with Node and read it back."""
    import subprocess, tempfile
    js = (
        "global.window = {};\n"
        f"require({json.dumps(os.path.join(ROOT, 'assets', 'js', 'catalog.js'))});\n"
        "process.stdout.write(JSON.stringify({c: window.YM_CATALOG, r: window.YM_RULES}));\n"
    )
    with tempfile.NamedTemporaryFile("w", suffix=".js", delete=False) as fh:
        fh.write(js)
        tmp = fh.name
    try:
        out = subprocess.check_output(["node", tmp], text=True)
    finally:
        os.unlink(tmp)
    d = json.loads(out)
    return d["c"], d["r"]


CATALOG, RULES = _load_catalog()

WA = RULES["whatsapp"]
SUPPORT_MAIL = RULES["supportEmail"]
SUPPORT_TEL = RULES["supportPhone"]


def money(n):
    return "₹" + f"{n:,}".replace(",", ",")


# ---------------------------------------------------------------- chrome
def head(title, desc, page=""):
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<meta name="description" content="{desc}">
<meta name="theme-color" content="#F7F2E9">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{desc}">
<meta property="og:type" content="website">
<link rel="icon" href="assets/img/mark.svg" type="image/svg+xml">
<link rel="preload" href="assets/fonts/fraunces.woff2" as="font" type="font/woff2" crossorigin>
<link rel="preload" href="assets/fonts/inter.woff2" as="font" type="font/woff2" crossorigin>
<link rel="stylesheet" href="assets/css/site.css">
</head>
<body data-page="{page}">
"""


def nav_links(active):
    items = [("shop.html", "Shop"), ("story.html", "Our Story"),
             ("index.html#method", "The Method"), ("index.html#faq", "FAQ")]
    out = []
    for href, label in items:
        cur = ' aria-current="page"' if href == active else ""
        out.append(f'<a href="{href}"{cur}>{label}</a>')
    return "\n        ".join(out)


BRAND = """<a class="brandmark" href="index.html" aria-label="Yugmantra Organic — home">
        <img src="assets/img/mark.svg" alt="" width="60" height="60">
        <span class="brandmark__txt">
          <span class="brandmark__name">Yugmantra</span>
          <span class="brandmark__sub">Organic Foods · Alwar</span>
        </span>
      </a>"""


def header(active=""):
    return f"""
<header class="hdr">
  <div class="hdr__in">
    {BRAND}
    <nav class="nav" aria-label="Primary">
        {nav_links(active)}
    </nav>
    <div class="hdr__act">
      <button class="cartbtn" data-cart-open>
        Cart <span class="cartbtn__n hide" data-cart-count>0</span>
      </button>
      <button class="burger" data-burger aria-label="Menu"><span></span></button>
    </div>
  </div>
</header>

<nav class="mnav" aria-label="Mobile">
  <a href="shop.html" style="--d:.10s">Shop</a>
  <a href="story.html" style="--d:.16s">Our Story</a>
  <a href="index.html#method" style="--d:.22s">The Method</a>
  <a href="index.html#faq" style="--d:.28s">FAQ</a>
  <a href="index.html#contact" style="--d:.34s">Contact</a>
</nav>
"""


ARROW = '<svg width="13" height="10" viewBox="0 0 13 10" fill="none" stroke="currentColor" stroke-width="1.2"><path d="M0 5h11.5M8 1.5 11.5 5 8 8.5"/></svg>'
TICK = '<svg width="13" height="13" viewBox="0 0 13 13" fill="none" stroke="currentColor" stroke-width="1.4"><path d="M1 6.8 4.6 10.4 12 2.6"/></svg>'
STAR = '<svg width="12" height="12" viewBox="0 0 12 12" fill="currentColor"><path d="M6 0l1.6 3.9L12 4.4 8.8 7.3l.9 4.3L6 9.4l-3.7 2.2.9-4.3L0 4.4l4.4-.5z"/></svg>'


def cart_drawer():
    return f"""
<div class="scrim" data-cart-close></div>
<aside class="drawer" aria-label="Cart">
  <div class="drawer__hd">
    <h3>Your Order</h3>
    <button class="xbtn" data-cart-close aria-label="Close">
      <svg width="14" height="14" viewBox="0 0 14 14" stroke="currentColor" stroke-width="1.3"><path d="M1 1l12 12M13 1L1 13"/></svg>
    </button>
  </div>
  <div class="drawer__body" data-cart-body></div>
  <div class="drawer__ft hide" data-cart-foot>
    <div class="crow"><span>Subtotal</span><span data-sub>₹0</span></div>
    <div class="crow"><span>Delivery</span><span data-ship>—</span></div>
    <div class="crow crow--tot"><span>Total</span><b data-tot>₹0</b></div>
    <p class="small" style="margin:6px 0 16px" data-freeship></p>
    <a class="btn btn--block" href="checkout.html">Secure Checkout {ARROW}</a>
    <p class="small center" style="margin-top:14px">Payments by PayU · UPI, cards, netbanking &amp; wallets</p>
  </div>
</aside>
"""


def footer():
    return f"""
<footer class="ftr" id="contact">
  <div class="wrap">
    <div class="ftr__top">
      <div>
        {BRAND}
        <p class="small" style="max-width:34ch; margin-top:22px; color:rgba(247,242,233,.62)">
          Healthy living should be for all — not the preserve of the privileged.
          Hand-churned ghee and raw honey from Alwar, Rajasthan.
        </p>
        <div class="socials">
          <a href="https://www.instagram.com/yugmantraorganic/" aria-label="Instagram" target="_blank" rel="noopener">
            <svg width="16" height="16" viewBox="0 0 20 20" fill="none" stroke="currentColor" stroke-width="1.3"><rect x="2" y="2" width="16" height="16" rx="5"/><circle cx="10" cy="10" r="3.8"/><circle cx="14.8" cy="5.2" r=".9" fill="currentColor" stroke="none"/></svg>
          </a>
          <a href="https://www.facebook.com/yugmantraorganic/" aria-label="Facebook" target="_blank" rel="noopener">
            <svg width="16" height="16" viewBox="0 0 20 20" fill="currentColor"><path d="M11.5 18v-7h2.4l.4-2.8h-2.8V6.4c0-.8.2-1.4 1.4-1.4h1.5V2.6C14.1 2.5 13.2 2.4 12.2 2.4c-2.1 0-3.6 1.3-3.6 3.7v2.1H6.2V11h2.4v7z"/></svg>
          </a>
          <a href="https://www.youtube.com/@YugmantraOrganic" aria-label="YouTube" target="_blank" rel="noopener">
            <svg width="16" height="16" viewBox="0 0 20 20" fill="currentColor"><path d="M18.2 6.2a2.1 2.1 0 0 0-1.5-1.5C15.4 4.4 10 4.4 10 4.4s-5.4 0-6.7.3A2.1 2.1 0 0 0 1.8 6.2C1.5 7.5 1.5 10 1.5 10s0 2.5.3 3.8a2.1 2.1 0 0 0 1.5 1.5c1.3.3 6.7.3 6.7.3s5.4 0 6.7-.3a2.1 2.1 0 0 0 1.5-1.5c.3-1.3.3-3.8.3-3.8s0-2.5-.3-3.8zM8.3 12.6V7.4l4.5 2.6z"/></svg>
          </a>
          <a href="https://wa.me/{WA}" aria-label="WhatsApp" target="_blank" rel="noopener">
            <svg width="16" height="16" viewBox="0 0 20 20" fill="currentColor"><path d="M10 1.7a8.2 8.2 0 0 0-7 12.5L1.7 18.3l4.2-1.3A8.2 8.2 0 1 0 10 1.7zm0 1.6a6.6 6.6 0 1 1-3.4 12.2l-.3-.2-2.5.8.8-2.4-.2-.3A6.6 6.6 0 0 1 10 3.3zm-2.9 3c-.2 0-.4 0-.6.3-.2.3-.8.8-.8 1.9s.8 2.2.9 2.4c.1.1 1.5 2.5 3.8 3.4 1.9.8 2.3.6 2.7.6.4 0 1.3-.5 1.5-1.1.2-.5.2-1 .1-1.1l-.5-.3-1.5-.7c-.2-.1-.4-.1-.5.1l-.7.9c-.1.2-.3.2-.5.1-.2-.1-1-.4-1.9-1.2-.7-.6-1.2-1.4-1.3-1.6-.1-.2 0-.3.1-.4l.4-.5.2-.4v-.4l-.7-1.7c-.2-.4-.4-.3-.5-.3z"/></svg>
          </a>
        </div>
      </div>

      <div>
        <h4 class="ftr__h">Shop</h4>
        <ul>
          <li><a href="product-gir-a2-ghee.html">Gir A2 Bilona Ghee</a></li>
          <li><a href="product-sahiwal-a2-ghee.html">Sahiwal A2 Bilona Ghee</a></li>
          <li><a href="product-desi-buffalo-ghee.html">Desi Buffalo Ghee</a></li>
          <li><a href="product-ashwagandha-raw-honey.html">Ashwagandha Raw Honey</a></li>
          <li><a href="shop.html">All products</a></li>
        </ul>
      </div>

      <div>
        <h4 class="ftr__h">Company</h4>
        <ul>
          <li><a href="story.html">Our story</a></li>
          <li><a href="index.html#method">The bilona method</a></li>
          <li><a href="index.html#faq">FAQ &amp; delivery</a></li>
          <li><a href="mailto:{SUPPORT_MAIL}">Wholesale enquiries</a></li>
          <li><a href="https://wa.me/{WA}" target="_blank" rel="noopener">WhatsApp us</a></li>
        </ul>
      </div>

      <div>
        <h4 class="ftr__h">Kitchen Notes</h4>
        <p class="small" style="color:rgba(247,242,233,.62); margin-bottom:14px">
          One letter a month — what's in season, how we cook it, and first access to small batches.
        </p>
        <form class="nl" onsubmit="event.preventDefault(); this.querySelector('input').value=''; this.nextElementSibling.hidden=false;">
          <input type="email" required placeholder="your@email.com" aria-label="Email address">
          <button type="submit" aria-label="Subscribe">{ARROW}</button>
        </form>
        <p class="small" hidden style="margin-top:10px; color:#E8B84B">Thank you — you're on the list.</p>
        <h4 class="ftr__h" style="margin-top:30px">Reach Us</h4>
        <ul>
          <li><a href="tel:{SUPPORT_TEL.replace(' ', '')}">{SUPPORT_TEL}</a></li>
          <li><a href="mailto:{SUPPORT_MAIL}">{SUPPORT_MAIL}</a></li>
          <li style="color:rgba(247,242,233,.62)">Alwar, Rajasthan 301001</li>
        </ul>
      </div>
    </div>

    <div class="ftr__bot">
      <span>© <span data-year>2026</span> Yugmantra Organic Foods. All rights reserved.</span>
      <div class="paylogos"><span>Secured by PayU</span><span>·</span><span>UPI</span><span>Visa</span><span>Mastercard</span><span>Rupay</span><span>Netbanking</span></div>
    </div>
  </div>
</footer>

<script src="assets/js/catalog.js"></script>
<script src="assets/js/site.js"></script>
</body>
</html>
"""


def pcard(p, delay=0):
    tag = ""
    if p.get("tag"):
        cls = "pcard__tag pcard__tag--gold" if p.get("tagStyle") == "gold" else "pcard__tag"
        tag = f'<span class="{cls}">{p["tag"]}</span>'
    mrp = f'<s>{money(p["mrp"])}</s>' if p.get("mrp") and p["mrp"] > p["price"] else ""
    return f"""
      <article class="pcard rv rv-d{delay}">
        <a class="pcard__media" href="product-{p['slug']}.html" aria-label="{p['name']}">
          {tag}
          <img src="{p['img']}" alt="{p['name']} in a glass jar" loading="lazy">
        </a>
        <div class="pcard__body">
          <span class="pcard__meta">{p['line']}</span>
          <h3 class="pcard__name"><a href="product-{p['slug']}.html">{p['name']}</a></h3>
          <p class="pcard__desc">{p['short']}</p>
          <div class="pcard__foot">
            <span class="price">{money(p['price'])} {mrp}<br><span class="pcard__meta">{p['size']}</span></span>
            <button class="btn" data-add="{p['sku']}">Add</button>
          </div>
        </div>
      </article>"""


# ---------------------------------------------------------------- index
def build_index():
    ghee = [p for p in CATALOG if not p.get("secondary")]
    cards = "\n".join(pcard(p, i + 1) for i, p in enumerate(ghee[:3]))

    marquee = ["A2 milk, never mixed", "Hand-churned in clay", "25 litres of milk per litre of ghee",
               "No preservatives, no colour", "Glass, never plastic", "Made in small batches",
               "Alwar, Rajasthan"]
    marq = "".join(f'<span class="marq__item">{m}</span>' for m in marquee)

    steps = [
        ("01", "The Grazing", "Our cows graze open pasture, not feedlots. What they eat is what ends up in the jar — so we start there."),
        ("02", "The Morning Milk", "Milked at dawn and set the same hour. Milk that waits is milk that loses."),
        ("03", "The Curd", "Set overnight with a live culture. Twelve hours, no shortcuts. This is the step industry skips."),
        ("04", "The Churn", "Curd — not cream — churned by hand in a clay pot until the butter lifts and separates."),
        ("05", "The Slow Flame", "Simmered low until the water leaves and the grain forms. Poured hot into glass. Sealed."),
    ]
    procs = "\n".join(f"""
        <div class="proc__step rv rv-d{i+1}">
          <span class="proc__n">{n}</span>
          <span class="proc__t">{t}</span>
          <p class="proc__d">{d}</p>
        </div>""" for i, (n, t, d) in enumerate(steps))

    cmp_rows = [
        ("What is churned", "Cultured curd, whole", "Cream skimmed off milk"),
        ("How it is churned", "By hand, in clay, slow", "Steel centrifuge, minutes"),
        ("Milk needed per litre", "≈ 25 litres", "≈ 12–15 litres"),
        ("Texture when set", "Grainy, crystalline", "Smooth, uniform paste"),
        ("Aroma", "Nutty, carries across a room", "Faint, often flat"),
        ("Time per batch", "Two days", "Under two hours"),
        ("What goes in", "Milk", "Milk, sometimes more"),
    ]
    cmp_html = "\n".join(
        f"<tr><th>{a}</th><td>{b}</td><td>{c}</td></tr>" for a, b, c in cmp_rows)

    # NOTE: replace with genuine verified reviews before launch — see README.
    tests = [
        ("I grew up in a house where ghee was made at home every fortnight. This is the first jar I've bought that smells the way that kitchen smelled.",
         "Verified buyer · Jaipur"),
        ("I ordered the Gir expecting the usual supermarket disappointment. It arrived grainy and yellow and my mother asked which village it came from.",
         "Verified buyer · Bengaluru"),
        ("Third litre now. My daughter has it on roti every morning. The jar is glass, the seal is proper, and it has never once arrived leaking.",
         "Verified buyer · Delhi NCR"),
    ]
    tests_html = "\n".join(f"""
        <figure class="test rv rv-d{i+1}">
          <div class="stars" aria-label="5 out of 5">{STAR*5}</div>
          <p>“{q}”</p>
          <footer>{a}</footer>
        </figure>""" for i, (q, a) in enumerate(tests))

    faqs = [
        ("What actually is the bilona method, and why does it cost more?",
         "Bilona means the whole milk is first set into curd, and that curd — not cream — is churned to butter, which is then simmered into ghee. It takes about two days and roughly twice the milk of the industrial cream-separator route. That is the entire reason it costs what it costs. There is no way to make it cheaper without making it something else."),
        ("Why is my ghee grainy? Is that a fault?",
         "It is the opposite of a fault. Grain forms when ghee is cooled slowly and has not been emulsified or adulterated. A perfectly smooth, uniform ghee at room temperature usually means it was rushed or blended. In Indian summers our ghee will go liquid and clear; in winter it sets grainy and pale. Both are correct."),
        ("What is A2, in plain language?",
         "A2 refers to a form of beta-casein protein found in the milk of indigenous Indian breeds like Gir and Sahiwal, as opposed to the A1 variant common in high-yield crossbred herds. Many people report finding A2 milk products easier to digest. We are not making a medical claim — we are telling you which cow the milk came from, which most brands will not."),
        ("Does it need refrigeration?",
         "No. Keep it in a cool, dark cupboard away from the stove, and always use a dry spoon. Water is the only real enemy. Unopened, it keeps twelve months; opened and kept dry, it will comfortably outlive that."),
        ("How fast do you ship, and where?",
         f"We dispatch within 24–48 hours of your order from Alwar and deliver across India, typically in 3–6 working days. Delivery is free on orders above {money(RULES['freeShipOver'])}; below that it is a flat {money(RULES['shipFlat'])}. Every jar ships double-boxed with a tamper seal."),
        ("What if the jar arrives broken?",
         f"Send a photo to {SUPPORT_MAIL} or WhatsApp us within 48 hours of delivery and we replace it, no argument and no return shipment required. Glass is worth the small risk and we carry that risk, not you."),
        ("How do I pay?",
         "Checkout runs on PayU, so you can pay by UPI, credit or debit card, netbanking or wallet. Card details never touch our servers."),
    ]
    faq_html = "\n".join(f"""
      <div class="faq__i">
        <button class="faq__q" data-faq aria-expanded="false">{q}<span class="faq__ic"></span></button>
        <div class="faq__a"><div>{a}</div></div>
      </div>""" for q, a in faqs)

    return head(
        "Yugmantra Organic — Bilona A2 Ghee, Hand-Churned in Alwar",
        "Grass-fed A2 Gir and Sahiwal cow ghee, hand-churned from cultured curd in clay pots and simmered slow. 25 litres of milk per litre. No additives. Made in small batches in Alwar, Rajasthan.",
        "home") + header("index.html") + f"""

<main>

  <!-- ================= HERO ================= -->
  <section class="hero">
    <div class="wrap hero__grid">
      <div>
        <span class="eyebrow fade-up" style="--d:.15s">Alwar, Rajasthan · Since 2019</span>
        <h1 class="display d1">
          <span class="ln"><span style="--d:.05s">Ghee the way</span></span>
          <span class="ln"><span style="--d:.17s">your grandmother</span></span>
          <span class="ln"><span style="--d:.29s">would recognise&nbsp;it.</span></span>
        </h1>
        <p class="lede hero__sub fade-up" style="--d:.5s">
          Whole milk from free-grazing Gir and Sahiwal cows, set to curd overnight,
          churned by hand in a clay pot, and simmered on a slow flame until it turns
          golden and grainy. Twenty-five litres of milk make one litre.
          Nothing else goes in.
        </p>
        <div class="hero__cta fade-up" style="--d:.66s">
          <a class="btn btn--lg" href="shop.html">Shop the range {ARROW}</a>
          <a class="btn btn--ghost btn--lg" href="#method">See how it's made</a>
        </div>
        <div class="pill-row fade-up" style="--d:.8s; margin-top:34px">
          <span class="badge">{TICK} A2 milk</span>
          <span class="badge">{TICK} No preservatives</span>
          <span class="badge">{TICK} Glass jar</span>
        </div>
      </div>

      <div class="hero__art">
        <span class="halo"></span>
        <img src="assets/img/jar-gir.svg" alt="Yugmantra Gir A2 bilona ghee in a glass jar" width="520" height="700">
        <img class="hero__seal" src="assets/img/seal.svg" alt="" width="200" height="200" aria-hidden="true">
      </div>
    </div>

    <div class="scrollcue"><i></i> Scroll</div>
  </section>

  <!-- ================= MARQUEE ================= -->
  <div class="marq" aria-hidden="true"><div class="marq__track">{marq}</div></div>

  <!-- ================= STATEMENT ================= -->
  <section class="section">
    <div class="wrap center">
      <p class="display d2 rv measure mx-auto" style="max-width:20ch">
        Most ghee is a <span class="gold italic">by-product.</span> Ours is the
        <span class="gold italic">point.</span>
      </p>
      <p class="lede rv rv-d2 measure mx-auto" style="margin-top:34px">
        Industrial ghee is what remains after the valuable parts of milk have been
        sold off elsewhere — skimmed cream, spun in a centrifuge, deodorised and
        packed in plastic within two hours. We do the slow, expensive, older thing
        instead, because it is the only way to get the grain, the colour and the smell.
      </p>
    </div>
  </section>

  <!-- ================= RANGE ================= -->
  <section class="section section--tight" id="range">
    <div class="wrap">
      <div class="sechead">
        <span class="eyebrow eyebrow--gold rv">The Range</span>
        <div class="split" style="align-items:end; gap:32px">
          <h2 class="display d2 rv">Three jars.<br>No compromises.</h2>
          <p class="lede rv rv-d2" style="max-width:44ch">
            We make a small number of things and we make them the long way.
            Every jar is filled hot, sealed by hand and labelled with the batch it came from.
          </p>
        </div>
      </div>
      <div class="prods">{cards}</div>
      <div class="center" style="margin-top:44px">
        <a class="tlink rv" href="shop.html">View the full range {ARROW}</a>
      </div>
    </div>
  </section>

  <!-- ================= METHOD ================= -->
  <section class="section" id="method" style="background:linear-gradient(180deg,transparent,rgba(232,221,201,.5))">
    <div class="wrap">
      <div class="sechead center">
        <span class="eyebrow eyebrow--gold rv">The Bilona Method</span>
        <h2 class="display d2 rv">Two days, five steps,<br>one ingredient.</h2>
      </div>
      <div class="proc">{procs}</div>
      <p class="small center rv" style="margin-top:34px">
        Steps 03 and 04 are the ones industry removes. Removing them is what makes ghee cheap.
      </p>
    </div>
  </section>

  <!-- ================= COW ================= -->
  <section class="section">
    <div class="wrap split">
      <div class="split__media rv">
        <img src="assets/img/plate-cow.svg" alt="Desi cows grazing open pasture at dawn" loading="lazy">
      </div>
      <div>
        <span class="eyebrow eyebrow--gold rv">Why The Cow Matters</span>
        <h2 class="display d3 rv rv-d1" style="margin:20px 0 24px">
          A high-yield cow makes<br>more milk. Not better milk.
        </h2>
        <p class="lede rv rv-d2">
          Gir and Sahiwal are indigenous Indian breeds. They give a fraction of the
          milk a crossbred herd does, which is precisely why almost nobody keeps them
          commercially any more. Their milk carries A2 beta-casein and noticeably more
          carotene — which is where the yellow comes from. You cannot add that colour
          later. You can only start with the right cow.
        </p>
        <div class="stat-row rv rv-d3">
          <div><div class="stat__n">A2</div><div class="stat__l">Beta-casein milk</div></div>
          <div><div class="stat__n">100%</div><div class="stat__l">Open grazed</div></div>
          <div><div class="stat__n">0</div><div class="stat__l">Additives, ever</div></div>
        </div>
        <div class="rv rv-d4" style="margin-top:38px">
          <a class="tlink" href="story.html">Read the full story {ARROW}</a>
        </div>
      </div>
    </div>
  </section>

  <!-- ================= COMPARISON ================= -->
  <section class="section section--tight">
    <div class="wrap">
      <div class="sechead center">
        <span class="eyebrow eyebrow--gold rv">Honest Comparison</span>
        <h2 class="display d3 rv">What you are actually paying for</h2>
      </div>
      <div class="rv" style="overflow-x:auto">
        <table class="cmp">
          <thead>
            <tr><th></th><th>Bilona ghee (ours)</th><th>Cream-separator ghee</th></tr>
          </thead>
          <tbody>{cmp_html}</tbody>
        </table>
      </div>
      <p class="small center rv" style="margin-top:22px; max-width:60ch; margin-inline:auto">
        Cream-separator ghee is not fraudulent — it is simply a different, faster product.
        We think you should know which one is in your jar.
      </p>
    </div>
  </section>

  <!-- ================= POUR / YIELD ================= -->
  <section class="section">
    <div class="wrap split split--rev">
      <div class="split__media rv">
        <img src="assets/img/plate-pour.svg" alt="Golden ghee pouring from a spoon" loading="lazy">
      </div>
      <div>
        <span class="eyebrow eyebrow--gold rv">The Arithmetic</span>
        <h2 class="display d3 rv rv-d1" style="margin:20px 0 24px">
          Twenty-five litres of milk.<br>One litre of ghee.
        </h2>
        <p class="lede rv rv-d2">
          That ratio is not marketing — it is the reason a real jar of bilona ghee
          cannot be sold for a few hundred rupees. Curd yields less butter than cream
          does, hand-churning leaves some behind, and a slow flame drives off more water.
          Every one of those losses is deliberate. Each one is also where the flavour comes from.
        </p>
        <ul class="acc-list rv rv-d3" style="margin-top:30px">
          <li>{TICK} <span>Filled hot into glass — never plastic, never a pouch</span></li>
          <li>{TICK} <span>Batch number on every label, traceable to the week it was made</span></li>
          <li>{TICK} <span>Double-boxed with a tamper seal; breakage replaced free</span></li>
          <li>{TICK} <span>No refrigeration needed — twelve months in a dark cupboard</span></li>
        </ul>
      </div>
    </div>
  </section>

  <!-- ================= QUOTE ================= -->
  <section class="section quote">
    <div class="wrap quote__in">
      <blockquote>Healthy living should be for all — not the preserve of the privileged.</blockquote>
      <cite>The founding idea, unchanged since 2019</cite>
    </div>
  </section>

  <!-- ================= TESTIMONIALS ================= -->
  <section class="section">
    <div class="wrap">
      <div class="sechead center">
        <span class="eyebrow eyebrow--gold rv">From The Kitchen Table</span>
        <h2 class="display d3 rv">What people write back</h2>
      </div>
      <div class="tests">{tests_html}</div>
    </div>
  </section>

  <!-- ================= FAQ ================= -->
  <section class="section section--tight" id="faq">
    <div class="wrap">
      <div class="sechead">
        <span class="eyebrow eyebrow--gold rv">Questions</span>
        <h2 class="display d3 rv">The things worth asking</h2>
      </div>
      <div class="faq rv">{faq_html}</div>
    </div>
  </section>

  <!-- ================= CTA ================= -->
  <section class="section" style="background:linear-gradient(180deg,transparent,rgba(232,184,75,.16))">
    <div class="wrap center">
      <span class="eyebrow eyebrow--gold rv">Start Here</span>
      <h2 class="display d2 rv rv-d1" style="margin:20px auto 26px; max-width:16ch">
        Try one jar. You will know within a spoon.
      </h2>
      <p class="lede rv rv-d2 measure mx-auto" style="margin-bottom:36px">
        If it does not smell like the ghee you remember, write to us and we will make it right.
      </p>
      <div class="hero__cta rv rv-d3" style="justify-content:center">
        <a class="btn btn--lg" href="shop.html">Shop the range {ARROW}</a>
        <a class="btn btn--ghost btn--lg" href="https://wa.me/{WA}" target="_blank" rel="noopener">Ask us on WhatsApp</a>
      </div>
    </div>
  </section>

</main>
""" + cart_drawer() + footer()


# ---------------------------------------------------------------- shop
def build_shop():
    ghee = [p for p in CATALOG if not p.get("secondary")]
    pantry = [p for p in CATALOG if p.get("secondary")]
    g = "\n".join(pcard(p, (i % 3) + 1) for i, p in enumerate(ghee))
    pn = "\n".join(pcard(p, (i % 3) + 1) for i, p in enumerate(pantry))

    return head("Shop — Yugmantra Organic",
                "Buy A2 Gir and Sahiwal bilona ghee, desi buffalo ghee and raw infused honey. Free delivery across India above ₹999.",
                "shop") + header("shop.html") + f"""
<main>
  <section class="section" style="padding-top:clamp(130px,15vh,190px)">
    <div class="wrap">
      <div class="sechead">
        <span class="eyebrow eyebrow--gold rv">The Range</span>
        <div class="split" style="align-items:end; gap:32px">
          <h1 class="display d2 rv">Every jar,<br>made the long way.</h1>
          <p class="lede rv rv-d2" style="max-width:46ch">
            Free delivery across India on orders above {money(RULES['freeShipOver'])}.
            Dispatched from Alwar within 24–48 hours. Breakage replaced free.
          </p>
        </div>
      </div>
      <div class="prods">{g}</div>
    </div>
  </section>

  <div class="wrap"><hr class="rule"></div>

  <section class="section section--tight">
    <div class="wrap">
      <div class="sechead">
        <span class="eyebrow eyebrow--gold rv">Also From The Pantry</span>
        <h2 class="display d3 rv">A short shelf of other things</h2>
      </div>
      <div class="prods">{pn}</div>
    </div>
  </section>

  <div class="marq" aria-hidden="true"><div class="marq__track">
    <span class="marq__item">Free delivery above {money(RULES['freeShipOver'])}</span>
    <span class="marq__item">Dispatched in 24–48 hours</span>
    <span class="marq__item">Breakage replaced free</span>
    <span class="marq__item">Pay by UPI, card or netbanking</span>
    <span class="marq__item">Glass, never plastic</span>
  </div></div>

  <section class="section">
    <div class="wrap center">
      <h2 class="display d3 rv" style="max-width:20ch; margin-inline:auto">Not sure which cow to start with?</h2>
      <p class="lede rv rv-d2 measure mx-auto" style="margin:22px auto 32px">
        Gir is deeper, nuttier and more aromatic — the one to spoon over dal at the table.
        Sahiwal is milder and creamier — the everyday jar. Buffalo is white and neutral, for mithai and frying.
      </p>
      <a class="btn rv rv-d3" href="https://wa.me/{WA}" target="_blank" rel="noopener">Ask us on WhatsApp {ARROW}</a>
    </div>
  </section>
</main>
""" + cart_drawer() + footer()


# ---------------------------------------------------------------- product
def build_product(p):
    others = [q for q in CATALOG if q["sku"] != p["sku"]][:3]
    rel = "\n".join(pcard(q, i + 1) for i, q in enumerate(others))

    sizes = [q for q in CATALOG if q["slug"].startswith(p["slug"].split("-litre")[0])
             and q["name"] == p["name"]]
    if len(sizes) > 1:
        opts = "".join(
            f'<a class="opt {"on" if q["sku"]==p["sku"] else ""}" href="product-{q["slug"]}.html">'
            f'{q["size"]}<small>{money(q["price"])}</small></a>' for q in sizes)
        opt_block = f'<div><span class="eyebrow">Size</span><div class="opts">{opts}</div></div>'
    else:
        opt_block = f'<div><span class="eyebrow">Size</span><div class="opts"><span class="opt on">{p["size"]}<small>{money(p["price"])}</small></span></div></div>'

    notes = "".join(f"<li>{TICK} <span>{n}</span></li>" for n in p["notes"])
    specs = "".join(f"<tr><th>{a}</th><td colspan='2'>{b}</td></tr>" for a, b in p["specs"])
    body = "".join(f"<p style='margin-bottom:18px'>{para}</p>" for para in p["long"].split("\n\n"))
    mrp = f'<s>{money(p["mrp"])}</s>' if p.get("mrp") and p["mrp"] > p["price"] else ""
    save_pct = round((1 - p["price"] / p["mrp"]) * 100) if p.get("mrp") else 0

    ld = json.dumps({
        "@context": "https://schema.org", "@type": "Product", "name": p["name"],
        "description": p["short"], "brand": {"@type": "Brand", "name": "Yugmantra Organic Foods"},
        "sku": p["sku"],
        "offers": {"@type": "Offer", "priceCurrency": "INR", "price": p["price"],
                   "availability": "https://schema.org/InStock"}
    }, ensure_ascii=False)

    return head(f"{p['name']} {p['size']} — Yugmantra Organic",
                p["short"], "product") + header("shop.html") + f"""
<script type="application/ld+json">{ld}</script>
<main>
  <div class="wrap pdp">

    <div class="pdp__gal">
      <div class="pdp__hero rv">
        <img src="{p['img']}" alt="{p['name']} in a glass jar" width="520" height="700">
      </div>
      <div class="thumbs rv rv-d1">
        <span class="thumb thumb--jar on"><img src="{p['img']}" alt=""></span>
        <span class="thumb"><img src="assets/img/plate-bilona.svg" alt=""></span>
        <span class="thumb"><img src="assets/img/plate-pour.svg" alt=""></span>
        <span class="thumb"><img src="assets/img/plate-cow.svg" alt=""></span>
      </div>
    </div>

    <div>
      <a class="small" href="shop.html" style="letter-spacing:.14em; text-transform:uppercase; font-size:.66rem">← All products</a>
      <span class="eyebrow eyebrow--gold rv" style="display:block; margin-top:22px">{p['line']}</span>
      <h1 class="display d2 rv rv-d1" style="margin:14px 0 18px">{p['name']}</h1>

      <div class="stars rv rv-d1" style="margin-bottom:18px">{STAR*5} <span class="small" style="margin-left:9px">Rated by our customers</span></div>

      <p class="lede rv rv-d2">{p['short']}</p>

      <div class="rv rv-d2" style="display:flex; align-items:baseline; gap:14px; margin:28px 0 6px">
        <span class="price" style="font-size:2rem">{money(p['price'])}</span>
        <span class="small">{mrp} {"· save " + str(save_pct) + "%" if save_pct else ""}</span>
      </div>
      <p class="small rv rv-d2" style="margin-bottom:26px">{p['unit']} · inclusive of all taxes</p>

      <div class="rv rv-d3">{opt_block}</div>

      <div class="rv rv-d3" style="display:flex; gap:12px; align-items:stretch; margin-top:26px; flex-wrap:wrap">
        <div class="qty" style="margin:0; padding:4px 6px">
          <button data-qty-dn aria-label="Decrease">−</button>
          <span data-qty-val>1</span>
          <button data-qty-up aria-label="Increase">+</button>
        </div>
        <button class="btn btn--lg" data-add="{p['sku']}" style="flex:1; min-width:200px">Add to bag — {money(p['price'])}</button>
      </div>
      <p class="small rv rv-d3" style="margin-top:14px">
        Free delivery above {money(RULES['freeShipOver'])} · dispatched in 24–48 hrs · breakage replaced free
      </p>

      <ul class="acc-list rv rv-d4" style="margin-top:34px">{notes}</ul>

      <div class="rv rv-d4" style="margin-top:40px">
        <h2 class="display d4" style="margin-bottom:16px">The long version</h2>
        <div class="lede">{body}</div>
      </div>

      <div class="rv rv-d5" style="margin-top:40px">
        <h2 class="display d4" style="margin-bottom:4px">Specification</h2>
        <table class="cmp"><tbody>{specs}</tbody></table>
      </div>

      <p class="small rv" style="margin-top:30px">
        Questions about this jar? <a class="tlink" href="https://wa.me/{WA}" target="_blank" rel="noopener">WhatsApp us {ARROW}</a>
      </p>
    </div>
  </div>

  <section class="section">
    <div class="wrap">
      <div class="sechead"><span class="eyebrow eyebrow--gold rv">Also Consider</span></div>
      <div class="prods">{rel}</div>
    </div>
  </section>
</main>
""" + cart_drawer() + footer()


# ---------------------------------------------------------------- story
def build_story():
    return head("Our Story — Yugmantra Organic",
                "Why we make ghee the long way in Alwar, Rajasthan — the cows, the clay pots, and the arithmetic behind the jar.",
                "story") + header("story.html") + f"""
<main>
  <section class="section" style="padding-top:clamp(140px,16vh,200px); padding-bottom:clamp(40px,5vw,70px)">
    <div class="wrap center">
      <span class="eyebrow eyebrow--gold rv">Alwar, Rajasthan · Est. 2019</span>
      <h1 class="display d1 rv rv-d1" style="margin:24px auto; max-width:14ch">The slow way, on purpose.</h1>
      <p class="lede rv rv-d2 measure mx-auto">
        Yugmantra began with a small complaint: that the ghee sold everywhere had stopped
        smelling like ghee. Everything we have built since is an answer to that.
      </p>
    </div>
  </section>

  <section class="section" style="padding-top:0">
    <div class="wrap">
      <div class="split__media rv" style="aspect-ratio:16/9; border-radius:3px">
        <img src="assets/img/plate-kitchen.svg" alt="Jars of ghee and honey on a wooden shelf" loading="lazy">
      </div>
    </div>
  </section>

  <section class="section section--tight">
    <div class="wrap" style="max-width:760px">
      <h2 class="display d3 rv" style="margin-bottom:26px">It started with a smell that had gone missing</h2>
      <div class="lede rv rv-d1" style="display:grid; gap:20px">
        <p>Anyone who grew up in an Indian household before the nineties can describe the smell of ghee being made — the sharp cultured note of the curd, the slap of the wooden churn, then the long nutty warmth that took over the whole house for an afternoon.</p>
        <p>Somewhere in the decades that followed, that smell left most kitchens. Not because people stopped buying ghee. Because the way it was made changed. Cream separators replaced clay pots. Crossbred herds replaced desi cows. Two days of work became ninety minutes. The jar on the shelf still said ghee, and it still cost money, but it no longer did the one thing ghee is supposed to do, which is announce itself.</p>
        <p>We started Yugmantra in Alwar in 2019 to make the older version again, on a scale small enough that we could keep doing it properly.</p>
      </div>
    </div>
  </section>

  <section class="section" style="padding-top:0">
    <div class="wrap split">
      <div class="split__media rv"><img src="assets/img/plate-bilona.svg" alt="A clay pot and wooden churn" loading="lazy"></div>
      <div>
        <span class="eyebrow eyebrow--gold rv">What We Refuse To Change</span>
        <h2 class="display d3 rv rv-d1" style="margin:20px 0 22px">Curd, not cream.<br>Clay, not steel.</h2>
        <p class="lede rv rv-d2">
          The single decision that defines this business is that we churn cultured curd rather
          than skimmed cream. It costs us roughly twice the milk and two days per batch instead
          of two hours. Every commercial argument says not to do it. It is the only way to get
          the grain and the aroma, so we do it anyway.
        </p>
        <p class="lede rv rv-d3" style="margin-top:18px">
          The clay pot is not nostalgia either — it holds temperature gently and does not
          shear the butter the way a steel centrifuge does. Old methods survive when they work.
        </p>
      </div>
    </div>
  </section>

  <section class="section quote">
    <div class="wrap quote__in">
      <blockquote>We would rather make less of something real than more of something convincing.</blockquote>
      <cite>Yugmantra Organic Foods</cite>
    </div>
  </section>

  <section class="section">
    <div class="wrap">
      <div class="sechead center">
        <span class="eyebrow eyebrow--gold rv">What We Promise</span>
        <h2 class="display d3 rv">Four things, plainly stated</h2>
      </div>
      <div class="prods" style="grid-template-columns:repeat(2,1fr)">
        <div class="test rv rv-d1"><span class="proc__n">01</span><p><b>We tell you the breed.</b> Gir, Sahiwal or buffalo — named on the jar. Never a blend sold as a mystery.</p></div>
        <div class="test rv rv-d2"><span class="proc__n">02</span><p><b>One ingredient.</b> Milk. No vegetable fat, no colour, no preservative, no flavouring. Read the label and there is nothing to read.</p></div>
        <div class="test rv rv-d3"><span class="proc__n">03</span><p><b>Glass, always.</b> Fat draws compounds out of plastic over months. Glass costs more to ship and breaks more often. We ship glass.</p></div>
        <div class="test rv rv-d4"><span class="proc__n">04</span><p><b>Small batches, dated.</b> Every jar carries the batch it came from. If a batch is off, we can find it — and so can you.</p></div>
      </div>
    </div>
  </section>

  <section class="section" style="background:linear-gradient(180deg,transparent,rgba(232,184,75,.16))">
    <div class="wrap center">
      <h2 class="display d2 rv" style="max-width:16ch; margin-inline:auto">Come and taste the difference.</h2>
      <div class="hero__cta rv rv-d2" style="justify-content:center; margin-top:34px">
        <a class="btn btn--lg" href="shop.html">Shop the range {ARROW}</a>
        <a class="btn btn--ghost btn--lg" href="https://wa.me/{WA}" target="_blank" rel="noopener">Talk to us</a>
      </div>
    </div>
  </section>
</main>
""" + cart_drawer() + footer()


# ---------------------------------------------------------------- checkout
def build_checkout():
    return head("Checkout — Yugmantra Organic",
                "Secure checkout powered by PayU. UPI, cards, netbanking and wallets.",
                "checkout") + header() + f"""
<main>
  <section class="section" style="padding-top:clamp(130px,15vh,180px)">
    <div class="wrap">
      <div class="sechead">
        <span class="eyebrow eyebrow--gold">Checkout</span>
        <h1 class="display d2">Almost yours.</h1>
      </div>

      <form class="split" data-checkout-form method="POST" action="server/payu-initiate.php" style="align-items:start">

        <!-- ---------- details ---------- -->
        <div>
          <h2 class="display d4" style="margin-bottom:22px">Delivery details</h2>

          <div class="field--row">
            <div class="field"><label for="fn">First name</label><input id="fn" name="firstname" required autocomplete="given-name"></div>
            <div class="field"><label for="ln">Last name</label><input id="ln" name="lastname" autocomplete="family-name"></div>
          </div>
          <div class="field--row">
            <div class="field"><label for="em">Email</label><input id="em" type="email" name="email" required autocomplete="email"></div>
            <div class="field"><label for="ph">Mobile</label><input id="ph" type="tel" name="phone" required pattern="[0-9+ ]{{10,15}}" autocomplete="tel"></div>
          </div>
          <div class="field"><label for="a1">Address</label><input id="a1" name="address1" required autocomplete="address-line1"></div>
          <div class="field"><label for="a2">Apartment, landmark <span style="text-transform:none; letter-spacing:0">(optional)</span></label><input id="a2" name="address2" autocomplete="address-line2"></div>
          <div class="field--row">
            <div class="field"><label for="ct">City</label><input id="ct" name="city" required autocomplete="address-level2"></div>
            <div class="field"><label for="st">State</label><input id="st" name="state" required autocomplete="address-level1"></div>
          </div>
          <div class="field--row">
            <div class="field"><label for="zp">PIN code</label><input id="zp" name="zipcode" required pattern="[0-9]{{6}}" autocomplete="postal-code"></div>
            <div class="field"><label for="cn">Country</label><input id="cn" name="country" value="India" readonly></div>
          </div>
          <div class="field"><label for="nt">Order note <span style="text-transform:none; letter-spacing:0">(optional)</span></label><textarea id="nt" name="udf1" rows="3" placeholder="Gate code, preferred delivery time…"></textarea></div>

          <!-- filled in by site.js -->
          <input type="hidden" name="productinfo" value="">
          <input type="hidden" name="amount" value="0.00">
          <input type="hidden" name="cart_json" value="[]">
        </div>

        <!-- ---------- summary ---------- -->
        <aside style="background:var(--paper); border:1px solid var(--rule-soft); border-radius:3px; padding:30px 28px; position:sticky; top:110px">
          <h2 class="display d4" style="margin-bottom:20px">Your order</h2>
          <div data-co-lines style="margin-bottom:8px"></div>
          <div class="crow" style="padding-top:14px; border-top:1px solid var(--rule-soft)"><span>Subtotal</span><span data-co-sub>₹0</span></div>
          <div class="crow"><span>Delivery</span><span data-co-ship>—</span></div>
          <div class="crow crow--tot"><span>Total</span><b data-co-tot>₹0</b></div>

          <button class="btn btn--block btn--lg" type="submit" style="margin-top:24px">Pay securely {ARROW}</button>

          <div data-static-note hidden style="margin-top:18px; padding:18px 20px; border:1px solid var(--rule); border-radius:3px; background:rgba(232,184,75,.10)">
            <p class="small" style="color:var(--ink-2)">
              <b>This is a preview deployment.</b> Live card and UPI payments run through PayU,
              which needs the PHP or Node backend included in the project — that can't run on a
              static preview host. Everything else on the site is fully working.
            </p>
            <p class="small" style="margin-top:10px">
              <a class="tlink" href="https://wa.me/{WA}" target="_blank" rel="noopener">Order on WhatsApp instead {ARROW}</a>
            </p>
          </div>

          <p class="small" style="margin-top:16px">
            You will be taken to PayU to complete payment by UPI, card, netbanking or wallet.
            Your card details never touch our servers.
          </p>
          <ul class="acc-list" style="margin-top:14px">
            <li>{TICK} <span>Dispatched from Alwar within 24–48 hours</span></li>
            <li>{TICK} <span>Double-boxed · breakage replaced free</span></li>
            <li>{TICK} <span>Support on WhatsApp, 7 days</span></li>
          </ul>
          <p class="small" style="margin-top:16px">
            Prefer to order over WhatsApp?
            <a class="tlink" href="https://wa.me/{WA}" target="_blank" rel="noopener">Message us {ARROW}</a>
          </p>
        </aside>
      </form>
    </div>
  </section>
</main>
""" + cart_drawer() + footer()


# ---------------------------------------------------------------- result pages
def build_result(kind):
    if kind == "ok":
        title, h, sub, cta = ("Thank you — Yugmantra Organic", "Thank you.<br>Your ghee is on its way.",
                              "We've emailed your receipt. Your order leaves Alwar within 24–48 hours and you'll get a tracking link the moment it does.",
                              "Back to the shop")
        icon = f'<div style="width:74px;height:74px;border-radius:50%;border:1px solid var(--gold);display:grid;place-items:center;margin:0 auto 30px;color:var(--gold-dp)">{TICK}</div>'
        f = "thank-you.html"
    else:
        title, h, sub, cta = ("Payment not completed — Yugmantra Organic", "That payment didn't go through.",
                              "Nothing has been charged and your bag is still saved. Try again, or message us on WhatsApp and we'll take the order manually.",
                              "Try again")
        icon = '<div style="width:74px;height:74px;border-radius:50%;border:1px solid var(--clay);display:grid;place-items:center;margin:0 auto 30px;color:var(--clay);font-size:1.4rem">!</div>'
        f = "payment-failed.html"

    href = "shop.html" if kind == "ok" else "checkout.html"
    return f, head(title, sub, "result") + header() + f"""
<main>
  <section class="section" style="min-height:78vh; display:grid; place-items:center; padding-top:150px">
    <div class="wrap center">
      {icon}
      <h1 class="display d2" style="max-width:16ch; margin-inline:auto">{h}</h1>
      <p class="lede measure mx-auto" style="margin:26px auto 34px">{sub}</p>
      <div class="hero__cta" style="justify-content:center">
        <a class="btn btn--lg" href="{href}">{cta} {ARROW}</a>
        <a class="btn btn--ghost btn--lg" href="https://wa.me/{WA}" target="_blank" rel="noopener">WhatsApp us</a>
      </div>
    </div>
  </section>
</main>
""" + cart_drawer() + footer()


# ---------------------------------------------------------------- write
def write(name, content):
    with open(os.path.join(ROOT, name), "w") as fh:
        fh.write(content)
    print("built", name)


if __name__ == "__main__":
    write("index.html", build_index())
    write("shop.html", build_shop())
    write("story.html", build_story())
    write("checkout.html", build_checkout())
    for p in CATALOG:
        write(f"product-{p['slug']}.html", build_product(p))
    for k in ("ok", "fail"):
        fn, c = build_result(k)
        write(fn, c)
    print("\nDone.")
