import os
import json
import tempfile
import subprocess
import asyncio
import requests
from discord.ext import commands
from groq import Groq

GROQ_API_KEY   = os.getenv("GROQ_API_KEY")
DISCORD_TOKEN  = os.getenv("DISCORD_TOKEN")
MEME_API       = "https://meme-api.com/gimme"

client = Groq(api_key=GROQ_API_KEY)

class CircularArray:
    def __init__(self, size):
        self.size  = size
        self.array = []

    def append(self, element):
        self.array.append(element)
        if len(self.array) > self.size:
            self.array.pop(0)

    def get_context(self):
        return " ".join(self.array)

def _compile_python_code(input_code: str) -> str:
    with tempfile.NamedTemporaryFile("w+", suffix=".py", delete=False) as f:
        f.write(input_code)
        path = f.name

    proc = subprocess.run(
        ["python", path],
        capture_output=True,
        text=True,
        timeout=5,
    )
    return proc.stdout + proc.stderr

async def compile_python_code(input_code: str) -> str:
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(None, _compile_python_code, input_code)

def _call_llm(user_query: str, context: str) -> str:
    system_prompt = (
        "You are a knowledgeable programming expert. "
        f"Context: {context}"
    )
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user",   "content": user_query},
    ]
    resp = client.chat.completions.create(
        messages=messages,
        model="mixtral-8x7b-32768",
        temperature=0.4,
    )
    return resp.choices[0].message.content

async def call_llm(user_query: str, context: str) -> str:
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(None, _call_llm, user_query, context)

def _get_meme() -> str:
    try:
        r = requests.get(MEME_API, timeout=5)
        r.raise_for_status()
        data = r.json()
        return data.get("url", "No URL in response.")
    except Exception:
        return "Could not fetch a meme right now."

async def get_meme() -> str:
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(None, _get_meme)

intents = discord.Intents.default()
intents.message_content = True
bot    = commands.Bot(command_prefix="!", intents=intents)
memory = {}

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")

@bot.command(name="ask", description="Ask a question")
async def ask(ctx, *, question: str):
    uid   = ctx.author.id
    convo = memory.setdefault(uid, CircularArray(15))

    convo.append(f"User: {question}")
    context = convo.get_context()

    answer = await call_llm(question, context)

    convo.append(f"Bot: {answer}")
    await ctx.send(answer)

@bot.command(name="compile", description="Compile and run Python code")
async def _compile(ctx, *, code: str):
    output = await compile_python_code(code)
    await ctx.send(f"```\n{output}\n```")

@bot.command(name="meme", description="Get a meme")
async def _meme(ctx):
    url = await get_meme()
    await ctx.send(url)

bot.run(DISCORD_TOKEN)

