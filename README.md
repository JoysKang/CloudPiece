# CloudPiece
Notion 云片


### 技术选型

1. FastAPI + Notion database


### 启动

uvicorn app:app --host 0.0.0.0 --port 9000


欢迎使用【CloudPiece】
    
CloudPiece 能够快速记录你的想法到 Notion 笔记中
1. 请拷贝 [模板](https://joys.notion.site/fa90a1d7e8404e1286f66941dafd4155) 到自己的 Notion 中  
2. 使用 /bind 命令授权 CloudPiece 访问，在授权页面选择你刚刚拷贝的模板(注：错误的选择将无法正常使用 CloudPiece)
3. 输入 test ，你将收到 【已存储】的反馈，这时你的想法/灵感已经写入到 Notion，快去 Notion 看看吧~

如果 CloudPiece 不能使你满意，你可以到 [反馈页面](https://joys.notion.site/CloudPiece-feedback-3cb2307641184267a6ad7f4f1e97d5a9) 进行反馈，或者直接使用 /unbind 进行解绑
