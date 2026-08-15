<?php
/* =============================================================================
   Yugmantra Organic — configuration
   -----------------------------------------------------------------------------
   COPY THIS FILE TO  config.php  AND FILL IN YOUR REAL VALUES.
   Never commit config.php to git. Never expose the salt to the browser.
   ============================================================================= */

declare(strict_types=1);

/* ---- PayU credentials (PayU Dashboard → Settings → My Account → Key/Salt) --- */
define('YM_PAYU_KEY',  'YOUR_MERCHANT_KEY');
define('YM_PAYU_SALT', 'YOUR_MERCHANT_SALT_V1');

/* Use the TEST endpoint until you have completed a live test transaction. */
define('YM_PAYU_ENDPOINT', 'https://test.payu.in/_payment');       // sandbox
// define('YM_PAYU_ENDPOINT', 'https://secure.payu.in/_payment');  // LIVE

/* No trailing slash. Must be https in production — PayU rejects http callbacks. */
define('YM_SITE_URL', 'https://yugmantraorganic.in');

/* Where pending/paid orders are written as JSON.
   Put this OUTSIDE your public web root if you can. */
define('YM_ORDER_DIR', __DIR__ . '/../.orders');

/* Order notification email (leave '' to disable). */
define('YM_NOTIFY_EMAIL', 'orders@yugmantraorganic.in');

/* ---- Shipping rules — must match assets/js/catalog.js ---------------------- */
define('YM_FREE_SHIP_OVER', 999);
define('YM_SHIP_FLAT', 79);

/* ---- Authoritative prices -------------------------------------------------
   THIS is the price the customer is charged. The JavaScript catalogue is only
   for display. If you change a price, change it in BOTH places.
   --------------------------------------------------------------------------- */
define('YM_PRICES', [
    'GIR-A2-500'   => ['name' => 'Gir A2 Bilona Ghee 500ml',      'price' => 1499],
    'SAH-A2-500'   => ['name' => 'Sahiwal A2 Bilona Ghee 500ml',  'price' => 1249],
    'SAH-A2-1000'  => ['name' => 'Sahiwal A2 Bilona Ghee 1L',     'price' => 2349],
    'BUF-1000'     => ['name' => 'Desi Buffalo Ghee 1L',          'price' => 1149],
    'HON-ASH-325'  => ['name' => 'Ashwagandha Raw Honey 325g',    'price' => 549],
]);
