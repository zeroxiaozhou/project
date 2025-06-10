const jsdom = require('jsdom');
const { JSDOM } = jsdom;
// 创建一个虚拟的window对象
const dom = new JSDOM('<!DOCTYPE html>');
const window = dom.window;
// 将window对象添加到全局变量中
global.window = window;
// 在这之后就可以正常使用jsencrypt
const JSEncrypt = require('jsencrypt');
const CryptoJS = require('crypto-js');
const crypto = require('crypto');
const base64 = require('crypto-js').enc.Base64;
const NodeRSA = require('node-rsa');
function main() {
    // 给定的公钥字符串
    var RSA_PUBLIC_KEY = "MFwwDQYJKoZIhvcNAQEBBQADSwAwSAJBAKoR8mX0rGKLqzcWmOzbfj64K8ZIgOdH\nnzkXSOVOZbFu/TJhZ7rFAN+eaGkl3C4buccQd/EjEsj9ir7ijT7h96MCAwEAAQ=="
    var encrypt = new JSEncrypt();
    encrypt.setPublicKey(RSA_PUBLIC_KEY);
    return encrypt.encrypt('Atb@1234');
}
function main2(){
    var publicKey = "-----BEGIN PUBLIC KEY-----\nMFwwDQYJKoZIhvcNAQEBBQADSwAwSAJBAKoR8mX0rGKLqzcWmOzbfj64K8ZIgOdH\nnzkXSOVOZbFu/TJhZ7rFAN+eaGkl3C4buccQd/EjEsj9ir7ijT7h96MCAwEAAQ==\n-----END PUBLIC KEY-----";
    var rsaKey = new NodeRSA();
    rsaKey.importKey(publicKey, 'pkcs8-public-pem');
    // 加密数据
    var ciphertext = rsaKey.encrypt('Atb@1234', 'base64');
    return ciphertext
}


console.log('加密并Base64编码后的数据:', main2());
console.log('加密后的数据:', main());