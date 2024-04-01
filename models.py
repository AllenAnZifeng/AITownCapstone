import json
import threading
from concurrent.futures import ThreadPoolExecutor
from typing import List
import matplotlib
from matplotlib import pyplot as plt
from openai import OpenAI
import pickle

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
    def __init__(self, chat_id: int, sim_case: str, strategy: str):
        with open('prompts.json', 'r', encoding='utf-8') as f:
            data = json.load(f)

        self.chatID = chat_id
        self.strategy = strategy
        self.count = 0
        self.convo_history = []
        self.debug = False

        convo_data = data["conversation"]
        self.convo_max_turns = convo_data["max_turns"]
        self.convo_system_prompt = convo_data['system_prompt']
        self.convo_user_prompt = convo_data['user_prompt']

        eval_data = data["evaluation"]
        self.eval_system_prompt = eval_data['system_prompt']
        self.eval_user_prompt = eval_data['user_prompt']

        mod_data = data["moderator"]
        self.mod_system_prompt = mod_data['system_prompt']
        self.mod_user_prompt = mod_data['user_prompt']

        sim_case_data = data["simulation_cases"][sim_case]
        self.topic = sim_case_data["topic"]
        self.response_format = sim_case_data["response_format"]
        self.evaluation_prompts = sim_case_data["evaluation_prompts"]
        self.num_agents = sim_case_data["num_agents"]

        self.agents = []
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
            model="gpt-4",  # gpt-4
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
        self.convo_history.append(content)
        for agent in self.agents:
            agent.addConvoMemory(content)
        return content


    def getConvoHistory(self):
        return '\n'.join(self.convo_history)


    def getChatJSON(self):
        obj = {
            'chatID': self.chatID,
            'count': self.count,
            'memo': self.getConvoHistory()
        }
        return obj
    
    def getNextAgent(self):
        complete_system_prompt = self.mod_system_prompt.format(self.num_agents, self.topic)
        complete_user_prompt = self.mod_user_prompt.format(self.agents[0].getConvoMemory(), self.num_agents)
        
        response = self.client.chat.completions.create(
            model="gpt-4",  # gpt-4
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
        return int(content)


    def start(self):
        if self.strategy == "round_robin":
            orders = [i + 1 for i in range(self.num_agents)] * ((self.convo_max_turns // self.num_agents) + 1)
            while self.count < self.convo_max_turns:
                response = self.getResponse(orders[self.count]).strip()
                self.count += 1
                print(response)
                print(f'Chat {self.chatID}: count {self.count}!')
                if 'END OF CONVERSATION' in response:
                    print('break')
                    break
        elif self.strategy == "moderator":
            while self.count < self.convo_max_turns:
                next_agent = self.getNextAgent()
                print("next agent: ", next_agent)
                response = self.getResponse(next_agent).strip()
                self.count += 1
                print(response)
                print(f'Chat {self.chatID}: count {self.count}!')
                if 'END OF CONVERSATION' in response:
                    print('break')
                    break
        print(f'Chat {self.chatID}: ended!')

    
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

class Benchmark:
    def __init__(self, n: int, sim_case: str, strategy: str):
        self.n = n
        self.chats:List[Chat] = [Chat(i, sim_case, strategy) for i in range(n)]
        self.distribution = {}  # length: frequency
        self.jsons =[]  # json to serialize


    def run(self):
        with ThreadPoolExecutor(max_workers=5) as executor:
            for chat in self.chats:
                print(f'executing chat {chat.chatID}')
                executor.submit(chat.start)


        self.chats.sort(key=lambda x: x.count, reverse=True)
        for chat in self.chats:
            if chat.count not in self.distribution:
                self.distribution[chat.count] = 0
            self.distribution[chat.count] += 1
            self.jsons.append(chat.getChatJSON())

        for i in range(max(self.distribution.keys())+1):
            if i not in self.distribution:
                self.distribution[i] = 0
    

    def plot_distribution(self):
        data = list(self.distribution.items())

        lengths = [item[0] for item in data]
        frequencies = [item[1] for item in data]

        plt.hist(lengths, weights=frequencies, bins=len(lengths), alpha=0.5)

        plt.xlabel('Length')
        plt.ylabel('Frequency')
        plt.title('Distribution of lengths')

        plt.show()


    def write_to_file(self):
        with open('benchmark.json', 'w') as f:
            json.dump(self.jsons, f)


    @staticmethod
    def visualizeJSON(filename):
        jsons:List[dict] = json.load(open(filename, 'r'))
        for chat in jsons:
            for key,val in chat.items():
                print(f'{key}: {val}')
            print('=='*10)


if __name__ == '__main__':
    sim = Benchmark(5, "decision_making", "round_robin")
    sim.run()
    sim.plot_distribution()
    sim.write_to_file()    
    sim.visualizeJSON('benchmark.json')
