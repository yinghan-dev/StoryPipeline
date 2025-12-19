# StoryPipeline — 数据驱动小说创作工作流

## 🌼项目功能

StoryPipeline 是一个 **数据驱动的小说生成工作流**，通过结构化 CSV 数据描述世界观、人物、阵营、章节和事件，AI 根据这些约束生成连贯章节正文。  

不同于完全依赖 AI，StoryPipeline 强调 **人类创作可控性**：  
- 生成章节可**随时中断或续写**  
- 文本可以**本地修改**，保持作者最终决策权  
- 数据结构化 + 分层约束让 AI 输出更连贯，同时保持可编辑性  

## 🔧核心技术支持
- 数据驱动创作
-- 使用 CSV 结构化管理人物、国家、阵营、事件、章节和时间线，保证故事逻辑清晰，同时允许用户本地修改生成结果，保持创作主动权。
- 分层约束与 AI 辅助
-- 世界背景、事件顺序、人物关系和章节目标分层约束 AI 输出，使章节连贯可读。AI 仅作为辅助，作者掌控故事节奏。
- 流式生成与实时服务
-- 基于 FastAPI + uvicorn 提供流式生成接口，章节生成可随时中断或续写，支持高效迭代与本地保存。


❗该项目是我作为非计算机专业学生的一次尝试，旨在更高效的完成小说创作，同时也能保证高度的自主性，目前只做了后端，希望有能力的大佬能给我这个项目封装完善，感兴趣的话欢迎💡fork和给个⭐star


## ⚙项目架构
```
StoryPipeline/
│
├─ storage/ # 文件存储模块
│ └─ file_storage.py
│
├─ chapters/ # 用于存放生成的小说章节
├─ data/ # CSV 数据表
│ ├─ factions.csv #自定义阵营/势力，比国家概念大
│ ├─ countries.csv #自定义国家
│ ├─ characters.csv #自定义角色
│ ├─ chapters.csv #自定义每章内容
│ ├─ storyline.csv # 自定义小说阶段，比如1-3章是铺垫,4-6章是战争..
│ ├─ timeline.csv # 世界事件
│ └─ events.csv # 事件，用于串起章节的具体内容
│ └─ storyoverview.md # 用于确定小说整体走向
│ └─ storyline.md # 生成章节后形成摘要，给后文生成提供参考
│
├─ .env # 存放API
├─ models.py # 数据模型定义
├─ llm_client.py # AI 模型接口
├─ main.py # FastAPI 服务入口
└─ README.md
```

## 🚀快速开始
### 1.安装依赖
```bash
pip install -r requirements.txt
```

### 2.配置API
在.env文件中录入API。当前项目采用OPENAI的接口，我给的是deepseek-chat模型，可以在llm_client.py更改模型。

### 3.更改各个csv文件
参考项目/data文件夹
建议顺序如下：
1. story_overview.md 确定小说走向
2. timeline.csv 确定小说大的阶段
3. chapters.csv 确定章节内容
4. events.csv 确定章节展开
5. characters.csv 确定人物
6. countries.csv/factions.csv 确认国家/派系

### 4.启动FastAPI 服务
```bash
uvicorn main:app --reload
```

### 5.生成文本
🔍浏览器访问
```
127.0.0.1:8000/chapter_flow?chapter_number=1
```
- 实时返回章节正文流，需要逐章生成
- 生成结果保存到 chapters/ 文件夹

### 6.后期修改
可以在生成某章后修改storyline.md和chapter 序号.md文件，检查有无生成错误

## 未来计划
1. 加入逻辑检查程序
2. 封装前端，做交互UI
3. 加入embedding，支持文本库检索

