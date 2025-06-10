const CryptoJS = require('crypto-js');


const e = "LTPUCZC_getQualificationByCardnoAndName"
const t = '1.0.0'
const n = {
    "cardno": "142322199001065016",
    "name": "周杰彪",
    "pagenum": 1
}

function a(e) {
    var t = CryptoJS.enc.Utf8.parse("longrise211thsssdsaqqas");
    return CryptoJS.DES.encrypt(e, t, {
        mode: CryptoJS.mode.ECB,
        padding: CryptoJS.pad.Pkcs7
    }).toString()
}
function main(n){
    var parmams = {
        service: a(e),
        version: a(t),
        data: a(JSON.stringify(n))
    }
    return parmams
}
// console.log(main(n))
