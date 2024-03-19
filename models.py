import json
import threading
from typing import List
import matplotlib
from matplotlib import pyplot as plt
from openai import OpenAI
import pickle

class Memory:
    def __init__(self):
        self.memory = []  # type: List[str]

    def add(self, conversation):
        self.memory.append(conversation)

    def get(self) -> str:
        return '\n'.join(self.memory)


class Chat:
    def __init__(self, chatID: int):
        self.chatID = chatID
        self.memo = Memory()
        self.limit = 20
        self.number_of_agents = 3
        self.count = 0
        with open('config.secret', 'r') as f:
            api_key = f.read()
        self.client = OpenAI(api_key=api_key)
        with open('system_prompt.txt', 'r') as f:
            prompt_body = f.read()
        self.system_prompt = str(self.number_of_agents) + prompt_body

    def getResponse(self, order: int) -> str:
        response = self.client.chat.completions.create(
            model="gpt-3.5-turbo",  # gpt-4
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

    def getMemo(self):
        return self.memo.get()

    def getChatJSON(self):
        obj = {
            'chatID': self.chatID,
            'count': self.count,
            'memo': self.getMemo()
        }
        return obj

    def start(self):

        orders = self.getOrder()

        while self.count < self.limit:
            response = self.getResponse(orders[self.count]).strip()
            self.count += 1
            # print(response)
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