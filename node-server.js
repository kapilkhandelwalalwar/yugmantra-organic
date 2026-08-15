/* =============================================================================
   Yugmantra Organic — Node/Express alternative to the PHP backend.
   Use this instead of payu-initiate.php / payu-return.php if your host runs
   Node (Render, Railway, Fly, a VPS…) rather than PHP.

     npm init -y && npm i express
     PAYU_KEY=xxx PAYU_SALT=yyy SITE_URL=https://yugmantraorganic.in node server/node-server.js

   Serves the static site from the project root and handles the two PayU routes.
   ============================================================================= */

const express = require("express");
const crypto  = require("crypto");
const fs      = require("fs");
const path    = require("path");

const ROOT       = path.join(__dirname, "..");
const ORDERS     = path.join(ROOT, ".orders");
const PORT       = process.env.PORT || 3000;
const KEY        = process.env.PAYU_KEY  || "YOUR_MERCHANT_KEY";
const SALT       = process.env.PAYU_SALT || "YOUR_MERCHANT_SALT_V1";
const SITE_URL   = (process.env.SITE_URL || `http://localhost:${PORT}`).replace(/\/$/, "");
const ENDPOINT   = process.env.PAYU_LIVE === "1"
  ? "https://secure.payu.in/_payment"
  : "https://test.payu.in/_payment";

/* Authoritative prices — must match assets/js/catalog.js */
const PRICES = {
  "GIR-A2-500":  { name: "Gir A2 Bilona Ghee 500ml",     price: 1499 },
  "SAH-A2-500":  { name: "Sahiwal A2 Bilona Ghee 500ml", price: 1249 },
  "SAH-A2-1000": { name: "Sahiwal A2 Bilona Ghee 1L",    price: 2349 },
  "BUF-1000":    { name: "Desi Buffalo Ghee 1L",         price: 1149 },
  "HON-ASH-325": { name: "Ashwagandha Raw Honey 325g",   price: 549  },
};
const FREE_SHIP_OVER = 999;
const SHIP_FLAT = 79;

fs.mkdirSync(ORDERS, { recursive: true });

const app = express();
app.use(express.urlencoded({ extended: true }));
app.use(express.static(ROOT, { extensions: ["html"] }));

