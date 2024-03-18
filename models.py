import json
from typing import List
from openai import OpenAI


class Agent:
    def __init__(self, agent_id: int, background: str):
        self.id = agent_id
        self.background = background
        self.convo_memory = []  # type: List[str]

    def addConvoMemory(self, conversation: str):
        self.convo_memory.append(conversation)

    def getConvoMemory(self) -> str:
        return '\n'.join(self.convo_memory)
    
    def getBackground(self) -> str:
        return self.background
    
    def getId(self) -> int:
        return self.id


class Chat:
    def __init__(self, sim_case: str):
        with open('prompts.json', 'r', encoding='utf-8') as f:
            prompt_data = json.load(f)

        self.max_turns = prompt_data["max_turns"]
        self.system_prompt = prompt_data['system_prompt']
        self.user_prompt = prompt_data['user_prompt']
        self.topic = prompt_data[sim_case]["topic"]
        self.response_format = prompt_data[sim_case]["response_format"]
        self.num_agents = prompt_data[sim_case]["num_agents"]
        self.agents = []
        for agent in prompt_data[sim_case]["agents"]:
            new_agent = Agent(agent["id"], agent["background"])
            self.agents.append(new_agent)
        
        with open('config.secret', 'r') as f:
            api_key = f.read()
        self.client = OpenAI(api_key=api_key)


    def getResponse(self, order: int) -> str:
        complete_system_prompt = self.system_prompt.format(self.num_agents, self.topic, self.response_format)
        complete_user_prompt = self.user_prompt.format(order, self.agents[order - 1].getBackground(), self.agents[order - 1].getConvoMemory(), order)
        # print()
        # print()
        # print("===============================================")
        # print(complete_system_prompt)
        # print()
        # print(complete_user_prompt)
        # print("===============================================")
        
        response = self.client.chat.completions.create(
            model="gpt-4",
            messages=[
                {
                    "role": "system",
                    "content": complete_system_prompt
                },
                {
                    "role": "user",
                    "content": complete_user_prompt
                }
            ]
        )

        content = response.choices[0].message.content
        for agent in self.agents:
            agent.addConvoMemory(content)
        return content

    def getOrder(self):  # round robin
        return [i + 1 for i in range(self.num_agents)] * ((self.max_turns // self.num_agents) + 1)

    def start(self):
        count = 0
        orders = self.getOrder()

        while count < self.max_turns:
            response = self.getResponse(orders[count]).strip()
            count += 1
            print(response)

            if response.endswith('END OF CONVERSATION'):
                print('break')
                break

        print('Chat ended')


if __name__ == '__main__':
    chat = Chat()
    chat.start()
