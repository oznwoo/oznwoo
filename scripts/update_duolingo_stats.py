import json
import os
import re
import urllib.request

START_MARKER = "<!--START_SECTION:duolingoStats-->"
END_MARKER = "<!--END_SECTION:duolingoStats-->"

FLAGS = {
    "de": "🇩🇪",
    "en": "🇬🇧",
    "ja": "🇯🇵",
    "fr": "🇫🇷",
    "es": "🇪🇸",
    "zh": "🇨🇳",
}


def fetch_stats(user_id: str, jwt: str) -> dict:
    url = (
        f"https://www.duolingo.com/2017-06-30/users/{user_id}"
        "?fields=username,streak,totalXp,courses,streakData"
    )
    request = urllib.request.Request(url, headers={"Authorization": f"Bearer {jwt}"})
    with urllib.request.urlopen(request) as response:
        return json.load(response)


def render_section(stats: dict) -> str:
    streak = stats.get("streak", 0)
    total_xp = stats.get("totalXp", 0)
    courses = stats.get("courses", [])

    lines = [f"🔥 **{streak}-day streak** · ⭐ **{total_xp:,} XP**", ""]
    if courses:
        lines += ["| Language | XP |", "|---|---|"]
        for course in courses:
            flag = FLAGS.get(course.get("learningLanguage", ""), "🏳️")
            lines.append(f"| {flag} {course.get('title', '')} | {course.get('xp', 0):,} |")

    return "\n".join(lines)


def update_readme(readme_path: str, section: str) -> None:
    with open(readme_path, encoding="utf-8") as file:
        content = file.read()

    pattern = re.compile(
        re.escape(START_MARKER) + r".*?" + re.escape(END_MARKER), re.DOTALL
    )
    replacement = f"{START_MARKER}\n\n{section}\n\n{END_MARKER}"
    new_content = pattern.sub(replacement, content)

    with open(readme_path, "w", encoding="utf-8") as file:
        file.write(new_content)


def main() -> None:
    user_id = os.environ["DUOLINGO_USER_ID"]
    jwt = os.environ["DUOLINGO_JWT"]
    readme_path = os.environ.get("README_PATH", "README.md")

    stats = fetch_stats(user_id, jwt)
    section = render_section(stats)
    update_readme(readme_path, section)


if __name__ == "__main__":
    main()
