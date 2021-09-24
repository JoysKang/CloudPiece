# CloudPiece

本着 All in one 的思想，实在不想再换或者加笔记了(累了)，所以就有了 CloudPiece。
用来记录开车、神游、喝酒等等时迸发的新思路、新玩法，如果你也喜欢 或 能帮到你，
请 star。


### 技术选型

Aiohttp + aiogram + Notion + sentry + 腾讯云函数  
用 Aiohttp 做 web 服务，用 telegram 官方的 SDK aiogram 连接 telegram，
Notion database 做数据库和笔记，sentry 做日志记录，腾讯云函数做服务器。


### 配置说明
注意这里因为要和朋友一起使用，所以有两个 integrations,   
一个用来记录授权数据(private integrations), 数据也是记录在 Notion；  
一个是用来转发消息的(public integrations), public integrations 会将发到 CloudPiece 的数据转存到 Notion。 **本服务不记录任何数据，只做转发**；    

如果你是自己使用，完全不用这么复杂，直接使用一个 private integrations 就能实现，也不用记录授权关系，直接 fork 修改就好。  

或者直接使用[该服务](https://telegram.me/CloudPieceBot), 为次还特意加了[留言板](https://joys.notion.site/c144f89764564f928c31f162e0ff307a)
```json
{
  "relation_code": "private integrations 授权码",
  "relation_database_id": "授权关系数据库id",
  "client_id": "public integrations 中的 client_id",
  "client_secret": "public integrations 中的 client_secret",
  "redirect_uri": "public integrations 回调地址",
  "telegram_token": "telegram bot token",
  "key": "Oauth2 对 state 进行加密解密的key(保证 telegram 和 notion 授权一对一的关系)",
  "webhook_host": "腾讯云函数网关地址",
  "notion_version": "notion api 版本",
  "sentry_address": "sentry 项目key"
}
```

### 启动

```shell
# 启动后有个问题，我没尝试，不知道怎么连接 telegram，
# 我本地只是为了测试 Notion，
# 和 telegram 联动的测试都是部署后测的
uvicorn app:app --host 0.0.0.0 --port 9000  
# 或   
docker run -it -p 9000:9000 cloudpiece
```

### 独立部署
因为是镜像部署，比较简单，这里就不详细列了，简单说下：
1. 将 conf_back.json 改为 conf.json，修改里边的配置；
2. build 自己的镜像，并上传到腾讯云镜像仓库；
3. 到云函数页面，选择 web 函数，镜像部署，直接部署就可以了
(可以先创建 ap i网关，第一部要用，也可以部署创建，修改参数再 build、部署一次。
不要问我为什么知道😂)；
4. 另我申请了腾讯云函数预置并发的内测，建议也申请个，否则发一个消息，
几十秒才有回馈，总感觉出错了，这中体验很不好😯。

### 后续
一些小伙伴不用 telegram，用微信，但没有开发过微信生态的东西，后续再说。
