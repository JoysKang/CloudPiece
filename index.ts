const { Client } = require("@notionhq/client")

const Config = require("./conf.json")


const notion = new Client({ auth: Config.relationCode });

async function getUserData(chatId: string): Promise<string[]> {
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


(async () => {
    const [databaseId, accessToken, pageId] = await getUserData("")
    console.log(databaseId, accessToken, pageId)
})();