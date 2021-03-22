require 'openssl'
require 'Base64'

timestamp = 1562952827927000  # please use the same timestamp (in miliseconds) as in request header
api_path = 'user/info'
msg = "#{timestamp}+#{api_path}"
secret = '98dRnVqbIhriRMZJfax3EvSPRBJrIuZ6J755KcLz6napGUpzmApJmfBY7EY3yYZn'

def signature(msg, secret)
    Base64.encode64(OpenSSL::HMAC.digest('sha256', secret, msg))
end

print("prehash msg: #{msg}")
print("\nsignature: #{signature(msg, secret)}")