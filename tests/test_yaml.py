import yaml
import pytest


def test_yaml_load():
    content = """
- A
- B
- C
"""
    document = yaml.load(content, yaml.Loader)
    assert document == ["A", "B", "C"]


def test_yaml_load_file():
    content = """
- D
- E
- F
"""
    with open("test_yaml_load_file.yaml", "w") as file:
        file.write(content)
    with open("test_yaml_load_file.yaml", "r") as file:
        document = yaml.load(file, yaml.Loader)
        assert document == ["D", "E", "F"]
