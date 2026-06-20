#!/usr/bin/env python3
"""Generate diagrams for WeChat articles using the diagrams library.

Usage:
    python3 diagram.py spec.yaml --output diagram.png
    python3 diagram.py --type architecture --title "Title" -o out.png

Input spec (YAML or JSON):
    title: "Architecture Overview"
    direction: LR           # LR | TB | RL | BT
    background: "#FFFFFF"
    clusters:
      - label: "Before"
        color: "#F5F5F5"
        nodes:
          - id: web
            label: "Web Server"
            type: server    # generic | server | db | cache | language | blank
          - id: db
            label: "MySQL"
            type: db
        edges:
          - from: web
            to: db
          - from: web
            to: cache
            label: "reads"
"""

import os
import argparse
import json
import sys
from pathlib import Path

# Ensure Graphviz is on PATH
_GRAPHVIZ_PATHS = [
    r"C:\Program Files\Graphviz\bin",
    "/usr/local/bin",
    "/usr/bin",
    "/opt/homebrew/bin",
]
for _p in _GRAPHVIZ_PATHS:
    if os.path.isdir(_p):
        os.environ["PATH"] = _p + os.pathsep + os.environ.get("PATH", "")
        break

try:
    import yaml
except ImportError:
    yaml = None


NODE_CLASSES = {}


def _lazy_import():
    global NODE_CLASSES
    from diagrams.generic import Generic
    from diagrams.generic.blank import Blank
    from diagrams.onprem.compute import Server
    from diagrams.onprem.database import Postgresql as Database
    from diagrams.onprem.inmemory import Redis as Cache
    from diagrams.onprem.network import Nginx as Network
    from diagrams.programming.language import Python as ProgLang

    NODE_CLASSES.update({
        "generic": Generic,
        "blank": Blank,
        "server": Server,
        "db": Database,
        "database": Database,
        "cache": Cache,
        "network": Network,
        "language": ProgLang,
        "programming": ProgLang,
        # Aliases for clean labels
        "compute": Server,
        "storage": Database,
        "lb": Network,
    })


def render_from_spec(spec: dict, output_path: str):
    _lazy_import()
    from diagrams import Diagram, Cluster, Edge

    title = spec.get("title", "Diagram")
    direction = spec.get("direction", "LR")
    bg = spec.get("background", "#FFFFFF")
    clusters_data = spec.get("clusters", [])
    flat_nodes = spec.get("nodes", [])
    flat_edges = spec.get("edges", [])

    outfile = Path(output_path).with_suffix("")

    with Diagram(
        title,
        show=False,
        filename=str(outfile),
        direction=direction,
        outformat="png",
        graph_attr={
            "bgcolor": bg,
            "fontname": "Microsoft YaHei, SimHei, Arial",
            "fontsize": "14",
            "pad": "0.5",
        },
        node_attr={
            "fontname": "Microsoft YaHei, SimHei, Arial",
            "fontsize": "11",
        },
        edge_attr={
            "fontname": "Microsoft YaHei, SimHei, Arial",
            "fontsize": "10",
        },
        # cleanup=True,
    ):
        if clusters_data:
            _render_clusters(clusters_data)
        elif flat_nodes:
            _render_flat(flat_nodes, flat_edges)

    png_path = f"{outfile}.png"
    print(f"Diagram saved: {png_path}")


def _get_node(type_name: str, label: str):
    cls = NODE_CLASSES.get(type_name, NODE_CLASSES.get("generic"))
    return cls(label)


def _render_clusters(clusters_data):
    from diagrams import Cluster, Edge

    cluster_nodes = {}

    for cluster_spec in clusters_data:
        label = cluster_spec.get("label", "")
        nodes = cluster_spec.get("nodes", [])
        edges = cluster_spec.get("edges", [])
        color = cluster_spec.get("color", "#FAFAFA")

        with Cluster(label, graph_attr={"bgcolor": color, "fontsize": "14"}):
            for n in nodes:
                node = _get_node(n.get("type", "generic"), n.get("label", n["id"]))
                cluster_nodes[n["id"]] = node

            for e in edges:
                src = cluster_nodes.get(e["from"])
                dst = cluster_nodes.get(e["to"])
                if src and dst:
                    el = e.get("label", "")
                    src >> Edge(label=el) >> dst if el else src >> dst

    # Cross-cluster edges
    for cluster_spec in clusters_data:
        for e in cluster_spec.get("edges_between", []):
            src = cluster_nodes.get(e["from"])
            dst = cluster_nodes.get(e["to"])
            if src and dst:
                el = e.get("label", "")
                src >> Edge(label=el) >> dst if el else src >> dst


def _render_flat(nodes, edges):
    from diagrams import Cluster, Edge

    node_map = {}

    for n in nodes:
        node = _get_node(n.get("type", "generic"), n.get("label", n["id"]))
        node_map[n["id"]] = node

    for e in edges:
        src = node_map.get(e["from"])
        dst = node_map.get(e["to"])
        if src and dst:
            src >> dst


def main():
    parser = argparse.ArgumentParser(description="Generate diagrams for WeChat articles")
    parser.add_argument("input", nargs="?", help="YAML/JSON spec file")
    parser.add_argument("--output", "-o", required=True, help="Output PNG path")
    parser.add_argument("--title", help="Diagram title")
    parser.add_argument("--stdin", action="store_true", help="Read spec from stdin")
    args = parser.parse_args()

    spec = None

    if args.stdin or (not args.input and not sys.stdin.isatty()):
        text = sys.stdin.read()
        if text.strip():
            try:
                spec = json.loads(text)
            except json.JSONDecodeError:
                print("Error: invalid JSON from stdin", file=sys.stderr)
                sys.exit(1)
    elif args.input:
        path = Path(args.input)
        text = path.read_text(encoding="utf-8")
        if path.suffix in (".yaml", ".yml") and yaml:
            spec = yaml.safe_load(text)
        else:
            spec = json.loads(text)
    else:
        parser.print_help()
        sys.exit(1)

    if not spec or not isinstance(spec, dict):
        print("Error: empty or invalid spec", file=sys.stderr)
        sys.exit(1)

    if args.title:
        spec["title"] = args.title

    render_from_spec(spec, args.output)


if __name__ == "__main__":
    main()
