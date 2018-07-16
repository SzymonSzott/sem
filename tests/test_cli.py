import sem
from click.testing import CliRunner


def test_cli():
    runner = CliRunner()
    runner.invoke(sem, '--help')
