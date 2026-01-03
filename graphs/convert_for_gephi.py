import json
import csv
from pathlib import Path

IN_PATH = "graph_data.json"

with open(IN_PATH, "r", encoding="utf-8") as f:
    data = json.load(f)

# Handle both formats
if isinstance(data, dict) and "nodes" in data and "edges" in data:
    nodes = data["nodes"]
    edges = data["edges"]
elif isinstance(data, list):
    # assume list of records, no edges
    nodes = data
    edges = []
else:
    raise ValueError("Unrecognized graph_data.json format")

with open("nodes.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=["id", "label", "group", "value"])
    w.writeheader()
    for n in nodes:
        w.writerow({
            "id": n.get("id"),
            "label": n.get("label", ""),
            "group": n.get("group", ""),
            "value": n.get("value", 1)
        })

with open("edges.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=["source", "target", "label", "weight", "type"])
    w.writeheader()
    for e in edges:
        w.writerow({
            "source": e.get("from"),
            "target": e.get("to"),
            "label": e.get("label", ""),
            "weight": e.get("weight", 1),
            "type": e.get("type", "")
        })

print("wrote nodes.csv and edges.csv")
