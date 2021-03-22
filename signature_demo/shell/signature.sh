# /bin/bash 
APIPATH=user/info
APIKEY=CEcrjGyipqt0OflgdQQSRGdrDXdDUY2x
SECRET=98dRnVqbIhriRMZJfax3EvSPRBJrIuZ6J755KcLz6napGUpzmApJmfBY7EY3yYZn
TIMESTAMP=1562952827927000 # `date +%s%N | cut -c -13`  # please use the same timestamp (in milliseconds)  as in request header
MESSAGE=$TIMESTAMP+$APIPATH
SIGNATURE=`echo -n $MESSAGE | openssl dgst -sha256 -hmac $SECRET -binary | base64`
echo $MESSAGE
echo $SIGNATURE  # UlpDqbDlNYydgT57It2IGiZGts13GnfF+D6Cmzq7xQE=

echo curl -X GET -i \
  -H "Accept: application/json" \
  -H "Content-Type: application/json" \
  -H "x-auth-key: $APIKEY" \
  -H "x-auth-signature: $SIGNATURE" \
  -H "x-auth-timestamp: $TIMESTAMP" \
  https://ascendex.com/api/pro/v1/user/info
