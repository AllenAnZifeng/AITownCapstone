from openai import OpenAI
import json

if __name__ == "__main__":
    with open('config.secret', 'r') as f:
        api_key = f.read()
    client = OpenAI(api_key=api_key)

    with open('single_agent_prompts.json', 'r', encoding='utf-8') as f:
        data = json.load(f)

    topic = data["problem_solving"]["topic"]
    example = data["problem_solving"]["example"]

    response = client.chat.completions.create(
        model="gpt-3.5-turbo",  # gpt-4
        messages=[
            {
                "role": "system",
                "content": topic
            },
            {
                "role": "user",
                "content": example
            }
        ]
    )

    content = response.choices[0].message.content
    print(content)