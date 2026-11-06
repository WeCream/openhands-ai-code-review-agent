import os

from openhands.sdk import LLM, Agent, Conversation, Tool
from openhands.sdk.tool import register_tool

from src.openhands_adapter.code_review_tool import CodeReviewTool


# Agent 和 Reviewer 使用同一个 DeepSeek Key，但配置名称不同
api_key = os.getenv("LLM_API_KEY") or os.getenv("DEEPSEEK_API_KEY")
if not api_key:
    raise RuntimeError(
        "请先设置 LLM_API_KEY 或 DEEPSEEK_API_KEY，不能把 API Key 写进代码。"
    )

os.environ.setdefault("DEEPSEEK_API_KEY", api_key)

# 注册我们自己实现的 OpenHands Tool
register_tool(CodeReviewTool.name, CodeReviewTool)

llm = LLM(
    model=os.getenv("LLM_MODEL", "deepseek/deepseek-chat"),
    api_key=api_key,
    base_url=os.getenv("LLM_BASE_URL", "https://api.deepseek.com"),
)

agent = Agent(
    llm=llm,
    tools=[Tool(name=CodeReviewTool.name)],
)

conversation = Conversation(
    agent=agent,
    workspace=os.getcwd(),
)

sample_diff = """diff --git a/app.py b/app.py
index 1111111..2222222 100644
--- a/app.py
+++ b/app.py
@@ -1,2 +1,2 @@
 def get_user(user_id):
-    return db.query("SELECT * FROM users WHERE id = ?", user_id)
+    return db.query("SELECT * FROM users WHERE id = " + user_id)
"""

conversation.send_message(
    "请调用 code_review 工具审查下面的 Git Diff。"
    "不要自行代替工具进行代码审查。请总结工具返回的审查结果。\n\n"
    + sample_diff
)

conversation.run()
print("OpenHands CodeReview Agent test finished.")
