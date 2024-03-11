import json
import threading
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
    def __init__(self, chatID: int = 0):
        with open('prompts.json', 'r', encoding='utf-8') as f:
            prompt_data = json.load(f)

        self.chatID = chatID
        self.count = 0
        self.convo_history = []
        self.max_turns = prompt_data["max_turns"]
        self.system_prompt = prompt_data['system_prompt']
        self.user_prompt = prompt_data['user_prompt']
        self.topic = prompt_data["topic"]
        self.response_format = prompt_data["response_format"]
        self.num_agents = prompt_data["num_agents"]
        self.agents = []
        for agent in prompt_data["agents"]:
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
            model="gpt-3.5-turbo",  # gpt-4
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


    def getOrder(self):  # round robin
        return [i + 1 for i in range(self.num_agents)] * ((self.max_turns // self.num_agents) + 1)


    def getConvoHistory(self):
        return '\n'.join(self.convo_history)


    def getChatJSON(self):
        obj = {
            'chatID': self.chatID,
            'count': self.count,
            'memo': self.getConvoHistory()
        }
        return obj


    def start(self):
        orders = self.getOrder()
        while self.count < self.max_turns:
            response = self.getResponse(orders[self.count]).strip()
            self.count += 1
            print(response)
            print(f'Chat {self.chatID}: count {self.count}!')
            if 'END OF CONVERSATION' in response:
                print('break')
                break
        print(f'Chat {self.chatID}: ended!')


class Simulation:
    def __init__(self, n: int = 0):
        self.n = n
        self.chats:List[Chat] = [Chat(i) for i in range(n)]
        self.distribution = {}  # length: frequency
        self.jsons =[]  # json to serialize


    def run(self):
        threads = []
        for chat in self.chats:
            t = threading.Thread(target=chat.start)
            threads.append(t)
            t.start()
        for t in threads:
            t.join()

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
        with open('simulation.json', 'w') as f:
            json.dump(self.jsons, f)


    @staticmethod
    def visualizeJSON(filename):
        jsons:List[dict] = json.load(open(filename, 'r'))
        for chat in jsons:
            for key,val in chat.items():
                print(f'{key}: {val}')
            print('=='*10)
    # @staticmethod
    # def printJSONforChromeExtension(filename):
    #     jsons: List[dict] = json.load(open(filename, 'r'))
    #     for chat in jsons:
    #         print(chat)
    #         print('==' * 10)
    #         print()

if __name__ == '__main__':
    sim = Simulation(10)
    # sim.run()
    # sim.plot_distribution()
    # sim.write_to_file()


    sim.visualizeJSON('simulation.json')


    # with open('sim.pkl', 'wb') as f:
    #     pickle.dump(sim, f)
    #
    # # # Deserialize the sim object
    # # with open('sim.pkl', 'rb') as f:
    # #     sim = pickle.load(f)