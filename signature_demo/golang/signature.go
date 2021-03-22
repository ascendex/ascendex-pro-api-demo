package main

import (
	"crypto/hmac"
	"crypto/sha256"
	"encoding/base64"
	"fmt"
	"strings"
	"strconv"
)


func sign(message string, secret string) string {
	key := []byte(secret)
	h := hmac.New(sha256.New, key)
	h.Write([]byte(message))
	return base64.StdEncoding.EncodeToString(h.Sum(nil))
}

func main() {

	secret := "98dRnVqbIhriRMZJfax3EvSPRBJrIuZ6J755KcLz6napGUpzmApJmfBY7EY3yYZn"
	timestamp := 1562952827927000
	ts := strconv.Itoa(timestamp)
	apiPath := "user/info"
	msg := strings.Join([]string{ts, "+", apiPath}, "")
	fmt.Println("Prehash msg: ", msg)
	signature := sign(msg, secret)
	fmt.Println("Signature: ", signature)
}

