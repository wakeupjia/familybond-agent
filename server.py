import os
from contextlib import asynccontextmanager

from dotenv import load_dotenv
from fastapi import FastAPI
from pydantic import BaseModel

from agent import create_familybond_agent

load_dotenv()

agent = None


class InvokeRequest(BaseModel):
    user_id: str
    user_role: str = "elder"
    message: str
    source: str = "feishu"
    session_id: str = ""


class InvokeResponse(BaseModel):
    reply_text: str
    intent: str = ""
    memory_written: bool = False
    meta: dict = {}


@asynccontextmanager
async def lifespan(_app: FastAPI):
    global agent
    agent = create_familybond_agent()
    yield


app = FastAPI(title="FamilyBond Agent", lifespan=lifespan)


@app.post("/invoke", response_model=InvokeResponse)
async def invoke(req: InvokeRequest):
    result = agent.invoke(
        {
            "messages": [
                {
                    "role": "user",
                    "content": f"user_role={req.user_role}\nmessage={req.message}",
                }
            ],
        }
    )

    final_message = result["messages"][-1]
    reply_text = final_message.content if hasattr(final_message, "content") else str(final_message)

    intent = _extract_intent(req.user_role, req.message)

    return InvokeResponse(
        reply_text=reply_text,
        intent=intent,
        memory_written=True,
        meta={"used_context": True},
    )


def _extract_intent(user_role: str, message: str) -> str:
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


if __name__ == "__main__":
    import uvicorn

    port = int(os.environ.get("AGENT_PORT", 9000))
    uvicorn.run("server:app", host="0.0.0.0", port=port, reload=True)
