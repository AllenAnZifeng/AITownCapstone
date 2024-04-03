import json

from matplotlib import pyplot as plt

# d1 = {1:[1,2,3],2:[4,5,6]}
# d2 = {1:[7,8,9],2:[10,11,12]}
#
# res = [d1,d2]
# # Write self.res to a file
# with open('res.json', 'w') as f:
#     json.dump(res, f)
#
d = {}
for i in range(10):
    d[i] = 0

# d = {1:0,3:1,9:2}
d[2] = 10
data = list(d.items())
print(data)

lengths = [item[0] for item in data]
frequencies = [item[1] for item in data]

plt.hist(lengths, weights=frequencies, bins=len(lengths), alpha=0.5)

plt.xlabel('Length')
plt.ylabel('Frequency')
plt.title('Distribution of lengths')

plt.show()