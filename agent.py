import argparse
import os

from deepagents import create_deep_agent
from deepagents.backends import FilesystemBackend
from dotenv import load_dotenv
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI
from rich.console import Console
from rich.panel import Panel

from storage import (
    load_family_context,
    load_recent_updates,
    save_health_log_record,
    save_recent_update,
    save_translation_log_record,
)

load_dotenv()
console = Console()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


# --- Tools ---


@tool
def classify_message(user_role: str, message: str) -> str:
    """对用户输入做轻量分类。返回 clarify / health / summarize / translation 之一。

    基础规则：
    - 包含"什么是"或"是什么意思" → clarify
    - 包含血压、吃药、药也吃了等健康关键词 → health
    - user_role == "elder" → summarize
    - 否则 → translation
    """
    health_keywords = ["血压", "吃药", "药也吃了", "心率", "血糖", "体温"]
    clarify_keywords = ["什么是", "是什么意思", "啥是", "啥叫"]

    for kw in clarify_keywords:
        if kw in message:
            return "clarify"
    for kw in health_keywords:
        if kw in message:
            return "health"
    if user_role == "elder":
        return "summarize"
    return "translation"


@tool
def get_family_context() -> str:
    """获取家庭长期背景信息，包括老人和年轻人的基本资料与共享事实。"""
    return load_family_context()


@tool
def get_recent_updates() -> str:
    """读取最近的生活近况摘要列表。"""
    return load_recent_updates()


@tool
def save_life_update(raw_text: str, summary: str, mood: str) -> str:
    """保存老人生活近况摘要。

    Args:
        raw_text: 老人原始输入文本
        summary: 概括后的生活近况摘要
        mood: 情绪状态描述
    """
    save_recent_update({
        "type": "life_update",
        "raw_text": raw_text,
        "summary": summary,
        "mood": mood,
    })
    return "生活近况已保存。"


@tool
def save_health_log(raw_text: str, parsed_result: str) -> str:
    """保存健康签到内容。

    Args:
        raw_text: 老人原始输入文本
        parsed_result: 提取的健康信息摘要
    """
    save_health_log_record({
        "type": "health_log",
        "raw_text": raw_text,
        "parsed_result": parsed_result,
    })
    return "健康记录已保存。"


@tool
def save_translation_result(original_text: str, translated_text: str) -> str:
    """保存年轻人原始消息与转译结果。

    Args:
        original_text: 年轻人原始消息
        translated_text: 转译后的老人友好文本
    """
    save_translation_log_record({
        "type": "translation",
        "original_text": original_text,
        "translated_text": translated_text,
    })
    return "转译记录已保存。"


# --- Agent Factory ---


def create_familybond_agent():
    model = ChatOpenAI(
        model="glm-5.1",
        base_url="https://open.bigmodel.cn/api/coding/paas/v4",
        api_key=os.environ.get("OPENAI_API_KEY", ""),
        temperature=0,
    )

    agent = create_deep_agent(
        model=model,
        memory=["./AGENTS.md"],
        skills=["./skills/"],
        tools=[
            classify_message,
            get_family_context,
            get_recent_updates,
            save_life_update,
            save_health_log,
            save_translation_result,
        ],
        subagents=[],
        backend=FilesystemBackend(root_dir=os.path.join(BASE_DIR, "runtime")),
        debug=True,
    )
    return agent


# --- CLI ---


def main():
    parser = argparse.ArgumentParser(
        description="FamilyBond 家话 — 陪伴型家庭 DeepAgent",
    )
    parser.add_argument(
        "--role",
        choices=["elder", "young"],
        required=True,
        help="输入角色：elder（老人）或 young（年轻人）",
    )
    parser.add_argument("message", help="输入消息内容")
    args = parser.parse_args()

    console.print(Panel("FamilyBond 家话", style="bold green", subtitle="陪伴型家庭 Agent"))

    agent = create_familybond_agent()

    result = agent.invoke(
        {
            "messages": [
                {
                    "role": "user",
                    "content": f"user_role={args.role}\nmessage={args.message}",
                }
            ],
        }
    )

    final_message = result["messages"][-1]
    response_text = final_message.content if hasattr(final_message, "content") else str(final_message)

    console.print(Panel(response_text, title="家话回复", style="blue"))


if __name__ == "__main__":
    main()
