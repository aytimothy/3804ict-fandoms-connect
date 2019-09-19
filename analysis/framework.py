from common import *
from mlxtend.frequent_patterns import apriori, association_rules
from mlxtend.preprocessing import TransactionEncoder
import pandas as pd

df = get_local_data()                                   # Get Data
df.reset_index(inplace=True)                            # Prepare it for use with df.groupby()
gb = df.groupby("User")                                 # Group everything by the user
s = gb["Subreddit"].unique()                            # Return a table where the Subreddits are grouped by user
df = pd.DataFrame(s)                                    # Turn it into a DataFrame
df = df[df["Subreddit"].apply(lambda x: len(x) > 5)]    # Remove unnecessary leaf users (fluffs the data)
# df = df[df["Subreddit"].apply(lambda x: "Minecraft" in x)]    # Filter by Minecraft players...
# df = df[df["Subreddit"].apply(lambda x: "pokemon" in x)]      # Filter by Pokémon fans...
# df = df[df["Subreddit"].apply(lambda x: "digimon" in x)]      # Filter by Digimon fans...

ary = df["Subreddit"].to_list()                         # Prepare it for use by the transaction encoder (make it a list)
te = TransactionEncoder()                               # Initialize the transaction encoder class
te_ary = te.fit(ary).transform(ary)                     # Convrert the data into a binary transaction table
print(len(te_ary))
df = pd.DataFrame(te_ary, columns=te.columns_)          # Convert it back into a dataframe.
apr = apriori(df, min_support=0.3, use_colnames=True)   # Apply the apriori algorithm to the data.

with pd.option_context('display.max_rows', None, 'display.max_columns', None):
    print(apr)

#varname: type = val                                    # Type hinting (example)
