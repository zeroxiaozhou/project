const CryptoJs = require('crypto-js');
const md5 = require('md5');
function padLeftZero (str) {
  return ('00' + str).substr(str.length)
}
function formatDate (date, fmt) {
  if (/(y+)/.test(fmt)) {
    fmt = fmt.replace(RegExp.$1, (date.getFullYear() + '').substr(4 - RegExp.$1.length))
  }
  const o = {
    'M+': date.getMonth() + 1,
    'd+': date.getDate(),
    'h+': date.getHours(),
    'm+': date.getMinutes(),
    's+': date.getSeconds()
  }
  for (const k in o) {
    if (new RegExp(`(${k})`).test(fmt)) {
      const str = o[k] + ''
      fmt = fmt.replace(RegExp.$1, (RegExp.$1.length === 1) ? str : padLeftZero(str))
    }
  }
  return fmt
}
function getTimeStamp () {
  return formatDate(new Date(), 'yyyyMMddhhmmss')
}

function random (length) {
  var str = Math.random().toString(36).substr(2)
  if (str.length >= length) {
    return str.substr(0, length)
  }
  str += random(length - str.length)
  return str
}

function getAesKey (timeStamp) {
  var result = ''
  for (var i = 0; i < timeStamp.length; i++) {
    result = result + md5(timeStamp + i)
  }
  return md5(result)
}

function encrypt (str, keyStr) {
  let key = ''
  let iv = ''
  if (keyStr) {
    key = CryptoJs.enc.Utf8.parse(keyStr.substr(0, 16))
    iv = CryptoJs.enc.Utf8.parse(keyStr.substr(16))
  }
  const srcStr = CryptoJs.enc.Utf8.parse(str)
  var encrypted = CryptoJs.AES.encrypt(srcStr, key, {
    iv: iv,
    mode: CryptoJs.mode.CBC,
    padding: CryptoJs.pad.Pkcs7
  })

  return encrypted.ciphertext.toString().toUpperCase()
}

const timeStamp = getTimeStamp()
const nonce = random(32)
const aesKey = getAesKey(timeStamp)
const datastr = {name: '琼BBD577'}

function getParam (timeStampStr, nonceStr) {
  const aesKeyStr = getAesKey(timeStampStr)
  var signStr = {
    aesKey: aesKeyStr,
    nonce: nonceStr,
    timeStamp: timeStampStr
  }
  var paramStr = {
    timeStamp: timeStampStr,
    sign: encrypt(JSON.stringify(signStr), aesKeyStr)
  }
  return paramStr
};

function getBody (dataStr, timeStampStr, nonceStr) {
  const aesKeyStr = getAesKey(timeStampStr)
  var signStr = {
    timeStamp: timeStampStr,
    nonce: nonceStr
  }
  var bodyStr = {
    sign: encrypt(JSON.stringify(signStr), aesKeyStr),
    data: encrypt(JSON.stringify(dataStr), nonceStr)
  }
  return bodyStr
};

function main(){
  param = getParam(timeStamp, nonce)
  body = getBody(datastr, timeStamp, nonce)
  return [param, body]
};
console.log(main())
console.log(getParam(timeStamp, nonce))
console.log(getBody(datastr, timeStamp, nonce))
