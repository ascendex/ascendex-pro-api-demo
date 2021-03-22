const crypto = require('crypto');

const timestamp = '1562952827927000'; // please use the same timestamp (in milliseconds) as in request header
const api_path = 'user/info';
const msg = [timestamp, '+', api_path].join('');
const apiSecret = '98dRnVqbIhriRMZJfax3EvSPRBJrIuZ6J755KcLz6napGUpzmApJmfBY7EY3yYZn';

function signature(query_string) {
    return crypto
        .createHmac('sha256', apiSecret)
        .update(query_string)
        .digest('base64');
}

console.log("prehash msg: ");
console.log(msg);
console.log("signature:");
console.log(signature(msg));

console.log("\n");
