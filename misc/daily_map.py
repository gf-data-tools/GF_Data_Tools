from pathlib import Path

from gf_utils2.gamedata import GameData

game_data_dir: Path = Path("../../GF_Data_Tools/data/tw/")
gamedata: GameData = GameData(
    [game_data_dir / "stc", game_data_dir / "catchdata"],
    game_data_dir / "asset/table",
)
# %%
import pandas as pd

daily_map_df = pd.DataFrame.from_dict(gamedata["daily_map"], orient="index")
daily_map_df["coordinate"] = daily_map_df["coordinate"].map(
    lambda x: [int(i) for i in x.split(";")]
)
daily_map_df["neighbor"] = daily_map_df["neighbor"].map(
    lambda x: [int(i) for i in x.split("|")]
)
daily_map_spot_df = pd.DataFrame.from_dict(gamedata["daily_map_spot"], orient="index")

# %%
import networkx as nx


def gen_map(map_id=1):
    spot_df = daily_map_spot_df.query("map_id==@map_id").merge(
        daily_map_df, left_on="spot_id", right_on="id"
    )
    daily_map = nx.DiGraph()
    for _, node in spot_df.iterrows():
        idx = node["spot_id"]
        daily_map.add_node(idx, **node)
        for neighbor in node["neighbor"]:
            daily_map.add_edge(idx, neighbor)
    return daily_map


# %%
import pulp as lp


def analyze_map(map_id=1):
    daily_map = gen_map(map_id=map_id)

    edges = {
        (u, v): lp.LpVariable(f"edge_{u}_{v}", lowBound=0, cat=lp.LpInteger)
        for u, v in daily_map.edges()
    }
    nodes = {u: lp.LpVariable(f"node_{u}", cat=lp.LpBinary) for u in daily_map.nodes()}

    results = []
    for n in range(10, 50):
        prob = lp.LpProblem(sense=lp.LpMaximize)
        clear_var = lp.LpVariable(f"clear_map", cat=lp.LpBinary)
        total_score, total_cost = 500 * clear_var, 0
        for u, node in daily_map.nodes.items():
            if node["spot_type"] == 5:
                prob += nodes[u] == 0
            else:
                prob += clear_var <= nodes[u]
            if node["sub_type"] == 1:
                prob += nodes[u] == 1
            d = node["difficulty_group"]
            score = 0 if d == 0 else 30 + 30 * d if d < 6 else 360
            if node["sub_type"] != 1:
                total_score += score * nodes[u]
                if score != 0:
                    total_cost += nodes[u]

        for i, j in daily_map.edges():
            prob += edges[i, j] <= n * nodes[j]
        for v in daily_map.nodes():
            if daily_map.nodes[v]["sub_type"] == 1:
                edges[0, v] = lp.LpVariable(f"edge_0_{v}", lowBound=0, cat=lp.LpInteger)
                prob += edges[0, v] + sum(
                    edges[i, j] for i, j in daily_map.in_edges(v)
                ) == nodes[v] + sum(edges[i, j] for i, j in daily_map.out_edges(v))
            else:
                prob += sum(edges[i, j] for i, j in daily_map.in_edges(v)) == nodes[
                    v
                ] + sum(edges[i, j] for i, j in daily_map.out_edges(v))

        prob += sum(nodes.values()) == n

        prob += total_score
        prob.solve(solver=lp.PULP_CBC_CMD(msg=False))
        results.append(
            (
                total_score.value(),
                total_cost.value(),
                total_score.value() / total_cost.value(),
            )
        )
    # print(n, total_score.value(), total_cost.value(), total_score.value()/total_cost.value(), [edge for edge in edges.values() if edge.value()>0])
    optimal = max(results, key=lambda x: (x[-1], x[-2]))
    total = max(results, key=lambda x: (x[0]))
    print(map_id, optimal, total)
    return (map_id, optimal, total)


# %%
if __name__ == "__main__":
    from multiprocessing.pool import Pool

    pool = Pool(processes=16)
    res = pool.map(analyze_map, range(1, 101))
    print(res)
