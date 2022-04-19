const { Client } = require("@notionhq/client")

const Config = require("./conf.json")

// 获取用户基础数据
async function getUserData(chatId: string): Promise<string[]> {
    const notion = new Client({ auth: Config.relationCode });
    const response = await notion.databases.query({
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

    const databaseId: string = response.results[0].properties.DatabaseId.rich_text[0].plain_text
    const accessToken: string = response.results[0].properties.AccessToken.rich_text[0].plain_text
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

(async () => {
    const [databaseId, accessToken, pageId] = await getUserData("682824243")
    console.log(await writePage("", databaseId, accessToken, "Tuscan Kale", "Lacinato kale is a variety of kale with a long tradition in Italian cuisine, especially that of Tuscany. It is also known as Tuscan kale, Italian kale, dinosaur kale, kale, flat back kale, palm tree kale, or black Tuscan palm."))
})();