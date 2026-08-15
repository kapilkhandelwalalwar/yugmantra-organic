/* =============================================================
   YUGMANTRA ORGANIC — site behaviour
   Header, nav, reveals, FAQ, cart, PayU handoff.
   No dependencies.
   ============================================================= */
(function () {
  "use strict";

  var CAT = window.YM_CATALOG || [];
  var R = window.YM_RULES || {};
  var SYM = R.symbol || "₹";
  var KEY = "ym_cart_v1";

  /* ---------- helpers ---------- */
  function $(s, c) { return (c || document).querySelector(s); }
  function $$(s, c) { return Array.prototype.slice.call((c || document).querySelectorAll(s)); }
  function money(n) { return SYM + Number(n).toLocaleString("en-IN"); }
  function bySku(sku) { for (var i = 0; i < CAT.length; i++) if (CAT[i].sku === sku) return CAT[i]; return null; }
  function esc(s) { return String(s).replace(/[&<>"']/g, function (c) { return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]; }); }

  /* ---------- storage that never throws ---------- */
  var mem = null;
  function load() {
    if (mem) return mem;
    try { mem = JSON.parse(localStorage.getItem(KEY)) || []; }
    catch (e) { mem = []; }
    if (!Array.isArray(mem)) mem = [];
    return mem;
  }
  function save() {
    try { localStorage.setItem(KEY, JSON.stringify(mem)); } catch (e) { /* private mode — memory only */ }
  }

  /* ---------- cart model ---------- */
  var Cart = {
    items: function () { return load().filter(function (l) { return bySku(l.sku); }); },
    count: function () { return this.items().reduce(function (n, l) { return n + l.qty; }, 0); },
    subtotal: function () {
      return this.items().reduce(function (n, l) { return n + bySku(l.sku).price * l.qty; }, 0);
    },
    shipping: function () {
      var s = this.subtotal();
      if (s === 0) return 0;
      return s >= (R.freeShipOver || 0) ? 0 : (R.shipFlat || 0);
    },
    total: function () { return this.subtotal() + this.shipping(); },
    add: function (sku, qty) {
      var c = load(), i, found = false;
      qty = qty || 1;
      for (i = 0; i < c.length; i++) if (c[i].sku === sku) { c[i].qty += qty; found = true; }
      if (!found) c.push({ sku: sku, qty: qty });
      save(); render(); open();
    },
    setQty: function (sku, qty) {
      var c = load(), i;
      for (i = c.length - 1; i >= 0; i--) {
        if (c[i].sku === sku) { if (qty <= 0) c.splice(i, 1); else c[i].qty = qty; }
      }
      mem = c; save(); render();
    }
  };
  window.YM_CART = Cart;

  /* ---------- drawer ---------- */
  function open() { document.body.classList.add("cart-open"); }
  function close() { document.body.classList.remove("cart-open"); }

  function render() {
    var n = Cart.count();
    $$("[data-cart-count]").forEach(function (el) {
      el.textContent = n;
      el.classList.toggle("hide", n === 0);
    });

    var body = $("[data-cart-body]"), foot = $("[data-cart-foot]");
    if (!body) return;

    var items = Cart.items();
    if (!items.length) {
      body.innerHTML = '<div class="empty">Your jar shelf is empty.<br><br>' +
        '<a class="tlink" href="shop.html">Browse the range</a></div>';
      if (foot) foot.classList.add("hide");
      return;
    }
    if (foot) foot.classList.remove("hide");

    body.innerHTML = items.map(function (l) {
      var p = bySku(l.sku);
      return '<div class="citem">' +
        '<div class="citem__img"><img src="' + p.img + '" alt=""></div>' +
        '<div><div class="citem__n">' + esc(p.name) + '</div>' +
        '<div class="citem__v">' + esc(p.size) + '</div>' +
        '<div class="qty"><button data-dec="' + p.sku + '" aria-label="Decrease">−</button>' +
        '<span>' + l.qty + '</span>' +
        '<button data-inc="' + p.sku + '" aria-label="Increase">+</button></div></div>' +
        '<div class="citem__p">' + money(p.price * l.qty) + '</div></div>';
    }).join("");

    var sub = $("[data-sub]"), ship = $("[data-ship]"), tot = $("[data-tot]"), fs = $("[data-freeship]");
    if (sub) sub.textContent = money(Cart.subtotal());
    if (ship) ship.textContent = Cart.shipping() === 0 ? "Free" : money(Cart.shipping());
    if (tot) tot.textContent = money(Cart.total());
    if (fs) {
      var gap = (R.freeShipOver || 0) - Cart.subtotal();
      fs.textContent = gap > 0 ? "Add " + money(gap) + " for free delivery" : "Free delivery applied";
    }
  }

  /* ---------- global click delegation ---------- */
  document.addEventListener("click", function (e) {
    var t = e.target.closest("[data-add],[data-inc],[data-dec],[data-cart-open],[data-cart-close],.scrim,[data-burger],[data-faq]");
    if (!t) return;

    if (t.hasAttribute("data-add")) {
      e.preventDefault();
      var qtyEl = $("[data-qty-val]");
      Cart.add(t.getAttribute("data-add"), qtyEl ? parseInt(qtyEl.textContent, 10) || 1 : 1);
      return;
    }
    if (t.hasAttribute("data-inc")) { var s1 = t.getAttribute("data-inc"); Cart.setQty(s1, qtyOf(s1) + 1); return; }
    if (t.hasAttribute("data-dec")) { var s2 = t.getAttribute("data-dec"); Cart.setQty(s2, qtyOf(s2) - 1); return; }
    if (t.hasAttribute("data-cart-open")) { e.preventDefault(); render(); open(); return; }
    if (t.hasAttribute("data-cart-close") || t.classList.contains("scrim")) { close(); return; }
    if (t.hasAttribute("data-burger")) { document.body.classList.toggle("nav-open"); return; }
    if (t.hasAttribute("data-faq")) {
      var item = t.closest(".faq__i"), pane = $(".faq__a", item);
      var isOpen = item.classList.contains("open");
      $$(".faq__i.open").forEach(function (o) { o.classList.remove("open"); $(".faq__a", o).style.height = "0px"; });
      if (!isOpen) { item.classList.add("open"); pane.style.height = pane.firstElementChild.offsetHeight + "px"; }
    }
  });

  function qtyOf(sku) {
    var c = load(), i;
    for (i = 0; i < c.length; i++) if (c[i].sku === sku) return c[i].qty;
    return 0;
  }

  document.addEventListener("keydown", function (e) {
    if (e.key === "Escape") { close(); document.body.classList.remove("nav-open"); }
  });

  /* ---------- header ---------- */
  var hdr = $(".hdr"), lastY = 0;
  function onScroll() {
    var y = window.pageYOffset;
    if (!hdr) return;
    hdr.classList.toggle("is-stuck", y > 24);
    hdr.classList.toggle("is-hidden", y > 420 && y > lastY && !document.body.classList.contains("nav-open"));
    lastY = y;
  }
  window.addEventListener("scroll", onScroll, { passive: true });
  onScroll();

  /* ---------- reveal ---------- */
  if ("IntersectionObserver" in window) {
    var io = new IntersectionObserver(function (es) {
      es.forEach(function (en) { if (en.isIntersecting) { en.target.classList.add("in"); io.unobserve(en.target); } });
    }, { rootMargin: "0px 0px -9% 0px", threshold: .06 });
    $$(".rv").forEach(function (el) { io.observe(el); });
  } else {
    $$(".rv").forEach(function (el) { el.classList.add("in"); });
  }

  /* ---------- marquee: duplicate track for a seamless loop ---------- */
  $$(".marq__track").forEach(function (tr) { tr.innerHTML += tr.innerHTML; });

  /* ---------- PDP quantity stepper ---------- */
  var qv = $("[data-qty-val]");
  if (qv) {
    var up = $("[data-qty-up]"), dn = $("[data-qty-dn]");
    if (up) up.addEventListener("click", function () { qv.textContent = Math.min(9, +qv.textContent + 1); });
    if (dn) dn.addEventListener("click", function () { qv.textContent = Math.max(1, +qv.textContent - 1); });
  }

  /* ---------- checkout: serialise cart into the PayU form ---------- */
  var coForm = $("[data-checkout-form]");
  if (coForm) {
    var lines = Cart.items().map(function (l) {
      var p = bySku(l.sku);
      return p.name + " (" + p.size + ") x" + l.qty;
    });
    var setv = function (n, v) { var f = coForm.querySelector('[name="' + n + '"]'); if (f) f.value = v; };
    setv("productinfo", lines.join(" | ") || "Yugmantra order");
    setv("amount", Cart.total().toFixed(2));
    setv("cart_json", JSON.stringify(Cart.items()));

    var sumEl = $("[data-co-lines]");
    if (sumEl) {
      sumEl.innerHTML = Cart.items().map(function (l) {
        var p = bySku(l.sku);
        return '<div class="crow"><span>' + esc(p.name) + ' · ' + esc(p.size) +
          ' <span class="small">×' + l.qty + '</span></span><span>' + money(p.price * l.qty) + '</span></div>';
      }).join("") || '<div class="empty">Nothing to check out yet.</div>';
    }
    var sc = $("[data-co-sub]"), sp = $("[data-co-ship]"), st = $("[data-co-tot]");
    if (sc) sc.textContent = money(Cart.subtotal());
    if (sp) sp.textContent = Cart.shipping() === 0 ? "Free" : money(Cart.shipping());
    if (st) st.textContent = money(Cart.total());

    /* Static preview hosts (GitHub Pages etc.) have no PHP/Node backend, so the
       PayU endpoint would 404. Intercept and explain instead of dead-ending. */
    var STATIC_HOSTS = ["github.io", "githubusercontent.com", "netlify.app", "pages.dev"];
    var isStatic = STATIC_HOSTS.some(function (h) { return location.hostname.indexOf(h) !== -1; });
    if (isStatic) {
      coForm.addEventListener("submit", function (e) {
        e.preventDefault();
        var box = document.querySelector("[data-static-note]");
        if (box) { box.hidden = false; box.scrollIntoView({ behavior: "smooth", block: "center" }); }
      });
    }

    if (!Cart.items().length) {
      var btn = coForm.querySelector('[type="submit"]');
      if (btn) { btn.setAttribute("disabled", "disabled"); btn.textContent = "Cart is empty"; }
    }
  }

  /* ---------- year ---------- */
  $$("[data-year]").forEach(function (el) { el.textContent = new Date().getFullYear(); });

  render();
})();
