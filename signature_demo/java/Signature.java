import javax.crypto.Mac;
import javax.crypto.spec.SecretKeySpec;
import java.io.UnsupportedEncodingException;
import java.util.Base64;
import java.util.HashMap;
import java.util.Map;

public class Signature {

    public static String sign(String message, String secret) {
        try {
          Mac sha256_HMAC = Mac.getInstance("HmacSHA256");
          SecretKeySpec secretKeySpec = new SecretKeySpec(secret.getBytes(), "HmacSHA256");
          sha256_HMAC.init(secretKeySpec);
          return new String(Base64.getEncoder().encode(sha256_HMAC.doFinal(message.getBytes())));
        } catch (Exception e) {
          throw new RuntimeException("Unable to sign message.", e);
        }
    }

    public static void main(String[] args) {
        String secret = "98dRnVqbIhriRMZJfax3EvSPRBJrIuZ6J755KcLz6napGUpzmApJmfBY7EY3yYZn";

        String path = "user/info";
        Long timesamp = 1562952827927000L; //System.currentTimeMillis()

        String msg = timesamp.toString() + "+" + path;
        System.out.println("Prehash msg: " + msg);
        String sig = sign(msg, secret);
        System.out.println("Signature: " + sig);
    }
}