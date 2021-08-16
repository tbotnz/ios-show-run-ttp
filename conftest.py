import pytest
from ttp import ttp
from deepdiff import DeepDiff


class DiffException(Exception):
    """Diff exception for error reporting."""

    def __init__(self, deepdiff) -> None:
        self.deepdiff = deepdiff


def pytest_collect_file(parent, path):
    if path.ext == ".yaml" and path.basename.startswith("test"):
        return YamlFile.from_parent(parent, fspath=path)


class YamlFile(pytest.File):
    def collect(self):
        from ruamel.yaml import YAML

        yaml = YAML(typ="safe")
        test_definitions = yaml.load(self.fspath.open())

        if not isinstance(test_definitions, list):
            test_definitions = [test_definitions]

        for i, test in enumerate(test_definitions):
            yield YamlItem.from_parent(
                self,
                name=test.get("test", f"{self.fspath}_{i}"),
                running_config=test["config"],
                template="show_run.ttp",
                result=test["result"],
            )


class YamlItem(pytest.Item):
    def __init__(self, name, parent, running_config, template, result):
        super().__init__(name, parent)
        self.running_config = running_config
        self.template = template
        self.result = result

    def runtest(self):
        parser = ttp(self.running_config, self.template)
        parser.parse()
        result = parser.result()

        compare_data = {data: result[0][0][data] for data in self.result}
        dd = DeepDiff(compare_data, self.result)
        if dd:
            raise DiffException(dd)

    def repr_failure(self, excinfo):
        """Called when self.runtest() raises an exception."""
        if isinstance(excinfo.value, DiffException):
            return f"Diff found: {excinfo.value.deepdiff.pretty()}"
        return excinfo.value

    def reportinfo(self):
        return self.fspath, 0, f"usecase: {self.name}"