const esc = (s) => String(s).replace(/[&<>"']/g,
  (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
const sha512 = (s) => crypto.createHash("sha512").update(s).digest("hex").toLowerCase();

/* ------------------------------------------------------------- initiate */
app.post("/server/payu-initiate.php", (req, res) => {
  const b = req.body || {};
  const bad = (m) => { console.error("[initiate]", m); res.redirect("/payment-failed.html"); };

  const phone = String(b.phone || "").replace(/\D/g, "");
  const zip   = String(b.zipcode || "").replace(/\D/g, "");
  if (!b.firstname || !/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(b.email || "") ||
      phone.length < 10 || !b.address1 || !b.city || !b.state || zip.length !== 6) {
    return bad("invalid customer fields");
  }

  let cart;
  try { cart = JSON.parse(b.cart_json || "[]"); } catch { return bad("bad cart json"); }
  if (!Array.isArray(cart) || !cart.length) return bad("empty cart");

  let subtotal = 0;
  const lines = [];
  for (const l of cart) {
    const p = PRICES[l.sku];
    const q = parseInt(l.qty, 10);
    if (!p || !(q >= 1 && q <= 20)) return bad("bad sku/qty " + l.sku);
    subtotal += p.price * q;
    lines.push(`${p.name} x${q}`);
  }
  const shipping = subtotal >= FREE_SHIP_OVER ? 0 : SHIP_FLAT;
  const amount = (subtotal + shipping).toFixed(2);
  const productinfo = lines.join(" | ").slice(0, 100);

  const txnid = "YM" + new Date().toISOString().replace(/\D/g, "").slice(2, 14) +
                crypto.randomBytes(3).toString("hex").toUpperCase().slice(0, 5);

  const f = {
    key: KEY, txnid, amount, productinfo,
    firstname: b.firstname, lastname: b.lastname || "",
    email: b.email, phone,
    address1: b.address1, address2: b.address2 || "",
    city: b.city, state: b.state, country: b.country || "India", zipcode: zip,
    udf1: String(b.udf1 || "").slice(0, 200), udf2: zip, udf3: b.city, udf4: "", udf5: "",
    surl: `${SITE_URL}/server/payu-return.php`,
    furl: `${SITE_URL}/server/payu-return.php`,
  };
  f.hash = sha512([
    KEY, txnid, amount, productinfo, f.firstname, f.email,
    f.udf1, f.udf2, f.udf3, f.udf4, f.udf5, "", "", "", "", "", SALT,
  ].join("|"));

  fs.writeFileSync(path.join(ORDERS, txnid + ".json"), JSON.stringify({
    txnid, created: new Date().toISOString(), status: "pending",
    amount, subtotal, shipping, items: cart,
    customer: { firstname: f.firstname, lastname: f.lastname, email: f.email, phone,
                address1: f.address1, address2: f.address2, city: f.city,
                state: f.state, zipcode: zip, country: f.country },
    note: f.udf1,
  }, null, 2));

  res.send(`<!doctype html><html><head><meta charset="utf-8"><title>Redirecting…</title>
<style>body{margin:0;min-height:100vh;display:grid;place-items:center;background:#F7F2E9;color:#1C1815;
font-family:system-ui,sans-serif;text-align:center}.r{width:40px;height:40px;border:1px solid rgba(28,24,21,.15);
border-top-color:#C08A2E;border-radius:50%;margin:0 auto 22px;animation:s .9s linear infinite}
@keyframes s{to{transform:rotate(360deg)}}p{font-size:.8rem;letter-spacing:.18em;text-transform:uppercase;color:#6B6154}</style>
</head><body><div><div class="r"></div><p>Taking you to secure payment…</p>
<form id="f" method="POST" action="${ENDPOINT}">
${Object.entries(f).map(([k, v]) => `<input type="hidden" name="${esc(k)}" value="${esc(v)}">`).join("\n")}
<noscript><button type="submit">Continue</button></noscript></form></div>
<script>document.getElementById('f').submit()</script></body></html>`);
});

/* --------------------------------------------------------------- return */
app.post("/server/payu-return.php", (req, res) => {
  const b = req.body || {};
  const calc = sha512([
    SALT, b.status || "", "", "", "", "", "",
    b.udf5 || "", b.udf4 || "", b.udf3 || "", b.udf2 || "", b.udf1 || "",
    b.email || "", b.firstname || "", b.productinfo || "", b.amount || "", b.txnid || "", KEY,
  ].join("|"));

  if (!b.hash || calc !== String(b.hash).toLowerCase()) {
    console.error("[return] HASH MISMATCH", b.txnid);
    return res.redirect("/payment-failed.html");
  }

  const file = path.join(ORDERS, String(b.txnid).replace(/[^A-Za-z0-9]/g, "") + ".json");
  let ok = b.status === "success";
  if (fs.existsSync(file)) {
    const o = JSON.parse(fs.readFileSync(file, "utf8"));
    if (Number(o.amount).toFixed(2) !== Number(b.amount).toFixed(2)) {
      console.error("[return] amount mismatch", b.txnid);
      ok = false;
    }
    o.status = ok ? "paid" : "failed";
    o.payu = { mihpayid: b.mihpayid, mode: b.mode, error: b.error_Message || b.error };
    o.settledAt = new Date().toISOString();
    fs.writeFileSync(file, JSON.stringify(o, null, 2));
    if (ok) console.log(`PAID  ${o.txnid}  ₹${o.amount}  ${o.customer.email}`);
  }
  res.redirect(ok ? "/thank-you.html" : "/payment-failed.html");
});

app.listen(PORT, () => {
  console.log(`Yugmantra running on http://localhost:${PORT}`);
  console.log(`PayU endpoint: ${ENDPOINT}`);
});
