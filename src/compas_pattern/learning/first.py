categories = ['alt.atheism', 'soc.religion.christian', 'comp.graphics', 'sci.med']

from sklearn.datasets import fetch_20newsgroups

twenty_train = fetch_20newsgroups(subset='train', categories=categories, shuffle=True, random_state=42)

print twenty_train.target_names

print len(twenty_train.data)

print len(twenty_train.filenames)

print("\n".join(twenty_train.data[0].split("\n")[:3]))

print(twenty_train.target_names[twenty_train.target[0]])

print twenty_train.target[:10]

for t in twenty_train.target[:10]:
    print(twenty_train.target_names[t])