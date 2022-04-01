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

async function writePage(chatId: string, databaseId: string, accessToken: string, title: string, content: string): Promise<boolean> {
    const clientNotion = new Client({ auth: accessToken });
    try {
        await clientNotion.pages.create({
            parent: {
                database_id: databaseId,
            },
            icon: {
                type: "emoji",
                emoji: "🥬"
            },
            cover: {
                type: "external",
                external: {
                    url: "https://upload.wikimedia.org/wikipedia/commons/6/62/Tuscankale.jpg"
                }
            },
            properties: {
                Name: {
                    title: [
                        {
                            text: {
                                content: title,
                            },
                        },
                    ],
                }
            },
            children: [
                {
                    object: 'block',
                    type: 'heading_2',
                    heading_2: {
                        rich_text: [
                            {
                                type: 'text',
                                text: {
                                    content: 'Lacinato kale',
                                },
                            },
                        ],
                    },
                },
                {
                    object: 'block',
                    type: 'paragraph',
                    paragraph: {
                        rich_text: [
                            {
                                type: 'text',
                                text: {
                                    content: content,
                                    link: {
                                        url: 'https://en.wikipedia.org/wiki/Lacinato_kale',
                                    },
                                },
                            },
                        ],
                    },
                },
            ],
        });
        return true
    } catch (error) {
        console.log(error)
        return false
    }
}

(async () => {
    const [databaseId, accessToken, pageId] = await getUserData("")
    console.log(await writePage("", databaseId, accessToken, "Tuscan Kale", "Lacinato kale is a variety of kale with a long tradition in Italian cuisine, especially that of Tuscany. It is also known as Tuscan kale, Italian kale, dinosaur kale, kale, flat back kale, palm tree kale, or black Tuscan palm."))
})();