import json
from typing import List
from concurrent.futures import ThreadPoolExecutor
from matplotlib import pyplot as plt

from models import Chat


class Simulation:
    def __init__(self, n: int = 0):
        self.n = n
        self.chats:List[Chat] = [Chat("decision_making",i) for i in range(n)]
        self.distribution = {}  # length: frequency
        self.jsons =[]  # json to serialize

    def run(self):
        with ThreadPoolExecutor(max_workers=5) as executor:
            for chat in self.chats:
                print(f'executing chat {chat.chat_id}')
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
        with open('simulation.json', 'w') as f:
            json.dump(self.jsons, f)


    @staticmethod
    def visualizeJSON(filename):
        jsons:List[dict] = json.load(open(filename, 'r'))
        for chat in jsons:
            for key,val in chat.items():
                print(f'{key}: {val}')
            print('=='*10)

if __name__ == '__main__':
    sim = Simulation(50)
    sim.run()
    sim.plot_distribution()
    sim.write_to_file()
    Simulation.visualizeJSON('simulation.json')