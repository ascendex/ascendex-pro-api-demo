import base64
import hmac
import hashlib

def hmac_sha256(secret, pre_hash_msg):
    return hmac.new(secret.encode('utf-8'), pre_hash_msg.encode('utf-8'), hashlib.sha256).digest()

def get_signature(secret, api_path, ts):
    pre_hash_msg = f'{ts}+{api_path}'
    print("prehash msg: {}", pre_hash_msg)
    return base64.b64encode(hmac_sha256(secret, pre_hash_msg)).decode('utf-8')

def main():
    secret = '98dRnVqbIhriRMZJfax3EvSPRBJrIuZ6J755KcLz6napGUpzmApJmfBY7EY3yYZn'
    api_path = 'user/info'
    timestamp = 1562952827927000  # please use the same timestamp (in milliseconds) as in request header
    
    signature = get_signature(secret, api_path, timestamp)

    print('api path: {}'.format(api_path))
    print('ts: {}'.format(timestamp))
    print('signature: {}'.format(signature))

if __name__ == '__main__':
    main()
