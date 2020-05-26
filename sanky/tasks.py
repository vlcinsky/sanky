import json
import shutil
import sys
from pathlib import Path

import structlog
from invoke import task

from .fix import fix_cfg_file

DEPLOY_PATH = Path("_deploy")


logger = structlog.get_logger()


def check_main_jsonnet_here():
    main_fname = Path("main.jsonnet")
    if not main_fname.exists():
        print(f"Unable to find file {main_fname}.")
        print(f"Run this command from `environment` subdir with {main_fname}")
        sys.exit(1)


@task
def init(c):
    """Create the directory structure"""
    c.run("tk init")


@task
def clean(c):
    """Clean deployment directory `environment/{envname}/_deploy`"""
    check_main_jsonnet_here()
    shutil.rmtree(DEPLOY_PATH, ignore_errors=True)


@task
def generate(c):
    """Generate docker swarm config files into `environment/{envname}/_deploy`"""
    check_main_jsonnet_here()
    res = c.run("tk eval .", hide=True)
    data = json.loads(res.stdout)
    for stack_name, files_cfg in data.items():
        for fname, content in files_cfg.items():
            path = DEPLOY_PATH / stack_name / fname
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding="utf-8")
            print(path)


@task
def fix(c):
    """Fix secret and config names in docker-compose.yml in _deploy subdir"""
    check_main_jsonnet_here()
    cfg_files = list(Path(".").rglob("**/docker-compose.yml"))
    for cfg_file in cfg_files:
        fix_cfg_file(cfg_file)
