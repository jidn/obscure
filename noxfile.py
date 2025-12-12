import subprocess

import nox


def uv_versions_allowed_by_pyproject() -> list[str]:
    """uv known python versions allowed by pyproject.toml."""
    t = nox.project.load_toml("pyproject.toml")
    try:
        requires_python = t["project"]["requires-python"]
    except KeyError:
        return []
    if not requires_python.startswith(">="):
        raise ValueError("requires-python must start with '>='")
    major, minor = map(int, requires_python[2:].split(".")[:2])

    return [
        ".".join(map(str, _))
        for _ in uv_available_versions()
        if _[0] >= major and _[1] >= minor
    ]


# TODO: why does return type not like list[tuple[int, int]]
def uv_available_versions() -> list[tuple[int, int]]:  # type: ignore
    try:
        # Execute the shell command and capture the output
        result = subprocess.run(
            ["uv", "python", "list"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )

        # Check if the command was successful
        if result.returncode != 0:
            print(f"Error executing command: {result.stderr}")
            return []

        # Split the output into lines
        #   cpython-3.13.0-linux-x86_64-gnu  <download available>
        #   cpython-3.12.7-linux-x86_64-gnu  /usr/bin/python3.12
        lines = result.stdout.strip().split("\n")

        # Get unique (major, minor) version from each line
        # fmt: off
        versions = sorted({ # sorted, unique
            tuple(map(int,  # major.minor as tuple[int]
            _.split()[0]     # the first column
            .split("-")[1]   # the version number
            .split(".")[:2]  # the major.minor numbers
            ))
            for _ in lines
        })
        # fmt: on
        return versions  # type: ignore

    except Exception as e:
        print(f"An error occurred: {e}")
        return []


def cmd(command_line: str):
    """Split a command line into space separated arguments.

    Useful when running a nox.Session:
        session.run(*cmd("pytest --cov"))
    """
    return command_line.split()


# @nox.session(python=uv_versions_allowed_by_pyproject())
pyproject_versions = uv_versions_allowed_by_pyproject()


@nox.session(venv_backend="uv|venv", python=pyproject_versions)
def test(session: nox.Session):
    session.install("pytest", "pytest-cov")
    session.install("-e", ".")

    # remove existing coverage
    session.run(*cmd("coverage erase"))
    # remove existing __pycache__
    session.run(*cmd("make clean"), external=True)

    # session.run(*cmd("coverage run -m pytest"))
    session.run(*cmd("pytest --cov"))
    session.run(*cmd("coverage report --fail-under=100 --skip-covered --show-missing"))
