# Contributing

## Development

Tabbit is written in Python. You will need to install [uv], which is used to
manage the project.

Optionally, you can use [pre-commit] to install pre-commit hooks that run checks
whilst making a commit.

```shell
uv tool install pre-commit
pre-commit install
```

When sending a patch, ensure code passes checks and the test suite.

```shell
uv run --frozen pytest
uv run --frozen mypy src tests
pre-commit run --all-files
```

These checks are run via GitHub Actions and will block merging if any fail.
Running them locally saves time and expedites the review process.

### Testing

If you are adding a new feature, test the feature works as expected. If you are
fixing an issue, add a test that fails on the receiving branch and passes on the
merging branch.

This project targets 100% code coverage; all lines of code should be executed at
least once during a full run of the test suite.

To measure coverage with [coverage.py], run

```shell
uv run --frozen coverage run -m pytest
```

and then review the report with

```shell
uv run --frozen coverage report
```

Then, to erase the collected data

```shell
uv run --frozen coverage erase
```

### Typing

All code must be type-annotated and type-checked with `mypy`. Avoid using
`# type: ignore`, `typing.Any`, or `typing.cast` unless due to a bug with the
type-checker or an unavoidable limitation of Python's type system.

## Project structure

Application code is stored in the `src` directory. The following top-level
overview may be helpful.

- `tabbit.asgi`: manages the ASGI application.
- `tabbit.config`: manages configuration (such as application settings and
  logging).
- `tabbit.database`: manages database operations (such as creating, reading,
  updating, and deleting data), models for representing database objections, and
  session management.
- `tabbit.exceptions`: Tabbit exception types.
- `tabbit.http`: manages the user-facing API.
- `tabbit.schemas`: describes and manages the intermediary data between the API
  and database.

[uv]: https://docs.astral.sh/uv/
[pre-commit]: https://pre-commit.com/
[coverage.py]: https://coverage.readthedocs.io/en/latest/
