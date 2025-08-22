# %% [markdown]
# # LPO Measure - Data Exploration
#
# ## Load data

# %%
import sqlite3
import pandas as pd
import plotly.express as px
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
fig = px.bar(
    df_agg,
    x="clay_commit_sha",
    y="score",
    title="Average Score per Clay Commit (Plotly)",
    labels={"clay_commit_sha": "Clay Commit SHA", "score": "Average Score"},
    height=600,
)
fig.show()

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
