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

with open("out/jobs.json", "rt") as f:
    jobs = json.loads(f.read())

tis = []
for j in jobs:
    if j["selected_at"] > 0:
        tis.append(j["selected_at"] - j["submitted_at"])

plt.hist(tis, bins=50)
plt.xlabel("TiP [mins]")
plt.ylabel("Count [#]")
plt.show()
