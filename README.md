![Tests](https://github.com/eugeneyan/python-collab-template/workflows/Tests/badge.svg) [![codecov](https://codecov.io/gh/eugeneyan/python-collab-template/branch/master/graph/badge.svg)](https://codecov.io/gh/eugeneyan/python-collab-template)

# python-collab-template

Repository for [How to set up a Python Repo for Automation and Collaboration](https://eugeneyan.com/writing/setting-up-python-project-for-automation-and-collaboration/).

## Quickstart
```bash
# Clone this repo and change directory
git clone git@github.com:eugeneyan/python-collab-template.git
cd python-collab-template

# Install dependencies and set up the environment
make setup

# Run the suite of tests and checks
make check
```

Make a pull request to this repo to see the checks in action 😎

Here's a [sample pull request](https://github.com/eugeneyan/python-collab-template/pull/1) which initially failed ❌ the checks, and then passed ✅.

## Running our checks

In it, we cover the following aspects of setting up a python project, including:

### Unit Tests

```python
@pytest.fixture
def lowercased_df():
    string_col = ['futrelle, mme. jacques heath (lily may peel)',
                  'backstrom, major. karl alfred (maria mathilda gustafsson)']
    df_dict = {'string': string_col}
    df = pd.DataFrame(df_dict)
    return df

def test_extract_title(lowercased_df):
    result = extract_title(lowercased_df, col='string')
    assert result['title'].tolist() == ['mme', 'ms', 'mr', 'lady', 'major']


def test_extract_title_with_replacement(lowercased_df):
    title_replacement = {'mme': 'mrs', 'ms': 'miss', 'lady': 'rare', 'major': 'rare'}
    result = extract_title(lowercased_df, col='string', replace_dict=title_replacement)
    assert result['title'].tolist() == ['mrs', 'miss', 'mr', 'rare', 'rare']
```

```shell
$ rye run pytest
============================= test session starts ==============================
platform darwin -- Python 3.8.2, pytest-5.4.3, py-1.8.2, pluggy-0.13.1
rootdir: /Users/eugene/projects/python-collaboration-template/tests/data_prep
collected 2 items

test_categorical.py::test_extract_title PASSED                           [ 50%]
test_categorical.py::test_extract_title_with_replacement PASSED          [100%]

============================== 2 passed in 0.30s ===============================
```

### Code Coverage
```
$ rye run pytest --cov=src
============================================================================================================= test session starts ==============================================================================================================
platform darwin -- Python 3.12.2, pytest-8.1.1, pluggy-1.4.0
rootdir: /Users/alex.furrier/git_repositories/python-collab-template
configfile: pyproject.toml
plugins: cov-5.0.0
collected 8 items

tests/data_prep/test_categorical.py ...                                                                                                                                                                                                  [ 37%]
tests/data_prep/test_continuous.py .....                                                                                                                                                                                                 [100%]

---------- coverage: platform darwin, python 3.12.2-final-0 ----------
Name                           Stmts   Miss  Cover
--------------------------------------------------
src/__init__.py                    0      0   100%
src/data_prep/__init__.py          0      0   100%
src/data_prep/categorical.py      12      0   100%
src/data_prep/continuous.py       11      0   100%
--------------------------------------------------
TOTAL                             23      0   100%


======================================= 8 passed in 0.75s ========================================================
```

### Linting
```
$ rye lint src/data_prep/categorical -v
```

### Type Checking
```
$ rye run mypy src
src/data_prep/categorical.py:34: error: Incompatible default for argument "replace_dict" (default has type "None", argument has type "dict[Any, Any]")  [assignment]
src/data_prep/categorical.py:34: note: PEP 484 prohibits implicit Optional. Accordingly, mypy has changed its default to no_implicit_optional=True
src/data_prep/categorical.py:34: note: Use https://github.com/hauntsaninja/no_implicit_optional to automatically upgrade your codebase
Found 1 error in 1 file (checked 4 source files)
```

### Wrapping it in a Makefile
```
clean-pyc:
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +
	find . -name '__pycache__' -exec rm -fr {} +

clean-test:
	rm -f .coverage
	rm -f .coverage.*

clean: clean-pyc clean-test

test: clean
	. .venv/bin/activate && py.test tests --cov=src --cov-report=term-missing --cov-fail-under 95
```

### GitHub Actions with each `git push`
```
# .github/workflows/tests.yml
name: Tests
on: push
jobs:
  tests:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v2
    - uses: actions/setup-python@v1
      with:
        python-version: 3.8
        architecture: x64
    - run: make setup
    - run: make check
    - run: bash <(curl -s https://codecov.io/bash)
```
## Docker Dev Env + Image

Docker is often used for environment management and deployment of production code.

This repo is setup to package things in a Docker image for this purpose.

Through the use of [Docker Compose](https://docs.docker.com/compose/) a dev environment can also be stood up and torn down quickly. Docker compose allows for better environment setup through connected services (e.g. databases, etc) for closer replication of a production environment.

The docker compose file `docker/docker-compose.yml` builds an image from `docker/Dockerfile` and runs a bash shell.

Environment variables can be added in the relevant section of the `docker-compose.yml` if they are provided in a `.env` file within the `docker` directory. By default the `.env` file is excluded from the repo since it may contain secrets. Instead the file `docker/template.env` is provided which should provide non secret environment variables and the variable name for required secrets.

### Dev Env

To create a dev environment run:

```bash
make dev-env
```

This should create a running docker container with everything required for development in this repo.

All other Make commands should still work as before.

All changes made to relevant files inside the container will be reflected outside the container as they are bound in the `volumes` section of the `docker-compose.yml` file. Any newly added directories or files will need to be added to the `docker/Dockerfile` with a `COPY` command and bound as a volume in the docker compose file.

### Production Image

Once development is finished and the project is ready to be deployed it can be built and tagged as a Docker image with:

```bash
make build-image
```

The image name and tag are set in the Makefile variables `IMAGE_NAME` and `IMAGE_TAG`.

### Pushing to a container registry

If the name of the image is a container registry, the image can be pushed to the registry with:

```bash
make push-image
```

## Misc
### 👉 View the [article](https://eugeneyan.com/writing/setting-up-python-project-for-automation-and-collaboration/) for the walkthrough.

### Todo
- [ ] Update requirements.txt to use `poetry`
