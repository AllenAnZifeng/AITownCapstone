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
    def __init__(self, sim_case: str, chat_id:int):
        with open('prompts.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
        self.chat_id = chat_id
        self.count = 0
        self.chat_history = []
        convo_data = data["conversation"]
        self.convo_max_turns = convo_data["max_turns"]
        self.convo_system_prompt = convo_data['system_prompt']
        self.convo_user_prompt = convo_data['user_prompt']

        eval_data = data["evaluation"]
        self.eval_system_prompt = eval_data['system_prompt']
        self.eval_user_prompt = eval_data['user_prompt']

        sim_case_data = data["simulation_cases"][sim_case]
        self.topic = sim_case_data["topic"]
        self.response_format = sim_case_data["response_format"]
        self.evaluation_prompts = sim_case_data["evaluation_prompts"]
        self.num_agents = sim_case_data["num_agents"]
        self.agents = []
        self.debug = False
        for agent in sim_case_data["agents"]:
            new_agent = Agent(agent["id"], agent["background"])
            self.agents.append(new_agent)
                    
        with open('config.secret', 'r') as f:
            api_key = f.read()
        self.client = OpenAI(api_key=api_key)


    def getResponse(self, order: int) -> str:
        complete_system_prompt = self.convo_system_prompt.format(self.num_agents, self.topic, self.response_format)
        complete_user_prompt = self.convo_user_prompt.format(order, self.agents[order - 1].getBackground(), self.agents[order - 1].getConvoMemory(), order)
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
        self.chat_history.append(content)
        for agent in self.agents:
            agent.addConvoMemory(content)
        return content
    def getChatJSON(self):
        history = '\n'.join(self.chat_history)
        obj = {
            'chatID': self.chat_id,
            'count': self.count,
            'memo': history
        }
        return obj
    def getOrder(self):  # round robin
        return [i + 1 for i in range(self.num_agents)] * ((self.convo_max_turns // self.num_agents) + 1)

    def start(self):

        orders = self.getOrder()

        while self.count < self.convo_max_turns:
            response = self.getResponse(orders[self.count]).strip()
            self.count += 1
            if self.debug:
                print(response)

            if response.endswith('END OF CONVERSATION'):
                if self.debug:
                    print('break')
                break

        print(f'Chat {self.chat_id} ended')
    
    def eval_agents(self):
        for i, agent in enumerate(self.agents):
            print("===============================================")
            print(f"evaluating agent {i + 1}:")
            complete_system_prompt = ""
            complete_user_prompt = ""
            for prompt in self.evaluation_prompts:
                complete_system_prompt = self.eval_system_prompt.format(prompt)
                complete_user_prompt = self.eval_user_prompt.format(i + 1, agent.getBackground(), agent.getConvoMemory(), i + 1)
                print(f"evaluation prompt: {prompt}")
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
                print(f"answer: {content}")


if __name__ == '__main__':
    chat = Chat("decision_making")
    chat.start()
