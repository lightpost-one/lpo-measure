# %% [markdown]
# # LPO Measure - Data Exploration
#
# ## Load data

# %%
import sqlite3
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pprint import pprint

SQLITE_PATH = "prod-measurements.db"

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
# ## Run results

# %%
df_merged_runs = pd.merge(df_measurements, df_runs, left_on="run_id", right_on="id")

df_agg_runs = df_merged_runs.groupby("clay_commit_sha").agg(
    avg_score=("score", "mean"),
    total_runtime=("clay_runtime_seconds", "sum"),
    # min to get first timestamp
    timestamp=("timestamp", "min"),
    # first to get commit message
    clay_commit_message=("clay_commit_message", "first")
).reset_index()

df_agg_runs = df_agg_runs.sort_values(by="timestamp")

fig = go.Figure()

fig.add_trace(
    go.Bar(
        x=df_agg_runs["clay_commit_sha"],
        y=df_agg_runs["avg_score"],
        name="Average Score",
        customdata=df_agg_runs,
        hovertemplate="<b>Commit:</b> %{x}<br><b>Avg Score:</b> %{y:.2f}<br><b>Message:</b> %{customdata[4]}<extra></extra>"
    )
)

fig.add_trace(
    go.Bar(
        x=df_agg_runs["clay_commit_sha"],
        y=df_agg_runs["total_runtime"],
        name="Total Runtime",
        customdata=df_agg_runs,
        hovertemplate="<b>Commit:</b> %{x}<br><b>Total Runtime:</b> %{y:.2f}s<br><b>Message:</b> %{customdata[4]}<extra></extra>",
        visible=False
    )
)

fig.update_layout(
    updatemenus=[
        dict(
            active=0,
            buttons=list([
                dict(label="Average Score",
                     method="update",
                     args=[{"visible": [True, False]},
                           {"title": "Average Score per Commit"}]),
                dict(label="Total Runtime",
                     method="update",
                     args=[{"visible": [False, True]},
                           {"title": "Total Runtime per Commit"}]),
            ]),
            direction="down",
            pad={"r": 10, "t": 10},
            showactive=True,
            x=0.1,
            xanchor="left",
            y=1.1,
            yanchor="top"
        )
    ],
    title_text="Average Score per Commit",
    xaxis_title="Clay Commit SHA",
    height=600
)

fig.show()


# %% [markdown]
# ## Case results

# %%
df_merged_cases = pd.merge(df_measurements, df_runs, left_on="run_id", right_on="id")
df_merged_cases = pd.merge(df_merged_cases, df_cases, left_on="case_id", right_on="id")
df_merged_cases = df_merged_cases.sort_values(by="timestamp")

score_hover_template = "<b>Run ID:</b> %{customdata[3]}<br><b>Score:</b> %{y}<br><b>Commit SHA:</b> %{customdata[1]}<br><b>Commit message:</b> %{customdata[2]}<br><b>Reason:</b> %{customdata[0]}<extra></extra>"
runtime_hover_template = "<b>Run ID:</b> %{customdata[3]}<br><b>Runtime:</b> %{y}s<br><b>Commit SHA:</b> %{customdata[1]}<br><b>Commit message:</b> %{customdata[2]}<br><b>Reason:</b> %{customdata[0]}<extra></extra>"

instructions = df_merged_cases["instruction"].unique()

fig = go.Figure()

for instruction in instructions:
    df_case = df_merged_cases[df_merged_cases["instruction"] == instruction].copy()
    df_case["reason"] = df_case["reason"].str.wrap(80).str.replace('\n', '<br>')
    custom_data_columns = df_case[["reason", "clay_commit_sha", "clay_commit_message", "run_id"]]
    fig.add_trace(
        go.Bar(
            x=df_case["run_id"],
            y=df_case["score"],
            name="Score",
            customdata=custom_data_columns,
            hovertemplate=score_hover_template,
            visible=(instruction == instructions[0])
        )
    )
    fig.add_trace(
        go.Bar(
            x=df_case["run_id"],
            y=df_case["clay_runtime_seconds"],
            name="Runtime",
            customdata=custom_data_columns,
            hovertemplate=runtime_hover_template,
            visible=(instruction == instructions[0])
        )
    )


buttons = []
for instruction in instructions:
    df_case_for_instruction = df_merged_cases[df_merged_cases["instruction"] == instruction]
    tickvals = df_case_for_instruction["run_id"].tolist()
    ticktext = (df_case_for_instruction["clay_commit_message"].str.slice(0, 47) + '...').tolist()

    visibility = [s == instruction for s in instructions for _ in range(2)]
    buttons.append(
        dict(
            label=instruction,
            method="update",
            args=[
                {"visible": visibility},
                {
                    "title": f"Results for case: '{instruction}'",
                    "xaxis.tickvals": tickvals,
                    "xaxis.ticktext": ticktext,
                }
            ]
        )
    )

# Set initial layout for the first instruction
first_instruction = instructions[0]
df_case_initial = df_merged_cases[df_merged_cases["instruction"] == first_instruction]
initial_tickvals = df_case_initial["run_id"].tolist()
initial_ticktext = (df_case_initial["clay_commit_message"].str.slice(0, 47) + '...').tolist()

fig.update_layout(
    updatemenus=[
        dict(
            active=0,
            buttons=buttons,
            direction="down",
            pad={"r": 10, "t": 10},
            showactive=True,
            x=0.1,
            xanchor="left",
            y=1.1,
            yanchor="top"
        )
    ],
    title_text=f"Results for case: '{first_instruction}'",
    xaxis_title="Commit Message",
    xaxis_tickangle=-45,
    xaxis=dict(
        tickmode='array',
        tickvals=initial_tickvals,
        ticktext=initial_ticktext
    ),
    height=600
)

fig.show()

# %%
