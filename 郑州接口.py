import base64
import hashlib
import random
import string
import time
import requests
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend


def get_sha256_str(s: str) -> str:
    return hashlib.sha256(s.encode('utf-8')).hexdigest()


def get_private_key(private_key_str: str):
    key_bytes = base64.b64decode(private_key_str)
    private_key = serialization.load_der_private_key(
        key_bytes,
        password=None,
        backend=default_backend()
    )
    return private_key


def sign(data: str, private_key) -> str:
    signature = private_key.sign(
        data.encode('utf-8'),
        padding.PKCS1v15(),
        hashes.MD5()
    )
    return base64.b64encode(signature).decode('utf-8')


def get_token():
    api_id = "rf9c552da4b6dcd814"
    api_secret = "9b9782c2cbc74d9d865727db376ccfcf"
    private_key_str = "MIICdwIBADANBgkqhkiG9w0BAQEFAASCAmEwggJdAgEAAoGBAN+qeLwr0gBRdcgcvp8egEyuDEhg1TZiBc4lrjaNeUmnpGiPaQIiZib/m61yJvEWVSx6SFlRIjGWNjvUmfotIQMqfbAKVc7Ypx2ZcnL3pxvJ5HRgj+Ynpr/Tw4Kw+EnuD63QyL663sasGY1K3cU6sUMusgaqeMLSHAcNtBGddjIFAgMBAAECgYAUhzHjm2X/z3ou7qx0MDl4UDUiY3jOL/r2a7Dsotlx8Cf/zMHHh162z5j7N1HpqLISjfqb7/1ibbX2kdG8C25PDxyBmEf+Wa9Cgra0JTPq9gnQYRvkMBCzyTqPH+OAnWSyV3bm+wwE0rWNOFm73rmeYLWOz0eKVTFF3G15KHwBNQJBAPoxIxybAi3Vy6fP+Nknn3bmLE1Jtp8dwt9m6a6eW4seLtceHkt6gGo+7TMxgz4Nu/43AcTPXkx2iFpe5A527+8CQQDk27F0UqCsc5gVlsdpnTpxWSwotog7FIHJvoOKLU599LMFBQxewCrnDpguMHDIm/2T/TtA5WBns2jsIu6SOYlLAkEA5p6ImQOhXJKoKUWhQrotWbINwChkeAM88CSy3s0F4RSvZIdUsYp3+HeMuhW3vml2knwt2zay25SfV34EhfjIbQJARrXegVtaS443qkv49xfeS9FKhJXJR7/RTh0wFUxkWSR2/5EMvmXPm651tKfA4SrZUZVHboiwnbngLD2qysE+OwJBAPC+g7VBr0FWpU0tbkePXhlYzlHnftEvIyYWYndJd6uH+Su2GYxG99MCGJAMCpR00v8A7vU7E4iZgX1egI8ZEIY="

    nonce = ''.join(random.choices(string.ascii_letters + string.digits, k=10))
    time_stamp = str(int(time.time() * 1000))

    str_to_sign = f"{api_id}&{time_stamp}&{nonce}"
    sign_value = get_sha256_str(str_to_sign)

    params_map = {
        "sign": sign_value,
        "apiId": api_id,
        "nonce": nonce,
        "apiSecret": api_secret,
        "time": time_stamp
    }

    sorted_keys = sorted(params_map.keys())
    sb = []
    for k in sorted_keys:
        value = params_map[k].strip()
        if value:
            sb.append(f"{k}={value}&")
    sign_str = ''.join(sb)

    private_key = get_private_key(private_key_str)
    api_sign = sign(sign_str, private_key)
    params_map["apiSign"] = api_sign

    # 第一次请求获取code
    url1 = "http://zzjk.zztaxi.cn:8090/netCarMonitor/interface/auth/serverVerify.do"
    headers = {"Content-Type": "application/json"}  # 设置 Content-Type 为 application/json
    response1 = requests.post(url1, json=params_map, headers=headers)  # 使用 json 参数
    body1 = response1.json()
    print('第一次请求获取code', body1)
    code = body1.get("data", "")
    params_map["code"] = code

    # 第二次请求获取token
    url2 = "http://zzjk.zztaxi.cn:8090/netCarMonitor/interface/auth/getToken.do"
    response2 = requests.post(url2, json=params_map, headers=headers)  # 使用 json 参数
    token_body = response2.json()
    return token_body


def main():
    token_result = get_token()
    print("返回的token:", token_result)
    token = token_result.get("data", "")

    url = "http://zzjk.zztaxi.cn:8090/netCarMonitor/interfaceQuery/getVerificationStatus.do"
    # url = "http://zzjk.zztaxi.cn:8090/netCarMonitor/interfaceQuery/batchGetVerificationStatus.do"
    headers = {"interfaceToken": token}
    params = {
        "key": "MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQDfqni8K9IAUXXIHL6fHoBMrgxIYNU2YgXOJa42jXlJp6Roj2kCImYm/5utcibxFlUsekhZUSIxljY71Jn6LSEDKn2wClXO2KcdmXJy96cbyeR0YI/mJ6a/08OCsPhJ7g+t0Mi+ut7GrBmNSt3FOrFDLrIGqnjC0hwHDbQRnXYyBQIDAQAB",
        "vehicleNo": "豫AD89264",
        "idCardNo": "410422200108107698"
    }
    response = requests.get(url, headers=headers, params=params)
    print("结果返回:", response.json())


if __name__ == "__main__":
    main()
