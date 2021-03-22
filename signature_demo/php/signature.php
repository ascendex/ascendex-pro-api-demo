
<?php

function milliseconds() {
    list($msec, $sec) = explode(' ', microtime());
    return (int) ($sec . substr($msec, 2, 3));
}

function hmac($msg, $secret) {
    $hmac = hash_hmac('sha256', $msg, $secret, true);
    $hmac = base64_encode($hmac);
    return $hmac;
}

$secret = '98dRnVqbIhriRMZJfax3EvSPRBJrIuZ6J755KcLz6napGUpzmApJmfBY7EY3yYZn';
$api_path = 'user/info';
//$timestamp = (string) milliseconds();
$timestamp = '1562952827927000'; // Please use the timestamp (in miliseconds) in request head 
$msg = $timestamp . '+' . $api_path;
$signature = hmac($msg, $secret);
echo 'prehash msg: '.$msg.PHP_EOL;
echo 'signature: '.$signature.PHP_EOL;
