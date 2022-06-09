const CryptoJS = require("crypto-js");

export function encrypt(text: string) {
    return CryptoJS.AES.encrypt(text, process.env.key).toString();
}

export function decrypt(text: string) {
    return CryptoJS.AES.decrypt(text, process.env.key).toString(CryptoJS.enc.Utf8);
}
