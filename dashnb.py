# %% [markdown]
# # LPO Measure - Data Exploration
#
# ## Load data

# %%
import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
from pprint import pprint

SQLITE_PATH = "dev-measurements.db"

# %%
conn = sqlite3.connect(SQLITE_PATH)

df_runs = pd.read_sql_query("SELECT * FROM runs", conn)
df_measurements = pd.read_sql_query("SELECT * FROM measurements", conn)
df_cases = pd.read_sql_query("SELECT * FROM cases", conn)

conn.close()

print("df_runs head:")
display(df_runs.head())
print("\ndf_measurements head:")
display(df_measurements.head())
print("\ndf_cases head:")
display(df_cases.head())

# %% [markdown]
# ## Plots and analysis

# %%
df_merged = pd.merge(df_measurements, df_runs, left_on="run_id", right_on="id")
df_agg = df_merged.groupby("clay_commit_sha")["score"].mean().reset_index()

df_agg

# %%
plt.figure(figsize=(10, 6))
plt.bar(df_agg["clay_commit_sha"], df_agg["score"])
plt.xlabel("Clay Commit SHA")
plt.ylabel("Average Score")
plt.title("Average Score per Clay Commit (Matplotlib)")
plt.xticks(rotation=45, ha="right")
plt.ylim(0, df_agg['score'].max() * 1.1)
plt.tight_layout()
plt.show()

# %% [markdown]
# ## Explore a Single Case

# %%
def get_case_measurements(instruction:str|None=None, case_id: int|None = None):
    assert (instruction is not None) + (case_id is not None) > 0, "Need either instruction or case_id"

    if case_id is None:
        case_id = df_cases[df_cases["instruction"] == instruction]["id"].iloc[0]

    return df_measurements.query("case_id == @case_id").drop("case_id", axis=1)


pprint(df_cases.instruction.unique().tolist())
get_case_measurements(case_id=7)

# %%
