import hashlib
from collections import defaultdict
from pathlib import Path

import structlog
import yaml


logger = structlog.get_logger()


def fix_cfg_file(cfg_file: Path):
    log = logger.bind(cfg_file=str(cfg_file))
    log.info("loading")
    cfg = yaml.safe_load(cfg_file.open())
    changes = defaultdict(dict)

    for topic in ["secrets", "configs"]:
        log = log.bind(topic=topic)
        for topic_key, topic_cfg in cfg.get(topic, {}).items():
            log = log.bind(key=topic_key)
            if topic_cfg.get("external", False):
                log.info("skipping external item")
                continue
            try:
                fname = topic_cfg["file"]
            except KeyError:
                log.warning("cfg[topic][topic_key]['file'] is empty")
                continue
            full_fname = cfg_file.parent / fname
            if not full_fname.exists():
                log.warning("resource file does not exists.", resource_file=str(full_fname))
                continue
            md5 = hashlib.md5(full_fname.read_bytes()).hexdigest()
            # name limited to 64 chars, md5 has 32, truncate topic_key if necessary
            new_name = f"{topic_key:.31}.{md5}"[:64]
            changes[topic][topic_key] = new_name
    if changes:
        cfg_file.rename(cfg_file.with_suffix(".yml.bak"))
        for topic in ["secrets", "configs"]:
            for topic_key, new_name in changes[topic].items():
                cfg[topic][topic_key]["name"] = new_name
                log.info("append suffix", topic=topic, key=topic_key, new_name=new_name)
        yaml.safe_dump(cfg, cfg_file.open("w", encoding="utf-8"))
