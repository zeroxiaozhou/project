const CryptoJS = require('crypto-js');
const jsdom = require('jsdom');
const { JSDOM } = jsdom;
// 创建一个虚拟的window对象
const dom = new JSDOM('<!DOCTYPE html>');
const window = dom.window;
// 将window对象添加到全局变量中
global.window = window;
// 在这之后就可以正常使用jsencrypt
const JSEncrypt = require('jsencrypt');

var RSA_PUBLIC_KEY="MFwwDQYJKoZIhvcNAQEBBQADSwAwSAJBAJKTV32+OIzBMTDQreJGwjDe8/88a6QpeKSWdivyQkvIwq8d0BL1cOiSujKZP+G+3LGBfha2B6O0EiLT1ArKgC0CAwEAAQ==";
var AES_KEY_IV="1234567812345678";
function getRamNumber(digit){
    var result='';
    for(var i=0;i<digit;i++){
        result+=Math.floor(Math.random()*digit).toString(digit);
    }
    return result.toUpperCase();
};
function aesEnrypt(key,bodyText){
    var key  = CryptoJS.enc.Utf8.parse(key);//秘钥
    var iv   = CryptoJS.enc.Utf8.parse(AES_KEY_IV);//秘钥偏移量
    var encrypted =CryptoJS.AES.encrypt(bodyText,key,
        {
            iv:iv,
            mode:CryptoJS.mode.CBC,
            //padding:CryptoJS.pad.ZeroPadding
            padding:CryptoJS.pad.Pkcs7
        });
    return encrypted.ciphertext.toString()//128位的字符串
};
function rsaEncrypt(bodyText) {
    var encrypt = new JSEncrypt();
    encrypt.setPublicKey(RSA_PUBLIC_KEY);
    return encrypt.encrypt(bodyText);
};
function  postParamMake(params){
    // 获取16位随机数,当做aes秘钥key
    var aesKey = getRamNumber(16);
    // aes加密
    var requestData = aesEnrypt(aesKey,JSON.stringify(params));
    // rsa加密
    var encrypted = rsaEncrypt(aesKey)
    // 创建json对象
    var postParam={
        requestData :requestData,
        encrypted : encrypted
    }
    return postParam;
}
data = {
    "staffName": "赵祥鹤",
    "idType": "1",
    "idCard": "340122198511151811",
    "Page": 1,
    "PageSize": 10,
    "captcha": "aasm"
}
console.log(postParamMake(data))