"""
Compare TOX "env installed:" lines between builds.
This can help locate why a build failed.
"""
import re
from pathlib import Path
from typing import Dict, Iterable, Iterator, Tuple


def find_installed_iter(text_iter: Iterable[str]) -> Iterator[str]:
    line_pattern = re.compile(r"(\x1b\[\w\w)*(\w+) installed: (?P<installed>.*)(\x1b\[\w\w)*")
    for line in text_iter:
        if m := line_pattern.match(line):
            yield m.group("installed")

def component_iter(text_iter: Iterable[str]) -> Iterator[Tuple[str, str]]:
    for text in text_iter:
        components = text.split(",")
        for item in components:
            if item.startswith("-e"):
                name, _, version = item.partition(' ')
            else:
                name, _, version = item.partition('==')
            yield name, version

def components(path: Path) -> Dict[str, str]:
    with path.open() as source:
        return {
            name: version
            for name, version in component_iter(find_installed_iter(source))
        }

if __name__ == "__main__":
    working = components(Path("working.log"))
    failure = components(Path("failure.log"))
    if set(working.keys()) != set(failure.keys()):
        print(f"Working has {set(working.keys())-set(failure.keys())}")
        print(f"Failure has {set(working.keys())-set(failure.keys())}")
    for name in set(working.keys()) | set(failure.keys()):
        if (w := working.get(name)) != (f:= failure.get(name)):
            print(f"{name}=={w}  # Failed with {f}")
