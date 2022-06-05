"use strict";
exports.__esModule = true;
exports.decrypt = exports.encrypt = void 0;
var CryptoJS = require("crypto-js");
var Config = require("../conf.json");
function encrypt(text) {
    return CryptoJS.AES.encrypt(text, Config.key).toString();
}
exports.encrypt = encrypt;
function decrypt(text) {
    return CryptoJS.AES.decrypt(text, Config.key).toString(CryptoJS.enc.Utf8);
}
exports.decrypt = decrypt;
