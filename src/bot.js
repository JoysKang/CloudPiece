"use strict";
var __awaiter = (this && this.__awaiter) || function (thisArg, _arguments, P, generator) {
    function adopt(value) { return value instanceof P ? value : new P(function (resolve) { resolve(value); }); }
    return new (P || (P = Promise))(function (resolve, reject) {
        function fulfilled(value) { try { step(generator.next(value)); } catch (e) { reject(e); } }
        function rejected(value) { try { step(generator["throw"](value)); } catch (e) { reject(e); } }
        function step(result) { result.done ? resolve(result.value) : adopt(result.value).then(fulfilled, rejected); }
        step((generator = generator.apply(thisArg, _arguments || [])).next());
    });
};
var __generator = (this && this.__generator) || function (thisArg, body) {
    var _ = { label: 0, sent: function() { if (t[0] & 1) throw t[1]; return t[1]; }, trys: [], ops: [] }, f, y, t, g;
    return g = { next: verb(0), "throw": verb(1), "return": verb(2) }, typeof Symbol === "function" && (g[Symbol.iterator] = function() { return this; }), g;
    function verb(n) { return function (v) { return step([n, v]); }; }
    function step(op) {
        if (f) throw new TypeError("Generator is already executing.");
        while (_) try {
            if (f = 1, y && (t = op[0] & 2 ? y["return"] : op[0] ? y["throw"] || ((t = y["return"]) && t.call(y), 0) : y.next) && !(t = t.call(y, op[1])).done) return t;
            if (y = 0, t) op = [op[0] & 2, t.value];
            switch (op[0]) {
                case 0: case 1: t = op; break;
                case 4: _.label++; return { value: op[1], done: false };
                case 5: _.label++; y = op[1]; op = [0]; continue;
                case 7: op = _.ops.pop(); _.trys.pop(); continue;
                default:
                    if (!(t = _.trys, t = t.length > 0 && t[t.length - 1]) && (op[0] === 6 || op[0] === 2)) { _ = 0; continue; }
                    if (op[0] === 3 && (!t || (op[1] > t[0] && op[1] < t[3]))) { _.label = op[1]; break; }
                    if (op[0] === 6 && _.label < t[1]) { _.label = t[1]; t = op; break; }
                    if (t && _.label < t[2]) { _.label = t[2]; _.ops.push(op); break; }
                    if (t[2]) _.ops.pop();
                    _.trys.pop(); continue;
            }
            op = body.call(thisArg, _);
        } catch (e) { op = [6, e]; y = 0; } finally { f = t = 0; }
        if (op[0] & 5) throw op[1]; return { value: op[0] ? op[1] : void 0, done: true };
    }
};
exports.__esModule = true;
var telegraf_1 = require("telegraf");
var Koa = require('koa');
var koaBody = require('koa-body');
var safeCompare = require('safe-compare');
var Config = require("../conf.json");
var _a = require("./notion"), createRelation = _a.createRelation, deleteRelation = _a.deleteRelation;
var _b = require("./encryption"), encrypt = _b.encrypt, decrypt = _b.decrypt;
var token = Config.telegramToken;
if (token === undefined) {
    throw new Error('BOT_TOKEN must be provided!');
}
var bot = new telegraf_1.Telegraf(token, {
    telegram: { webhookReply: true }
});
bot.command('start', function (ctx) {
    // Explicit usage
    var text = "\n    \u6B22\u8FCE\u4F7F\u7528\u3010CloudPiece\u3011\n    CloudPiece \u80FD\u591F\u5FEB\u901F\u8BB0\u5F55\u4F60\u7684\u60F3\u6CD5\u5230 Notion \u7B14\u8BB0\u4E2D\u3002\u5FEB\u901F\u8BB0\u5F55\uFF0C\u4E0D\u6D41\u5931\u4EFB\u4F55\u4E00\u4E2A\u7075\u611F\u3002\n    1. \u8BF7\u62F7\u8D1D [\u6A21\u677F](https://joys.notion.site/fa90a1d7e8404e1286f66941dafd4155) \u5230\u81EA\u5DF1\u7684 Notion \u4E2D\n    2. \u4F7F\u7528 /bind \u547D\u4EE4\u6388\u6743 CloudPiece \u8BBF\u95EE\uFF0C\u5728\u6388\u6743\u9875\u9762\u9009\u62E9\u4F60\u521A\u521A\u62F7\u8D1D\u7684\u6A21\u677F(\u6CE8\uFF1A\u9519\u8BEF\u7684\u9009\u62E9\u5C06\u65E0\u6CD5\u6B63\u5E38\u4F7F\u7528 CloudPiece)\n    3. \u8F93\u5165 test,\u4F60\u5C06\u6536\u5230 \u3010\u5DF2\u5B58\u50A8\u3011\u7684\u53CD\u9988\uFF0C\u8FD9\u65F6\u4F60\u7684\u60F3\u6CD5\u5DF2\u7ECF\u5199\u5165\u5230 Notion\uFF0C\u5FEB\u53BB Notion \u770B\u770B\u5427~\n\n    \u5982\u679C CloudPiece \u4E0D\u80FD\u4F7F\u4F60\u6EE1\u610F\uFF0C\u4F60\u53EF\u4EE5\u5230 [github](https://github.com/JoysKang/CloudPiece/issues) \u63D0 issues,\n    \u6216\u5230[\u7559\u8A00\u677F](https://joys.notion.site/c144f89764564f928c31f162e0ff307a) \u7559\u8A00,\n    \u6216\u53D1\u90AE\u4EF6\u81F3 licoricepieces@gmail.com,\n    \u6216\u76F4\u63A5\u4F7F\u7528 /unbind \u8FDB\u884C\u89E3\u7ED1\uFF0C\u7136\u540E\u5230\u62F7\u8D1D\u7684\u6A21\u677F\u9875\uFF0C\u70B9\u51FB\u53F3\u4E0A\u89D2\u7684 Share \u6309\u94AE\uFF0C\u4ECE\u91CC\u8FB9\u79FB\u9664 CloudPiece\u3002\n    ";
    ctx.telegram.sendMessage(ctx.message.chat.id, text, {
        parse_mode: 'Markdown',
        disable_web_page_preview: true
    });
    // Using context shortcut
    ctx.leaveChat();
});
// 绑定
bot.command('bind', function (ctx) { return __awaiter(void 0, void 0, void 0, function () {
    var username, chat_id, isCreated, state, text;
    return __generator(this, function (_a) {
        switch (_a.label) {
            case 0:
                username = "";
                chat_id = ctx.message.chat.id;
                return [4 /*yield*/, createRelation(username, chat_id)];
            case 1:
                isCreated = _a.sent();
                if (!isCreated) {
                    return [2 /*return*/, ctx.reply('已绑定, 无需再次绑定')];
                }
                state = encrypt(ctx.message.chat.id);
                text = "[点击授权](https://api.notion.com/v1/oauth/authorize?owner=user&client_id=" +
                    Config.clientId + "&redirect_uri=" + Config.redirectUri + "&response_type=code&state=" + state;
                return [4 /*yield*/, ctx.telegram.sendMessage(ctx.message.chat.id, text, {
                        parse_mode: 'Markdown',
                        disable_web_page_preview: true
                    })];
            case 2:
                _a.sent();
                return [2 /*return*/];
        }
    });
}); });
// 解绑
bot.command('unbind', function (ctx) { return __awaiter(void 0, void 0, void 0, function () {
    var text;
    return __generator(this, function (_a) {
        switch (_a.label) {
            case 0: 
            // Explicit usage
            return [4 /*yield*/, deleteRelation(ctx.message.chat.id)];
            case 1:
                // Explicit usage
                _a.sent();
                text = "解绑完成，如需继续使用，请先使用 /bind 进行绑定";
                return [4 /*yield*/, ctx.telegram.sendMessage(ctx.message.chat.id, text, {
                        parse_mode: 'Markdown',
                        disable_web_page_preview: true
                    })];
            case 2:
                _a.sent();
                return [2 /*return*/];
        }
    });
}); });
bot.on('text', function (ctx) {
    // Explicit usage
    ctx.telegram.sendMessage(ctx.message.chat.id, "Hello ".concat(ctx.state.role));
    // Using context shortcut
    ctx.reply("Hello ".concat(ctx.state.role));
});
bot.on('callback_query', function (ctx) {
    // Explicit usage
    ctx.telegram.answerCbQuery(ctx.callbackQuery.id);
    // Using context shortcut
    ctx.answerCbQuery();
});
bot.on('inline_query', function (ctx) {
    var result = [];
    // Explicit usage
    ctx.telegram.answerInlineQuery(ctx.inlineQuery.id, result);
    // Using context shortcut
    ctx.answerInlineQuery(result);
});
// bot.launch()
var secretPath = "/telegraf/".concat(bot.secretPathComponent());
// webhook
bot.telegram.setWebhook("".concat(Config.webhookHost).concat(secretPath));
// Enable graceful stop
// process.once('SIGINT', () => bot.stop('SIGINT'))
// process.once('SIGTERM', () => bot.stop('SIGTERM'))
var app = new Koa();
app.use(koaBody());
app.use(function (ctx, next) { return __awaiter(void 0, void 0, void 0, function () {
    return __generator(this, function (_a) {
        switch (_a.label) {
            case 0:
                if (!safeCompare(secretPath, ctx.url)) return [3 /*break*/, 2];
                return [4 /*yield*/, bot.handleUpdate(ctx.request.body)];
            case 1:
                _a.sent();
                ctx.status = 200;
                return [2 /*return*/];
            case 2: return [2 /*return*/, next()];
        }
    });
}); });
app.listen(3000);
