import json
import sys
from operator import itemgetter
from pathlib import Path
from typing import Optional

import jsonlines
from invoke import task

from .dircontext import EnvironmentContext


@task
def save(c):
    """Save node ids for current docker context into environment context.json"""
    try:
        ec = EnvironmentContext(Path("."))
    except ValueError as exc:
        print(exc)
        sys.exit(1)

    cmd = "docker node ls --format '{{json .}}' "
    res = c.run(cmd, hide=True, warn=True)
    if res.exited != 0:
        print("WARNING: Current Docker Host is not in Swarm mode!!!")
        return
    nodes = list(jsonlines.Reader(res.stdout.splitlines()))
    nodes = {node["ID"]: node for node in nodes}
    context_json_fname = "context.json"
    with (ec.env_dir / context_json_fname).open("w", encoding="utf-8") as f:
        json.dump(nodes, f)
    print(f"{context_json_fname} updated.")


def show_contexts(c):
    cmd = "docker context ls --format '{{json .}}' "
    res = c.run(cmd, hide=True)
    contexts = list(jsonlines.Reader(res.stdout.splitlines()))
    # docker context ls reports empty StackOrchestrator for remotes
    contexts.sort(key=itemgetter("Current"), reverse=True)
    print("Existing docker contexts (first one is currently used):")
    print(f"{'NAME':15}: {'ENDPOINT':40} DESCRIPTION")
    for itm in contexts:
        print(f"{itm['Name']:15}: {itm['DockerEndpoint']:40} {itm['Description']}")


def show_nodes(c) -> dict:
    cmd = "docker node ls --format '{{json .}}' "
    res = c.run(cmd, hide=True, warn=True)
    if res.exited != 0:
        print("WARNING: Current Docker Host is not in Swarm mode!!!")
        return None
    nodes = list(jsonlines.Reader(res.stdout.splitlines()))
    nodes.sort(key=itemgetter("Self"), reverse=True)
    print("Existing Swarm nodes (first one is currently used):")
    print(f"{'ID':25}: {'HOSTNAME':20} {'AVAILABILITY':15} {'MANAGER STATUS':15}")
    for itm in nodes:
        print(
            f"{itm['ID']:25}: {itm['Hostname']:20} {itm['Availability']:15} {itm['ManagerStatus']}"
        )
    return nodes[0]


def show_context_json(c, current_node: Optional[dict]):
    print("Swarm nodes saved for current environment in context.json:")
    try:
        ec = EnvironmentContext(Path("."))
    except ValueError as exc:
        print(exc)
        print("ERROR: Unable to find current environment.")
        return
    json_path = ec.env_dir / "context.json"
    print(f"Environment dir: {ec.env_dir}")
    if not json_path.exists():
        print("No `context.json`")
        return

    with open(json_path, "r", encoding="utf-8") as f:
        nodes_dict = json.load(f)
    print(f"{'ID':25}: {'HOSTNAME':20} {'AVAILABILITY':15} {'MANAGER STATUS':15}")
    for itm in nodes_dict.values():
        print(
            f"{itm['ID']:25}: {itm['Hostname']:20} {itm['Availability']:15} {itm['ManagerStatus']}"
        )
    print("")
    # check, if current_node is within allowed ones
    current_node_id = current_node["ID"]
    if current_node_id in nodes_dict:
        print(f"OK: Swarm node {current_node_id} is present in context.json")
    else:
        print(f"WARNING: Swarm node {current_node_id} is NOT present in context.json")
        print("Hint: Use `sk context.save` if current Swarm nodes shall be used with current environment.")


@task
def show(c):
    """Compare currently saved environment context with current docker one"""
    show_contexts(c)
    print("")
    current_node = show_nodes(c)
    print("")
    show_context_json(c, current_node)
