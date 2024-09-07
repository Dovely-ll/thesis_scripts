from openai import OpenAI

client = OpenAI(api_key='sk-B6vehdpQ2qhNEcE6IznkCokkVj4SPr0snKUlka-XxBT3BlbkFJhAN6ukKoy4gnpoq9ggPN4cZpioASpLqn3Zh0LuZbQA')
import os
import sys

# Initialize the OpenAI API key

# Function to interact with ChatGPT with chat history
def ask_chatgpt(messages):
    try:
        # Call the ChatGPT model using OpenAI's API
        response = client.chat.completions.create(model="gpt-3.5-turbo",  # Use either 'gpt-4' or 'gpt-3.5-turbo'
            messages=messages,  # Pass the entire message history
            max_tokens=500  # Adjust the response length
        )

        # Extract the response content
        return response.choices[0].message.content
    except Exception as e:
        return f"Error: {e}"

def get_conf_classes(path, keyword):
    contents = {}
    for root, dirs, files in os.walk(path):
        for file in files:
            if 'test' not in root and '.java' in file and keyword.lower() in file.lower():
                file_path = os.path.join(root, file)
                with open(file_path, 'r', encoding='utf-8') as f:
                    # contents = f.readlines()
                    content = f.read()
                    contents[file] = content
    return contents

if __name__ == '__main__':
    print("ChatGPT API is ready! Type 'exit' to quit.")

    models = OpenAI.Model.list()
    for model in models['data']:
        print(model['id'])

    # Initialize the conversation history with an empty list
    chat_history = []

    setup = """I'm analyzing the configuration system of 18 projects. 
    So, I will give you a java class file each time,
    and you need to tell me how many constructors are there,
    how many configuration getter methods are there,
    and how many setter methods are there.
    If you understand my demand, answer yes."""
    chat_history.append({"role": "user", "content": setup})
    response = ask_chatgpt(chat_history)
    chat_history.append({"role": "assistant", "content": response})
    print("ChatGPT's response:")
    print(response)

    keyword = sys.argv[1]
    path = sys.argv[2]
    contents = get_conf_classes(path, keyword)

    for file in contents:   
        # Add the user input to the conversation history
        chat_history.append({"role": "user", "content": contents[file]})

        # Get response from ChatGPT
        response = ask_chatgpt(chat_history)

        # Add ChatGPT's response to the conversation history
        chat_history.append({"role": "assistant", "content": response})

        # Print the response from ChatGPT
        print("ChatGPT's response for class {file}:")
        print(response)

    while False:
        # Get user input for the prompt
        user_input = input("Enter your prompt: ")

        # Exit the loop if the user types 'exit'
        if user_input.lower() == "exit":
            print("Exiting...")
            break

        # Add the user input to the conversation history
        chat_history.append({"role": "user", "content": user_input})

        # Get response from ChatGPT
        response = ask_chatgpt(chat_history)

        # Add ChatGPT's response to the conversation history
        chat_history.append({"role": "assistant", "content": response})

        # Print the response from ChatGPT
        print("ChatGPT's response:")
        print(response)
