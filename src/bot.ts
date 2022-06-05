import {Telegraf} from 'telegraf'
const Koa = require('koa')
const koaBody = require('koa-body')
const safeCompare = require('safe-compare')

const Config = require("../conf.json")
const { createRelation, deleteRelation } = require("./notion")
const { encrypt, decrypt } = require("./encryption")


const token = Config.telegramToken
if (token === undefined) {
    throw new Error('BOT_TOKEN must be provided!')
}

const bot = new Telegraf(token, {
    telegram: { webhookReply: true }
})

bot.command('start', (ctx) => {
    // Explicit usage
    const text = `
    欢迎使用【CloudPiece】
    CloudPiece 能够快速记录你的想法到 Notion 笔记中。快速记录，不流失任何一个灵感。
    1. 请拷贝 [模板](https://joys.notion.site/fa90a1d7e8404e1286f66941dafd4155) 到自己的 Notion 中
    2. 使用 /bind 命令授权 CloudPiece 访问，在授权页面选择你刚刚拷贝的模板(注：错误的选择将无法正常使用 CloudPiece)
    3. 输入 test,你将收到 【已存储】的反馈，这时你的想法已经写入到 Notion，快去 Notion 看看吧~

    如果 CloudPiece 不能使你满意，你可以到 [github](https://github.com/JoysKang/CloudPiece/issues) 提 issues,
    或到[留言板](https://joys.notion.site/c144f89764564f928c31f162e0ff307a) 留言,
    或发邮件至 licoricepieces@gmail.com,
    或直接使用 /unbind 进行解绑，然后到拷贝的模板页，点击右上角的 Share 按钮，从里边移除 CloudPiece。
    `
    ctx.telegram.sendMessage(ctx.message.chat.id, text, {
        parse_mode: 'Markdown',
        disable_web_page_preview: true,
    })

    // Using context shortcut
    ctx.leaveChat()
})

// 绑定
bot.command('bind', async (ctx) => {
    // const username = ctx.message.chat.username
    const username = ""
    const chat_id = ctx.message.chat.id
    const isCreated = await createRelation(username, chat_id)
    if (!isCreated) {
        return ctx.reply('已绑定, 无需再次绑定')
    }

    const state = encrypt(ctx.message.chat.id)
    const text = "[点击授权](https://api.notion.com/v1/oauth/authorize?owner=user&client_id=" +
        Config.clientId + "&redirect_uri=" + Config.redirectUri + "&response_type=code&state=" + state
    await ctx.telegram.sendMessage(ctx.message.chat.id, text, {
        parse_mode: 'Markdown',
        disable_web_page_preview: true,
    })
})

// 解绑
bot.command('unbind', async (ctx) => {
    // Explicit usage
    await deleteRelation(ctx.message.chat.id)

    const text = "解绑完成，如需继续使用，请先使用 /bind 进行绑定"
    await ctx.telegram.sendMessage(ctx.message.chat.id, text, {
        parse_mode: 'Markdown',
        disable_web_page_preview: true,
    })
})

bot.on('text', (ctx) => {
    // Explicit usage
    ctx.telegram.sendMessage(ctx.message.chat.id, `Hello ${ctx.state.role}`)

    // Using context shortcut
    ctx.reply(`Hello ${ctx.state.role}`)
})

bot.on('callback_query', (ctx) => {
    // Explicit usage
    ctx.telegram.answerCbQuery(ctx.callbackQuery.id)

    // Using context shortcut
    ctx.answerCbQuery()
})

bot.on('inline_query', (ctx) => {
    const result = []
    // Explicit usage
    ctx.telegram.answerInlineQuery(ctx.inlineQuery.id, result)

    // Using context shortcut
    ctx.answerInlineQuery(result)
})

// bot.launch()

const secretPath = `/telegraf/${bot.secretPathComponent()}`

// webhook
bot.telegram.setWebhook(`${Config.webhookHost}${secretPath}`)

// Enable graceful stop
// process.once('SIGINT', () => bot.stop('SIGINT'))
// process.once('SIGTERM', () => bot.stop('SIGTERM'))

const app = new Koa()
app.use(koaBody())
app.use(async (ctx, next) => {
    if (safeCompare(secretPath, ctx.url)) {
        await bot.handleUpdate(ctx.request.body)
        ctx.status = 200
        return
    }
    return next()
})
app.listen(3000)
