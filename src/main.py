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

class CircularArray:
    def __init__(self, size):
        self.size = size
        self.array = [None] * size
        self.start = 0
        self.end = 0

    def append(self, element):
        if self.array[self.end] is not None:
            self.start = (self.start + 1) % self.size
        self.array[self.end] = element
        self.end = (self.end + 1) % self.size

    def get(self, index):
        if index < 0 or index >= self.size:
            return None
        return self.array[(self.start + index) % self.size]

def compile_python_code(input_code):
    try:
        # Create a temporary Python file
        with open("temp.py", "w") as f:
            f.write(input_code)
        # Execute the Python code
        process = subprocess.run(["python", "temp.py"], capture_output=True)
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

    # send only first phrase only if conversation has not started
    if conversation is None:
        messages = [{"role": "user", "content": prompt}]
    else:
        conversation.append(prompt)
        messages = [{"role": "user", "content": conversation.get(i)} for i in range(conversation.size) if
                    conversation.get(i)]

    # send introduction if conversation has not started
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
        conversations[user_id] = CircularArray(15)
    else:
        conversations[user_id].append(question)
        message_content = call(question, conversations[user_id])
    await ctx.send(message_content)

@bot.command(name="compile", description="Compile and run Python code")
async def compile(ctx, *, code: str):
    try:
        # Attempt to compile the code
        output = compile_python_code(code)
        message_content = f"Output: {output}" if output else "Code executed successfully!"
    except Exception as e:
        # Handle other exceptions
        message_content = f"An error occurred: {e}"
    await ctx.send(f"```\n{message_content}\n```")

@bot.command(name="meme", description="Get a meme")
async def meme(ctx):
    message_content = get_meme()
    await ctx.send(message_content)

bot.run('<token>')
