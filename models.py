from typing import List

from openai import OpenAI


class Memory:
    def __init__(self):
        self.memory = []  # type: List[str]

    def add(self, conversation):
        self.memory.append(conversation)

    def get(self) -> str:
        return '\n'.join(self.memory)


class Chat:
    def __init__(self):
        self.memo = Memory()
        self.limit = 10
        self.number_of_agents = 3
        with open('config.secret', 'r') as f:
            api_key = f.read()
        self.client = OpenAI(api_key=api_key)
        with open('system_prompt.txt', 'r') as f:
            prompt_body = f.read()
        self.system_prompt = str(self.number_of_agents) + prompt_body

    def getResponse(self, order: int) -> str:
        response = self.client.chat.completions.create(
            model="gpt-4",
            messages=[
                {
                    "role": "system",
                    "content": self.system_prompt + self.memo.get()
                },
                {
                    "role": "user",
                    "content": f" Now Agent {order} is talking"
                }
            ]
        )

        content = response.choices[0].message.content
        self.memo.add(content)
        return content

    def getOrder(self):  # round robin
        return [i + 1 for i in range(self.number_of_agents)] * ((self.limit // self.number_of_agents) + 1)

    def start(self):
        count = 0
        orders = self.getOrder()

        while count < self.limit:
            response = self.getResponse(orders[count]).strip()
            count += 1
            print(response)

            if response.startswith('END OF CONVERSATION'):
                print('break')
                break

        print('Chat ended')


if __name__ == '__main__':
    chat = Chat()
    chat.start()
