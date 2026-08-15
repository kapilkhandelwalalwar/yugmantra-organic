# Yugmantra Organic — website

A hand-built, dependency-free storefront for Yugmantra Organic Foods. Ghee-first,
warm-minimal, with PayU checkout.

Everything here is plain HTML, CSS and vanilla JS. No React, no build step required
to *run* it, no npm packages in production, no third-party fonts or trackers. It will
run on any host that serves static files, and on PHP or Node if you want live payments.

---

## 1. What's in the box

```
index.html                  Home
shop.html                   The range
story.html                  Our Story
product-*.html              One page per product (pre-rendered, good for SEO)
checkout.html               Delivery details + order summary
thank-you.html              Payment success landing
payment-failed.html         Payment failure landing

assets/css/site.css         The entire design system
assets/js/catalog.js        ← PRODUCTS AND PRICES LIVE HERE
assets/js/site.js           Cart, drawer, reveals, FAQ, checkout wiring
assets/fonts/               Fraunces + Inter, self-hosted (no Google Fonts call)
assets/img/                 All artwork, hand-drawn as SVG

server/config.sample.php    → copy to config.php and fill in
server/payu-initiate.php    Builds the PayU request + hash
server/payu-return.php      Verifies PayU's response
server/node-server.js       Node/Express equivalent of the two files above

build.py                    Regenerates the HTML pages from shared partials
gen_assets.py               Regenerates the SVG artwork
```

---

## 2. Run it locally

```bash
python3 -m http.server 8000
# open http://localhost:8000
```

Browsing, the cart and the drawer all work from static files. Only the final
"Pay securely" step needs a server (section 4).

---

## 3. Changing products and prices

**`assets/js/catalog.js` is the single source of truth for the front end.**
Edit a price, a name, a description or the size there.

Then regenerate the HTML pages:

```bash
python3 build.py
```

> ⚠️ **Prices live in two places on purpose.** The JS catalogue is what the
> customer *sees*; `server/config.php` (or the `PRICES` object in
> `node-server.js`) is what they are actually *charged*. The server never trusts
> a number sent by the browser — that is the single most important defence
> against someone editing the price in devtools. **When you change a price,
> change it in both files.**

Shipping rules (`freeShipOver`, `shipFlat`) also appear in both places.

---

## 4. Turning on PayU

### Option A — PHP hosting (cPanel, Hostinger, GoDaddy, most shared hosts)

1. Upload the whole folder to your web root.
2. `cp server/config.sample.php server/config.php`
3. Open `server/config.php` and fill in:
   - `YM_PAYU_KEY` and `YM_PAYU_SALT` — PayU Dashboard → Settings → My Account → Key/Salt
   - `YM_SITE_URL` — your https URL, no trailing slash
   - `YM_NOTIFY_EMAIL` — where new-order emails go
4. Leave `YM_PAYU_ENDPOINT` on the **test** URL and place a sandbox order end to end.
5. When that works, switch the endpoint constant to the live URL and place one
   real ₹1 order before you announce anything.

In the PayU dashboard set both the **Success URL** and **Failure URL** to:

```
https://yugmantraorganic.in/server/payu-return.php
```

### Option B — Node hosting (Render, Railway, Fly, a VPS)

```bash
npm init -y && npm i express
PAYU_KEY=xxx PAYU_SALT=yyy SITE_URL=https://yugmantraorganic.in PAYU_LIVE=1 \
  node server/node-server.js
```

It serves the static site *and* the two payment routes from the same process.
Leave `PAYU_LIVE` unset to stay on the sandbox.

### What the payment code actually does

- Recomputes the order total from the server-side price list — a tampered
  `amount` field in the browser is logged and thrown away.
- Rejects unknown SKUs, quantities outside 1–20, and malformed contact details.
- Generates the SHA-512 request hash to PayU's documented field order.
- **Verifies the response hash before marking anything paid.** PayU's callback is
  an ordinary browser POST and is trivially forgeable without this check.
- Re-checks the amount even after a valid hash.
- Writes each order to `.orders/<txnid>.json` (pending → paid/failed).

This was tested against a mock PayU: 11 checks covering hash correctness, price
tampering, bad SKUs, the shipping threshold, and a forged success callback.

### Keep `.orders/` private

The included `.htaccess` blocks it on Apache. On nginx add:

```nginx
location ~ /\.orders { deny all; }
location ~ /server/config\.php { deny all; }
```

Better still, move `YM_ORDER_DIR` somewhere outside the web root entirely.

---

## 5. Before you go live — a short checklist

- [ ] **Replace the three testimonials on `index.html`.** They are written as
      placeholders and are *not* real customer quotes. Swap in genuine reviews
      (Amazon and Flipkart reviews you already have are ideal) or delete the
      section. Search the file for `FROM THE KITCHEN TABLE`.
- [ ] **Check every price** in `assets/js/catalog.js` and `server/config.php`.
      The ones in there are plausible market rates, not your actual pricing.
- [ ] Confirm the phone number, email and address in `assets/js/catalog.js`
      (`YM_RULES`) — `care@yugmantraorganic.in` may need creating.
- [ ] Swap the SVG jar illustrations for real product photography when you have
      it. Drop the files into `assets/img/` and change the `img` paths in
      `assets/js/catalog.js`. Shoot square-ish, on a light warm background, with
      the jar centred — the layout expects roughly 4:4.6.
- [ ] Add a Privacy Policy, Terms, and Shipping & Returns page. Indian payment
      gateways generally require these to be linked before they approve a
      live merchant account.
- [ ] Point the newsletter form at a real list (Mailchimp/Brevo). Right now it
      just says thank you and does nothing.
- [ ] Set up HTTPS. PayU will not call back to a plain http URL.

---

## 6. Design notes

- **Palette** — bone `#F7F2E9`, ink `#1C1815`, molten gold `#C08A2E → #E8B84B`,
  clay `#A0503A`. All defined as CSS custom properties at the top of `site.css`;
  change them there and the whole site follows.
- **Type** — Fraunces for display (that slightly wonky high-contrast serif does
  most of the "expensive" work), Inter for everything else. Both self-hosted as
  variable fonts, ~170 KB total, preloaded.
- **Motion** — everything is a slow reveal on scroll via `IntersectionObserver`,
  plus a floating hero jar and a rotating seal. All of it is disabled under
  `prefers-reduced-motion`.
- **Grain** — a fixed SVG noise layer at 30% multiply over the whole page. It is
  the difference between "clean" and "printed".
- **Artwork** — every illustration is SVG generated by `gen_assets.py`, so it is
  sharp at any size and weighs almost nothing. Re-run that script after editing.

## 7. Accessibility and performance

Semantic landmarks, labelled form fields, keyboard-dismissable drawer and nav,
visible focus retained, reduced-motion honoured, and `Product` JSON-LD on every
product page. No render-blocking third-party requests at all — the only network
calls are to your own domain.
