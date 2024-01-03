import json
from matplotlib import pyplot as plt

plt.rcParams.update(
    {
        "font.size": 20,
        "font.family": "sans-serif",
        "axes.spines.right": False,
        "axes.spines.top": False,
        "figure.autolayout": True,
    }
)

with open("out/worst_case_jobs.json", "rt") as f:
    jobs = json.loads(f.read())

worst_tis = []
for j in jobs:
    if j["selected_at"] > 0:
        worst_tis.append(j["selected_at"] - j["submitted_at"])

with open("out/best_case_jobs.json", "rt") as f:
    jobs = json.loads(f.read())

best_tis = []
for j in jobs:
    if j["selected_at"] > 0:
        best_tis.append(j["selected_at"] - j["submitted_at"])

print(f"Worst: {sum(worst_tis)}. Best {sum(best_tis)}")

plt.hist(worst_tis, bins=100)
plt.hist(best_tis, bins=100)
plt.xlabel("TiP [mins]")
plt.ylabel("Count [#]")
plt.show()
