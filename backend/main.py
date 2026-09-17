import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from pydantic import BaseModel
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, ToolMessage
from langchain_core.tracers.context import tracing_v2_enabled
from langchain_mcp_adapters.client import MultiServerMCPClient

load_dotenv()
MCP_URL = os.environ.get("MCP_URL", "http://127.0.0.1:8000/mcp")
llm = ChatGroq(model="openai/gpt-oss-120b", temperature=0)

tools_by_name = {}
llm_with_tools = None

async def load_tools():
    global tools_by_name, llm_with_tools
    client = MultiServerMCPClient({"datamind": {"url": MCP_URL, "transport": "streamable_http"}})
    tools = await client.get_tools()
    tools_by_name = {t.name: t for t in tools}
    llm_with_tools = llm.bind_tools(tools)

async def run_agent(question, max_turns=8):
    with tracing_v2_enabled(project_name="datamind-v2"):
        messages = [HumanMessage(question)]
        chart = None                                     # ← NEW: holds chart data
        for turn in range(max_turns):
            ai_msg = await llm_with_tools.ainvoke(messages)
            messages.append(ai_msg)
            if not ai_msg.tool_calls:
                return ai_msg.content, chart             # ← NEW: return both
            for tool_call in ai_msg.tool_calls:
                if tool_call["name"] == "make_chart":    # ← NEW: grab the chart data
                    chart = tool_call["args"]
                selected_tool = tools_by_name[tool_call["name"]]
                result = await selected_tool.ainvoke(tool_call["args"])
                messages.append(ToolMessage(str(result), tool_call_id=tool_call["id"]))
        return "Stopped: hit max turns.", chart          # ← NEW: return both

@asynccontextmanager
async def lifespan(app):
    await load_tools()      # load MCP tools once at startup
    yield

app = FastAPI(lifespan=lifespan)

class Question(BaseModel):
    question: str

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/ask")
async def ask(q: Question):
    answer, chart = await run_agent(q.question)
    return {"answer": answer, "chart": chart}