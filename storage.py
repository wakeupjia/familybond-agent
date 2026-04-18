import json
import os

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")


def ensure_data_dir():
    os.makedirs(DATA_DIR, exist_ok=True)


def read_json(filename: str, default):
    path = os.path.join(DATA_DIR, filename)
    if not os.path.exists(path):
        write_json(filename, default)
        return default
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def write_json(filename: str, data):
    ensure_data_dir()
    path = os.path.join(DATA_DIR, filename)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def load_family_context() -> str:
    data = read_json("family_context.json", {
        "family_name": "Jia Family",
        "elder_profile": {
            "name": "爷爷",
            "notes": [
                "不熟悉英文词汇和现代生活方式名词",
                "更容易理解朴素、生活化的表达",
                "不喜欢太复杂的长句",
            ],
        },
        "young_profile": {
            "name": "孙女",
            "notes": [
                "最近工作较忙",
                "正在准备一个 AI 比赛项目",
            ],
        },
        "shared_facts": [
            "爷爷平时喜欢种菜",
            "爷爷最近需要注意血压记录",
            "解释时应该使用温和、尊重长辈的语气",
            "不要把长辈当作小孩来讲话",
            "不要做医疗诊断，只做生活记录与提醒",
        ],
    })
    return json.dumps(data, ensure_ascii=False, indent=2)


def load_recent_updates() -> str:
    data = read_json("recent_updates.json", [])
    if not data:
        return "暂无生活近况记录。"
    return json.dumps(data, ensure_ascii=False, indent=2)


def load_health_logs() -> str:
    data = read_json("health_logs.json", [])
    if not data:
        return "暂无健康记录。"
    return json.dumps(data, ensure_ascii=False, indent=2)


def load_translation_logs() -> str:
    data = read_json("translation_logs.json", [])
    if not data:
        return "暂无转译记录。"
    return json.dumps(data, ensure_ascii=False, indent=2)


def save_recent_update(record: dict):
    data = read_json("recent_updates.json", [])
    data.append(record)
    write_json("recent_updates.json", data)


def save_health_log_record(record: dict):
    data = read_json("health_logs.json", [])
    data.append(record)
    write_json("health_logs.json", data)


def save_translation_log_record(record: dict):
    data = read_json("translation_logs.json", [])
    data.append(record)
    write_json("translation_logs.json", data)
