<?php
/* =============================================================================
   Yugmantra Organic — PayU return handler (surl + furl)
   -----------------------------------------------------------------------------
   PayU POSTs the customer back here after payment. We verify the response hash
   before believing a single field, update the stored order, optionally email
   ourselves, then redirect to a friendly page.

   NEVER mark an order paid without this hash check — the response is a plain
   browser POST and can be forged trivially otherwise.
   ============================================================================= */

declare(strict_types=1);
require __DIR__ . '/config.php';

function p(string $k): string { return isset($_POST[$k]) ? (string) $_POST[$k] : ''; }

$status      = p('status');
$txnid       = p('txnid');
$amount      = p('amount');
$productinfo = p('productinfo');
$firstname   = p('firstname');
$email       = p('email');
$posted      = strtolower(p('hash'));
$mihpayid    = p('mihpayid');
$mode        = p('mode');
$error       = p('error_Message') ?: p('error');

/* ---- Response hash is the REQUEST hash, reversed, with status inserted ---- */
$calc = strtolower(hash('sha512', implode('|', [
    YM_PAYU_SALT, $status, '', '', '', '', '',
    p('udf5'), p('udf4'), p('udf3'), p('udf2'), p('udf1'),
    $email, $firstname, $productinfo, $amount, $txnid, YM_PAYU_KEY,
])));

$valid = ($posted !== '' && hash_equals($calc, $posted));

if (!$valid) {
    error_log("[payu-return] HASH MISMATCH for txn {$txnid} — refusing to trust response");
    header('Location: ../payment-failed.html');
    exit;
}

/* ---- Update the stored order ------------------------------------------- */
$file = YM_ORDER_DIR . '/' . preg_replace('/[^A-Za-z0-9]/', '', $txnid) . '.json';
if (is_file($file)) {
    $order = json_decode((string) file_get_contents($file), true) ?: [];

    /* Guard against a tampered amount even after a valid hash. */
    if (isset($order['amount']) && number_format((float) $order['amount'], 2, '.', '')
        !== number_format((float) $amount, 2, '.', '')) {
        error_log("[payu-return] amount mismatch on {$txnid}");
        $status = 'failure';
    }

    $order['status']    = ($status === 'success') ? 'paid' : 'failed';
    $order['payu']      = ['mihpayid' => $mihpayid, 'mode' => $mode, 'error' => $error];
    $order['settledAt'] = gmdate('c');
    file_put_contents($file, json_encode($order, JSON_PRETTY_PRINT | JSON_UNESCAPED_UNICODE));

    if ($status === 'success' && YM_NOTIFY_EMAIL !== '') {
        $c    = $order['customer'] ?? [];
        $body = "New paid order {$txnid}\n"
              . "Amount: ₹{$amount} ({$mode})\n"
              . "PayU ref: {$mihpayid}\n\n"
              . "Items: {$productinfo}\n\n"
              . ($c['firstname'] ?? '') . ' ' . ($c['lastname'] ?? '') . "\n"
              . ($c['address1'] ?? '') . "\n" . ($c['address2'] ?? '') . "\n"
              . ($c['city'] ?? '') . ', ' . ($c['state'] ?? '') . ' ' . ($c['zipcode'] ?? '') . "\n"
              . 'Phone: ' . ($c['phone'] ?? '') . "\n"
              . 'Email: ' . ($c['email'] ?? '') . "\n"
              . 'Note: ' . ($order['note'] ?? '') . "\n";
        @mail(YM_NOTIFY_EMAIL, "Order {$txnid} — ₹{$amount}", $body,
              "Content-Type: text/plain; charset=UTF-8\r\nFrom: orders@yugmantraorganic.in");
    }
}

header('Location: ../' . ($status === 'success' ? 'thank-you.html' : 'payment-failed.html'));
exit;
