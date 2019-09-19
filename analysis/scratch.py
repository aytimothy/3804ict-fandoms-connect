from common import *
import math
import numpy as np
import matplotlib as plt

# Data is in DataFrame(s), just got to make generic tuples first.
data = get_local_data()
data = list(data.itertuples(index=False, name=None))

# Transform the data into a list of transactions grouped by the user.
transactions = []     # (user, [subreddits])
items = []
for node in data:
    if node[1] not in items:
        items.append(node[1])

    in_transactions = False
    for i in range(len(transactions)):
        if transactions[i][0] == node[0]:
            transactions[i][1].append(node[1])
            in_transactions = True
            break
    if not in_transactions:
        transactions.append((node[0], []))
        transactions[-1][1].append(node[1])

# Remove all users where they are part of less than 5 communities (because they are outliers/unexplored branches)
subset = []
for transaction in transactions:
    if len(transaction[1]) > 5:
        subset = subset.append(transaction)

# Apply the apriori algorithm to it.
n1set = []      # (subreddit, n)
nkset = []      # ([subreddits], n, k)
for transaction in subset:
    for subreddit in subset[1]:
        in_set = False
        i = 0
        for i in range(len(n1set)):
            if n1set[i][0] == subreddit:
                in_set = True
                break
        if in_set:
            n1set[i][1] += 1
        if not in_set:
            n1set.append((subreddit, 1))

min_support = 0.6
cutoff = round(len(subset) * min_support)
n1set = [n1tuple for n1tuple in n1set if n1tuple[1] >= cutoff]

frontier = []
for subreddit, n in n1set:
    frontier.append([subreddit])

while len(frontier) > 0:
    new_frontier = []
    for set in frontier:
        for n1subreddit, n1 in n1set:
            if n1subreddit in set:
                continue
            new_set = set.copy()
            new_set.append(n1subreddit)

            total = 0
            for user, subreddits in subset:
                contains = True
                for subreddit in new_set:
                    if subreddit not in subreddits:
                        contains = False
                        break
                if contains == True:
                    total += 1
            if total >= cutoff:
                new_frontier.append(new_set)
                nkset.append((new_set, total, len(new_set)))
    frontier = new_frontier.copy()

print("Frequent Item Sets:")
for frequent_set in n1set:
    print(frequent_set)
for frequent_set in nkset:
    print(frequent_set)