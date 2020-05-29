from invoke import task
from pathlib import Path
import sys

from .dircontext import EnvironmentContext


@task
def deploy(c):
    """deploy all stacks (use it for update too)"""
    try:
        ec = EnvironmentContext(Path("."))
    except ValueError as exc:
        print(exc)
        sys.exit(1)
    for dock_comp in (ec.env_dir / "_deploy").rglob("docker-compose.yml"):
        stack_dir = dock_comp.parent
        stack_name = stack_dir.name
        with c.cd(stack_dir):
            cmd = f"docker stack deploy -c docker-compose.yml {stack_name}"
            print(f"cd {stack_dir} && {cmd}")


@task
def rm(c):
    """remove all stacks"""
    try:
        ec = EnvironmentContext(Path("."))
    except ValueError as exc:
        print(exc)
        sys.exit(1)
    for dock_comp in (ec.env_dir / "_deploy").rglob("docker-compose.yml"):
        stack_dir = dock_comp.parent
        stack_name = stack_dir.name
        # no need to be in stack directory for rm
        cmd = f"docker stack rm {stack_name}"
        print(f"{cmd}")
