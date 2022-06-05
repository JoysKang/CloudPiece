const CryptoJS = require("crypto-js");

const Config = require("../conf.json")


export function encrypt(text: string) {
    return CryptoJS.AES.encrypt(text, Config.key).toString();
}

export function decrypt(text: string) {
    return CryptoJS.AES.decrypt(text, Config.key).toString(CryptoJS.enc.Utf8);
}
