#include "ascendex_util.h"


string b2a_hex( char *byte_arr, int n ) {

    const static std::string HexCodes = "0123456789abcdef";
    string HexString;
    for ( int i = 0; i < n ; ++i ) {
        unsigned char BinValue = byte_arr[i];
        HexString += HexCodes[( BinValue >> 4 ) & 0x0F];
        HexString += HexCodes[BinValue & 0x0F];
    }
    return HexString;
}

string hmac_sha256(string key, string data) {
  const unsigned char* digest = HMAC(EVP_sha256(), key.c_str(), strlen(key.c_str()), (unsigned char*)data.c_str(), data.length(), NULL, NULL);  
  char signature[100];
  EVP_EncodeBlock((unsigned char *) signature, digest, strlen((const char*)digest));
  return signature;
}   
