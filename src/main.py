import json
import os
import subprocess
import requests
import discord
import threading

from discord.ext import commands
from groq import Groq

# Meme API endpoint
meme_api = 'https://meme-api.com/gimme'

client = Groq(api_key="<key>")

def compile_python_code(input_code):
    try:
        # Create a temporary Python file
        with open("temp", "w") as f:
            f.write(input_code)
        # Execute the Python code
        process = subprocess.run(["python", "temp"], capture_output=True)
        # Return the output
        return process.stdout.decode()
    except Exception as e:
        return f"Error during compilation: {e}"

def call(prompt, conversation=None):

    introduction = """
        You are a knowledgeable and experienced programming expert, 
        able to provide detailed explanations, write code, and solve problems. 
        You can answer questions, provide examples, and engage in conversations. 
        Your expertise includes languages such as Python, Java, JavaScript, and C++, 
        as well as various frameworks, libraries, and technologies.
    """ if not conversation else ""

    if conversation is None:
        conversation = []
    else:
        conversation.append(prompt)

    messages = [{"role": "user", "content": message} for message in conversation]

    if not conversation:
        messages.insert(0, {"role": "system", "content": introduction})

    payload = {
        "messages": messages,
        "model": "mixtral-8x7b-32768",
        "temperature": 0.4
    }

    response = client.chat.completions.create(**payload)
    return response.choices[0].message.content

def get_meme():
    response = requests.get(meme_api)
    json_data = json.loads(response.text)
    return json_data['url']

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='!', intents=intents)

conversations = {}

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}')

@bot.command(name="ask", description="Ask a question")
async def ask(ctx, *, question: str):
    user_id = ctx.author.id
    if user_id not in conversations:
        message_content = call(question)
        conversations[user_id] = []
    else:
        conversations[user_id].append(question)
        message_content = call(question, conversations[user_id])
    await ctx.send(message_content)

@bot.command(name="compile", description="Compile Python code")
async def compile(ctx, *, code: str):
    try:
        # Attempt to compile the code
        compiled_code = compile(code, "<string>", "exec")
        message_content = "Code compiled successfully!"
    except SyntaxError as e:
        # Handle syntax errors
        message_content = f"Syntax error: {e}"
    except Exception as e:
        # Handle other exceptions
        message_content = f"An error occurred: {e}"
    await ctx.send(f"```\n{message_content}\n```")

@bot.command(name="meme", description="Get a meme")
async def meme(ctx):
    message_content = get_meme()
    await ctx.send(message_content)

bot.run('<token>')
