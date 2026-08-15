<?php
/* =============================================================================
   Yugmantra Organic — PayU payment initiation
   -----------------------------------------------------------------------------
   The checkout form POSTs here. This file:
     1. validates the incoming order,
     2. recomputes the amount SERVER-SIDE from the catalogue (never trust the
        browser's number — this is the single most important line of defence),
     3. generates a transaction id and the SHA-512 request hash,
     4. writes a pending order to disk,
     5. auto-submits the customer to PayU's hosted payment page.

   Requires PHP 7.4+. No composer packages, no framework.
   ============================================================================= */

declare(strict_types=1);
require __DIR__ . '/config.php';

/* ---------------------------------------------------------------- helpers */
function fail(string $msg): void {
    error_log('[payu-initiate] ' . $msg);
    header('Location: ../payment-failed.html');
    exit;
}
function post(string $k, string $d = ''): string {
    return isset($_POST[$k]) ? trim((string) $_POST[$k]) : $d;
}

if ($_SERVER['REQUEST_METHOD'] !== 'POST') {
    fail('non-POST request');
}

/* ---------------------------------------------------------------- customer */
$firstname = post('firstname');
$lastname  = post('lastname');
$email     = filter_var(post('email'), FILTER_VALIDATE_EMAIL) ?: '';
$phone     = preg_replace('/[^0-9]/', '', post('phone'));
$address1  = post('address1');
$address2  = post('address2');
$city      = post('city');
$state     = post('state');
$zipcode   = preg_replace('/[^0-9]/', '', post('zipcode'));
$country   = post('country', 'India');
$note      = mb_substr(post('udf1'), 0, 200);

if ($firstname === '' || $email === '' || strlen($phone) < 10 ||
    $address1 === '' || $city === '' || $state === '' || strlen($zipcode) !== 6) {
    fail('missing or invalid customer fields');
}

/* -------------------------------------------------- recompute the amount */
$cart = json_decode(post('cart_json', '[]'), true);
if (!is_array($cart) || count($cart) === 0) {
    fail('empty cart');
}

$subtotal = 0;
$lines    = [];
foreach ($cart as $line) {
    $sku = isset($line['sku']) ? (string) $line['sku'] : '';
    $qty = isset($line['qty']) ? (int) $line['qty'] : 0;
    if ($qty < 1 || $qty > 20 || !isset(YM_PRICES[$sku])) {
        fail('unknown sku or bad quantity: ' . $sku);
    }
    $p         = YM_PRICES[$sku];
    $subtotal += $p['price'] * $qty;
    $lines[]   = $p['name'] . ' x' . $qty;
}

$shipping = $subtotal >= YM_FREE_SHIP_OVER ? 0 : YM_SHIP_FLAT;
$amount   = number_format($subtotal + $shipping, 2, '.', '');

/* Amount the browser claimed — log a mismatch, then ignore it. */
$claimed = number_format((float) post('amount', '0'), 2, '.', '');
if ($claimed !== $amount) {
    error_log("[payu-initiate] amount mismatch: browser={$claimed} server={$amount}");
}

$productinfo = mb_substr(implode(' | ', $lines), 0, 100);

/* ---------------------------------------------------------------- txn id */
$txnid = 'YM' . date('ymdHis') . strtoupper(substr(bin2hex(random_bytes(3)), 0, 5));

/* ---------------------------------------------------------------- hash
   PayU request hash (SHA-512):
   key|txnid|amount|productinfo|firstname|email|udf1|udf2|udf3|udf4|udf5||||||SALT
   -------------------------------------------------------------------------- */
$udf1 = $note;
$udf2 = $zipcode;
$udf3 = $city;
$udf4 = '';
$udf5 = '';

$hashString = implode('|', [
    YM_PAYU_KEY, $txnid, $amount, $productinfo, $firstname, $email,
    $udf1, $udf2, $udf3, $udf4, $udf5, '', '', '', '', '', YM_PAYU_SALT,
]);
$hash = strtolower(hash('sha512', $hashString));

/* ---------------------------------------------------------------- persist */
$order = [
    'txnid'     => $txnid,
    'created'   => gmdate('c'),
    'status'    => 'pending',
    'amount'    => $amount,
    'subtotal'  => $subtotal,
    'shipping'  => $shipping,
    'items'     => $cart,
    'customer'  => compact('firstname', 'lastname', 'email', 'phone',
                           'address1', 'address2', 'city', 'state', 'zipcode', 'country'),
    'note'      => $note,
];
@mkdir(YM_ORDER_DIR, 0770, true);
file_put_contents(YM_ORDER_DIR . '/' . $txnid . '.json',
                  json_encode($order, JSON_PRETTY_PRINT | JSON_UNESCAPED_UNICODE));

/* ---------------------------------------------------------------- hand off */
$fields = [
    'key'         => YM_PAYU_KEY,
    'txnid'       => $txnid,
    'amount'      => $amount,
    'productinfo' => $productinfo,
    'firstname'   => $firstname,
    'email'       => $email,
    'phone'       => $phone,
    'lastname'    => $lastname,
    'address1'    => $address1,
    'address2'    => $address2,
    'city'        => $city,
    'state'       => $state,
    'country'     => $country,
    'zipcode'     => $zipcode,
    'udf1'        => $udf1,
    'udf2'        => $udf2,
    'udf3'        => $udf3,
    'udf4'        => $udf4,
    'udf5'        => $udf5,
    'surl'        => YM_SITE_URL . '/server/payu-return.php',
    'furl'        => YM_SITE_URL . '/server/payu-return.php',
    'hash'        => $hash,
];
?>
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>Redirecting to secure payment…</title>
<meta name="robots" content="noindex">
<style>
  body{margin:0;min-height:100vh;display:grid;place-items:center;background:#F7F2E9;
       color:#1C1815;font-family:system-ui,-apple-system,"Segoe UI",sans-serif;text-align:center}
  .r{width:40px;height:40px;border:1px solid rgba(28,24,21,.15);border-top-color:#C08A2E;
     border-radius:50%;margin:0 auto 22px;animation:s .9s linear infinite}
  @keyframes s{to{transform:rotate(360deg)}}
  p{font-size:.8rem;letter-spacing:.18em;text-transform:uppercase;color:#6B6154}
  noscript button{margin-top:20px;padding:14px 28px;border-radius:999px;border:0;
     background:#1C1815;color:#F7F2E9;letter-spacing:.14em;text-transform:uppercase;font-size:.72rem}
</style>
</head>
<body>
  <div>
    <div class="r"></div>
    <p>Taking you to secure payment…</p>
    <form id="payu" method="POST" action="<?= htmlspecialchars(YM_PAYU_ENDPOINT, ENT_QUOTES) ?>">
      <?php foreach ($fields as $n => $v): ?>
        <input type="hidden" name="<?= htmlspecialchars((string) $n, ENT_QUOTES) ?>"
               value="<?= htmlspecialchars((string) $v, ENT_QUOTES) ?>">
      <?php endforeach; ?>
      <noscript><button type="submit">Continue to payment</button></noscript>
    </form>
  </div>
  <script>document.getElementById('payu').submit();</script>
</body>
</html>
