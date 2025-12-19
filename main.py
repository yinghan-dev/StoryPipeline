import csv
from fastapi import FastAPI, Query
from fastapi.responses import StreamingResponse

from models import Event
from storage.file_storage import save_chapter
from llm_client import stream_chat

app = FastAPI()


# ========== 基础数据加载 ==========

def load_csv(filepath: str):
    with open(filepath, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def load_events_from_csv(filepath: str, characters_map):
    """
    加载事件，并将人物 ID 映射为 canonical_name
    """
    events = []
    with open(filepath, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            participant_ids = row["characters"].split(";")
            participants = [
                characters_map[cid]["canonical_name"]
                for cid in participant_ids
                if cid in characters_map
            ]

            events.append(
                Event(
                    event_id=row["event_id"],
                    chapter_id=row["chapter_id"],
                    order_in_chapter=int(row["order_in_chapter"]),
                    year=int(row["year"]),
                    month=int(row["month"]),
                    location=row["location"],
                    characters=";".join(participants),
                    scene_type=row["scene_type"],
                    plot_direction=row["plot_direction"],
                )
            )
    return events


# ========== 路由入口 ==========

@app.get("/chapter_flow")
def chapter_flow(chapter_number: int = Query(1)):

    # ---- 加载基础数据 ----
    factions = {r["faction_id"]: r for r in load_csv("data/factions.csv")}
    countries = {r["country_id"]: r for r in load_csv("data/countries.csv")}
    characters = {r["character_id"]: r for r in load_csv("data/characters.csv")}
    chapters = {r["chapter_id"]: r for r in load_csv("data/chapters.csv")}
    timeline = load_csv("data/timeline.csv")
    events = load_events_from_csv("data/events.csv", characters)

    chapter_id = str(chapter_number)
    if chapter_id not in chapters:
        return {"error": f"章节 {chapter_number} 不存在"}

    chapter_info = chapters[chapter_id]

    # ---- 本章事件 ----
    chapter_events = sorted(
        [e for e in events if e.chapter_id == chapter_id],
        key=lambda e: e.order_in_chapter,
    )

    # ---- 涉及人物 / 国家 / 阵营 ----
    involved_characters = {
        ch["character_id"]: ch
        for ch in characters.values()
        if ch["canonical_name"] in ";".join(e.characters for e in chapter_events)
    }

    involved_countries = {
        c["country_id"]: c
        for c in countries.values()
        if c["country_id"]
        in {ch["country_id"] for ch in involved_characters.values()}
    }

    involved_factions = {
        f["faction_id"]: f
        for f in factions.values()
        if f["faction_id"]
        in {c["faction_id"] for c in involved_countries.values()}
    }

    # ========== Prompt 构造 ==========

    prompt = f"# 第{chapter_number}章 {chapter_info['chapter_title']}\n"

    # 世界背景
    prompt += "\n【世界背景约束】\n"
    for f in involved_factions.values():
        prompt += f"阵营 {f['name']}，核心科技：{f['core_tech']}，意识形态：{f['ideology']}。\n"

    for c in involved_countries.values():
        faction_name = factions[c["faction_id"]]["name"]
        prompt += (
            f"国家 {c['name']}（隶属阵营：{faction_name}），"
            f"政体：{c['regime']}，媒体生态：{c['media_ecology']}，立场：{c['alignment']}。\n"
        )

    # 时间线
    prompt += "\n【宏观时间线约束】\n"
    chapter_time_points = {(e.year, e.month) for e in chapter_events}
    for entry in timeline:
        if (int(entry["year"]), int(entry["month"])) in chapter_time_points:
            prompt += (
                f"{entry['year']}年{entry['month']}月，"
                f"{entry['location']}，{entry['actors']}，"
                f"{entry['event_type']}：{entry['impact']}。\n"
            )

    # 人物
    prompt += "\n【人物表约束】\n"
    for ch in involved_characters.values():
        country = countries[ch["country_id"]]["name"]
        faction = factions[countries[ch["country_id"]]["faction_id"]]["name"]
        titles = ",".join(ch["titles"].split(";"))
        prompt += (
            f"- {ch['canonical_name']}（可用称呼：{titles}），"
            f"国家：{country}（阵营：{faction}），"
            f"职业：{ch['profession']}，性格：{ch['personality']}\n"
        )

    # 章节目标
    prompt += (
        f"\n【章节目标约束】\n"
        f"必须在结尾体现：{chapter_info['chapter_goal']}\n"
        f"章节氛围：{chapter_info['chapter_tone']}\n"
    )

    # 事件叙事
    prompt += "\n【本章事件】\n"
    prompt += "请将以下场景自然融合为一个完整叙事，不要使用小标题或编号：\n"

    scenes = []
    for e in chapter_events:
        participants = e.characters.replace(";", "、")
        scenes.append(
            f"在{e.year}年{e.month}月的{e.location}，涉及人物：{participants}，"
            f"这是一次{e.scene_type}场面，事件结束后局势变化：{e.plot_direction}"
        )

    prompt += "；".join(scenes) + "。\n"
    prompt += "\n请根据以上约束生成完整章节正文，保持连贯叙事。"

    # ========== 流式生成 ==========

    def event_stream():
        collected = []

        for chunk in stream_chat(prompt, model="deepseek-chat"):
            collected.append(chunk)
            yield chunk

        full_text = "".join(collected)

        # 保存章节正文
        chapter_text = f"# 第{chapter_number}章 {chapter_info['chapter_title']}\n\n{full_text}"
        save_chapter(chapter_number, chapter_text)

        # 生成章节摘要（供后续章节参考）
        summary_prompt = (
            "请用一个简洁段落总结以下章节已发生的主要事件与走向，"
            "不要使用分点，不要补充未发生内容：\n\n"
            f"{full_text}"
        )

        summary = "".join(
            stream_chat(summary_prompt, model="deepseek-chat")
        )

        with open("data/storyline.md", "a", encoding="utf-8") as f:
            f.write(
                f"## 第{chapter_number}章 {chapter_info['chapter_title']}\n"
                f"{summary}\n\n"
            )

    return StreamingResponse(event_stream(), media_type="text/plain")
