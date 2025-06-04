import ollama

response = ollama.chat(
    model='phi',
    messages=[
        {'role': 'user', 'content': 'open notepad.exe and write them and save .txt'}
    ]
)

print(response['message']['content'])
