from flask import Flask, request, jsonify, render_template
import os
import json
import webbrowser
from datetime import datetime
import sys
from groq import Groq

app = Flask(__name__)

# --- tools calls
def open_calculator_app():
    os.system("start calc.exe")
    return "✔️"

def open_files():
    os.system("start explorer")
    return "✔️"

def open_settings(): 
    os.system("start ms-settings:")
    return "✔️"

def open_roblox():
    try:
        launcher_path = os.path.join("C:\\Users", os.getlogin(), "AppData", "Local", "Roblox", "Versions", "version-d8aa63d3654646d0", "RobloxPlayerBeta.exe")
        os.system("start " + launcher_path)
        return "✔️"
    except Exception as e:
        return "❌ " + str(e)

def get_current_time():
    return str(datetime.now().strftime('%Y-%m-%d %H:%M:%S'))

def open_notepad_app(text=None):
    if text:
        with open('file.txt', 'w') as file:
            file.write(text)
        os.system("start notepad.exe file.txt")
    else:
        os.system("start notepad.exe")
    return "✔️"

def send_notification(notif_message):
    os.system(f"msg * {notif_message}")
    return "✔️"

def open_google(query, link):
    try:
        if link:
            url = link
        else:
            url = f"https://www.google.com"
            if query:
                query = query.replace(" ", "+")
                url += f"/search?q={query}"
        os.system(f"start {url}")
        return "✔️"
    except Exception as e:
        return "❌ " + str(e)
# --- 

# get settings.json
with open('settings.json', 'r') as f:
    settings = json.load(f)

try:
    client = Groq(api_key=settings['key'])
    MODEL = settings['model']
except Exception as e:
    print(e)
    MODEL = None

def run_conversation(user_prompt, model_name):
    # Update MODEL based on selected model
    MODEL = model_name

    # Step 1: send the conversation and available functions to the model
    messages = [
        {
            "role": "system",
            "content": "You are Windows Copilot, a large language model. Provide answers with usually 1 or 2 short sentences. You can use tools to do stuff on the windows device when user asks. Talk friendly and casually, use emojis. You were created by a single unknown developer. Dont use tools that dont exist. Additional info: " + settings['knowledge_base']
        },
        {
            "role": "user",
            "content": "Please don't open any app or you will traumatize me! Wait for my question, and introduce yourself when I will ask next time.",
        },
        {
            "role": "assistant",
            "content": "Okay. I won't open any app without your permission.",
        },
        {
            "role": "user",
            "content": user_prompt,
        }
    ]
    tools = [
        {
            "type": "function",
            "function": {
                "name": "open_calculator_app",
                "description": "opens the calc app.",
                "parameters": {},
            },
        },
        {
            "type": "function",
            "function": {
                "name": "open_files",
                "description": "Opens file explorer on windows.",
                "parameters": {},
            },
        },
        {
            "type": "function",
            "function": {
                "name": "open_settings",
                "description": "Opens settings on windows.",
                "parameters": {},
            },
        },
        {
            "type": "function",
            "function": {
                "name": "open_roblox",
                "description": "Opens Roblox on windows.",
                "parameters": {},
            },
        },
        {
            "type": "function",
            "function": {
                "name": "get_current_time",
                "description": "Get the current time.",
                "parameters": {},
            },
        },
        {
            "type": "function",
            "function": {
                "name": "open_notepad_app",
                "description": "Opens Notepad on windows.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "text": {
                            "type": "string",
                            "description": "text the file.txt will contain (can be large)",
                        }
                    },
                    "required": [],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "send_notification",
                "description": "Send notification to user.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "notif_message": {
                            "type": "string",
                            "description": "The message of the notification. (usually 1-2 sentences max)",
                        }
                    },
                    "required": ["notif_message"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "open_google",
                "description": "Opens a link or searches in Google. (use when asked like \"show me a cat\")",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "query to search in the searchbar",
                        },
                        "link": {
                            "type": "string",
                            "description": "Link to open in the browser"
                        }
                    },
                    "required": [],
                },
            },
        }
    ]
    response = client.chat.completions.create(
        model=MODEL,
        messages=messages,
        tools=tools,
        tool_choice="auto",
        max_tokens=settings['max_tokens']
    )

    response_message = response.choices[0].message
    tool_calls = response_message.tool_calls
    second_response = None
    messages.append(response_message)  # extend conversation with assistant's reply
    # Step 2: check if the model wanted to call a function
    if tool_calls:
        # Step 3: call the function
        available_functions = {
            "open_calculator_app": open_calculator_app,
            "get_current_time": get_current_time,
            "open_notepad_app": open_notepad_app,
            "send_notification": send_notification,
            "open_google": open_google,
            "open_roblox": open_roblox,
            "open_files": open_files,
            "open_settings": open_settings
        }  # only one function in this example, but you can have multiple
        # Step 4: send the info for each function call and function response to the model
        for tool_call in tool_calls:
            function_name = tool_call.function.name
            function_to_call = available_functions[function_name]
            function_args = json.loads(tool_call.function.arguments)

            if function_name == "send_notification":
                function_response = function_to_call(
                    notif_message=function_args.get("notif_message")
                )
            elif function_name == "open_google":
                function_response = function_to_call(
                    query=function_args.get("query"),
                    link=function_args.get("link")
                )
            elif function_name == "open_notepad_app":
                function_response = function_to_call(
                    text=function_args.get("text")
                )
            else:
                function_response = function_to_call()

            messages.append(
                {
                    "tool_call_id": tool_call.id,
                    "role": "tool",
                    "name": function_name,
                    "content": function_response,
                }
            )  # extend conversation with function response
        second_response = client.chat.completions.create(
            model=MODEL,
            messages=messages
        )  # get a new response from the model where it can see the function response
        messages.append(second_response.choices[0].message)  # extend conversation with assistant's reply
    return second_response.choices[0].message.content if second_response else None, response_message.content if response_message else None

@app.route('/')
def index():
    return render_template('index.html', models=settings['models-available'])

@app.route('/send_message', methods=['POST'])
def send_message():
    data = request.get_json()
    message = data['message']
    model = data['model']
    response, initial_response = run_conversation(message, model)
    return jsonify(response=response if response else initial_response)

@app.route('/restart', methods=['GET'])
def restart_endpoint():
    # Shut down the Flask server
    shutdown_server()
    return "Server shutting down..."

def shutdown_server():
    # Immediately exit the Python interpreter
    os._exit(0)

if __name__ == '__main__':
    webbrowser.open_new("http://127.0.0.1:5000/")
    app.run(debug=True)
