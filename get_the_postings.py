import sys
import pickle

term = sys.argv[1]

with open('dictionary.txt','rb') as f:
    dic = pickle.load(f)

print(dic[term])

offset = dic[term][1]
with open('postings.txt','rb') as f:
    f.seek(offset)
    print(pickle.load(f))
