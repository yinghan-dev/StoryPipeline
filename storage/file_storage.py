import os

def save_chapter(chapter_number: int, text: str):
    os.makedirs("chapters", exist_ok=True)
    filename = f"chapters/chapter_{chapter_number}.md"
    with open(filename, "w", encoding="utf-8") as f:
        f.write(text)
    return filename

def load_previous_chapters(upto: int) -> str:
    text = ""
    for i in range(1, upto):
        filename = f"chapters/chapter_{i}.md"
        if os.path.exists(filename):
            with open(filename, "r", encoding="utf-8") as f:
                text += f.read() + "\n\n"
    return text
