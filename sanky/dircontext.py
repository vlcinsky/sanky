from pathlib import Path
import attr
from typing import Optional, Tuple, List


class MissingEnvironmentDir(ValueError):
    pass


class MissingRootDir(ValueError):
    pass


def findup(here: Path, name: str) -> Optional[Tuple[List[str], Path]]:
    """Find the dir where `name` file exists. Start `here`, proceed up"""
    dir_lst = []
    # fake.file allows to use .parents to traverse all dirs incl. here
    for dirname in (here / "fake.file").absolute().parents:
        if (dirname / name).exists():
            return reversed(dir_lst), dirname
        dir_lst.append(dirname.name)
    return [], None


@attr.s(auto_attribs=True)
class EnvironmentContext:
    here: Path
    root_dir: Path = attr.ib(init=False)
    env_dir: Path = attr.ib(init=False)

    def __attrs_post_init__(self):
        dir_lst, self.env_dir = findup(self.here, "main.jsonnet")
        if self.env_dir is None:
            raise MissingEnvironmentDir(
                f"No `main.jsonnet` in current or parent dir of {self.here}"
            )
        dir_lst, self.root_dir = findup(self.env_dir, "jsonnetfile.json")
        if self.root_dir is None:
            raise MissingRootDir(f"No `jsonnetfile.json` in parents of {self.env_dir}")
