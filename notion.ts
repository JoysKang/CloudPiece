const { Client } = require("@notionhq/client")

const Config = require("./conf.json")

const relationNotion = new Client({ auth: Config.relationCode });

export async function createRelation(username: string, chatId: string): Promise<boolean> {
    const [_, __, pageId] = await getDatabaseIdAndAccessToken(chatId)
    if (pageId) {
        return false
    }

    const pageArgs = {
        "parent": {"database_id": Config.relationDatabaseId},
        "properties": {
            "Name": {
                "title": [
                    {
                        "text": {
                            "content": username
                        }
                    }
                ]
            },
            "ChatId": {
                "rich_text": [
                    {
                        "text": {
                            "content": chatId
                        }
                    }
                ]
            }
        },
    }
    try {
        await relationNotion.pages.create(pageArgs)
        return true
    } catch (error) {
        console.log(error)
        return false
    }
}

export async function deleteRelation(chatId: string) {
    const [_, __, pageId] = await getDatabaseIdAndAccessToken(chatId)
    const response = await relationNotion.blocks.delete({
        block_id: pageId,
    });
    console.log(response);
}

export async function updateRelation(chatId: string, accessToken: string, databaseId: string, code: string) {
    const [_, __, pageId] = await getDatabaseIdAndAccessToken(chatId)
    const pageArgs = {
        "parent": {"database_id": Config.relationDatabaseId},
        "properties": {}
    }
    if (accessToken) {
        pageArgs.properties["AccessToken"] = {
            "rich_text": [
                {
                    "text": {
                        "content": accessToken
                    }
                }
            ]
        }
    }
    if (databaseId) {
        pageArgs.properties["DatabaseId"] = {
            "rich_text": [
                {
                    "text": {
                        "content": databaseId
                    }
                }
            ]
        }
    }
    if (code) {
        pageArgs.properties["Code"] = {
            "rich_text": [
                {
                    "text": {
                        "content": code
                    }
                }
            ]
        }
    }

    await relationNotion.pages.update({
        page_id: pageId,
        properties: pageArgs.properties
    });
}

// 获取用户基础数据
async function getDatabaseIdAndAccessToken(chatId: string): Promise<string[]> {
    const response = await relationNotion.databases.query({
        database_id: Config.relationDatabaseId,
        filter: {
            or: [
                {
                    property: 'ChatId',
                    rich_text: {
                        equals: chatId,
                    },
                },
            ],
        }
    });
    if (response.results.length === 0) {
        console.log("No entry found")
        return []
    }

    if (response.results[0].properties.DatabaseId.rich_text === null ||
        response.results[0].properties.AccessToken.rich_text === null) {
        console.log("No entry found")
        return []
    }

    let databaseId: string = ''
    if (response.results[0].properties.DatabaseId.rich_text.length !== 0) {
        databaseId = response.results[0].properties.DatabaseId.rich_text[0].plain_text
    }

    let accessToken: string = ''
    if (response.results[0].properties.AccessToken.rich_text.length !== 0) {
        accessToken = response.results[0].properties.AccessToken.rich_text[0].plain_text
    }

    const pageId: string = response.results[0].id
    return [databaseId, accessToken, pageId]
}

function writeTitle(title: string): { title: { text: { content: string } }[] } {
    return {
        "title": [
            {
                "text": {
                    "content": title,
                },
            },
        ]
    }
}

function writeIcon(): { type: string; emoji: string  } {
    return {
        type: "emoji",
        emoji: "🥬"
    }
}

function writeCover(url: string): { type: string, external: { url: string } } {
    return {
        type: "external",
        external: {
            url: url
        }
    }
}

function writeText(text: string) {
    return {
        "object": "block",
        "type": "paragraph",
        "paragraph": {
            "rich_text": [
                {
                    "type": "text",
                    "text": {
                        "content": text
                    }
                }
            ]
        }
    }
}

function writeImage(url: string) {
    return {
        "type": "image",
        "image": {
            "type": "external",
            "external": {
                "url": url
            }
        }
    }
}

function writeBookmark(url: string): { bookmark: { url: string }; type: string;} {
    return {
        "type": "bookmark",
        "bookmark": {
            "url": url
        }
    }
}

function writeMap(url: string) {
    return {
        "object": "block",
        "type": "embed",
        "embed": {
            "url": url
        }
    }
}

function writeDocument(url: string) {
    return {
        "type": "file",
        "file": {
            "type": "external",
            "external": {
                "url": url
            }
        }
    }
}

function writeVideo(url: string) {
    return {
        "type": "video",
        "video": {
            "type": "external",
            "external": {
                "url": url
            }
        }
    }
}

async function writePage(chatId: string, databaseId: string, accessToken: string, title: string, content: string): Promise<boolean> {
    const pageArgs = {
        parent: {
            database_id: databaseId,
        },
        properties: {
        },
        children: []
    }
    pageArgs["icon"] = writeIcon()
    pageArgs["cover"] = writeCover("https://upload.wikimedia.org/wikipedia/commons/6/62/Tuscankale.jpg")
    pageArgs["properties"]["Name"] = writeTitle(title)
    pageArgs["children"].push(writeText(content))
    pageArgs["children"].push(writeBookmark("https://zh.odysseydao.com/pathways/intro-to-web3"))

    const clientNotion = new Client({ auth: accessToken });
    try {
        await clientNotion.pages.create(pageArgs)
        return true
    } catch (error) {
        console.log(error)
        return false
    }
}

export async function writeNotion(chatId: string, title: string, content: string): Promise<boolean> {
    const [databaseId, accessToken, _] = await getDatabaseIdAndAccessToken(chatId)
    if (databaseId === "" || accessToken === "") {
        return false
    }
    return await writePage(chatId, databaseId, accessToken, title, content)
}

(async () => {
    // const [databaseId, accessToken, pageId] = await getDatabaseIdAndAccessToken("682824244")
    // console.log(await writePage("", databaseId, accessToken, "Tuscan Kale", "Lacinato kale is a variety of kale with a long tradition in Italian cuisine, especially that of Tuscany. It is also known as Tuscan kale, Italian kale, dinosaur kale, kale, flat back kale, palm tree kale, or black Tuscan palm."))

    await createRelation("joys", "682824244")
    // await updateRelation("682824244", "682824244", Config.relationDatabaseId, "joys")
    // await deleteRelation("682824244")
})();