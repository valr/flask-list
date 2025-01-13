# use default or current directory for temporary directories/files
set tempdir := "."

# list the recipes
default:
  @just --justfile {{justfile()}} --list --list-heading '' --unsorted

# initialise the python environment
init-pyenv:
  #!/usr/bin/env bash
  set -euo pipefail
  [ -d .pyenv ] && { echo "error: the python environment .pyenv already exists"; false; }

  mkdir .pyenv

  export PYENV_ROOT="$PWD/.pyenv"
  export PATH="$PYENV_ROOT/bin:$PATH"
  eval "$(pyenv init - bash)"

  pyenv install 3.12.7

# initialise the virtual environment
init-venv:
  #!/usr/bin/env bash
  set -euo pipefail
  [ ! -d .pyenv ] && { echo "error: the python environment .pyenv doesn't exist"; false; }
  [ -d .venv ] && { echo "error: the virtual environment .venv already exists"; false; }

  export PYENV_ROOT="$PWD/.pyenv"
  export PATH="$PYENV_ROOT/bin:$PATH"
  eval "$(pyenv init - bash)"
  pyenv shell 3.12.7

  python -m venv .venv
  source .venv/bin/activate

  pip install --upgrade pip setuptools wheel
  pip install --upgrade pip-tools

# install the requirements for a production environment
install-requirements-production:
  #!/usr/bin/env bash
  set -euo pipefail
  [ ! -d .pyenv ] && { echo "error: the python environment .pyenv doesn't exist"; false; }
  [ ! -d .venv ] && { echo "error: the virtual environment .venv doesn't exist"; false; }

  export PYENV_ROOT="$PWD/.pyenv"
  export PATH="$PYENV_ROOT/bin:$PATH"
  eval "$(pyenv init - bash)"
  pyenv shell 3.12.7

  source .venv/bin/activate

  pip-sync requirements.txt

# install the requirements for a development environment
install-requirements-development:
  #!/usr/bin/env bash
  set -euo pipefail
  [ ! -d .pyenv ] && { echo "error: the python environment .pyenv doesn't exist"; false; }
  [ ! -d .venv ] && { echo "error: the virtual environment .venv doesn't exist"; false; }

  export PYENV_ROOT="$PWD/.pyenv"
  export PATH="$PYENV_ROOT/bin:$PATH"
  eval "$(pyenv init - bash)"
  pyenv shell 3.12.7

  source .venv/bin/activate

  pip-sync requirements.txt dev-requirements.txt

# compile the requirements for production and development environments
compile-requirements:
  #!/usr/bin/env bash
  set -euo pipefail
  [ ! -d .pyenv ] && { echo "error: the python environment .pyenv doesn't exist"; false; }
  [ ! -d .venv ] && { echo "error: the virtual environment .venv doesn't exist"; false; }

  export PYENV_ROOT="$PWD/.pyenv"
  export PATH="$PYENV_ROOT/bin:$PATH"
  eval "$(pyenv init - bash)"
  pyenv shell 3.12.7

  source .venv/bin/activate

  pip-compile --quiet requirements.in
  pip-compile --quiet dev-requirements.in

# upgrade the requirements for production and development environments
upgrade-requirements:
  #!/usr/bin/env bash
  set -euo pipefail
  [ ! -d .pyenv ] && { echo "error: the python environment .pyenv doesn't exist"; false; }
  [ ! -d .venv ] && { echo "error: the virtual environment .venv doesn't exist"; false; }

  export PYENV_ROOT="$PWD/.pyenv"
  export PATH="$PYENV_ROOT/bin:$PATH"
  eval "$(pyenv init - bash)"
  pyenv shell 3.12.7

  source .venv/bin/activate

  pip-compile --quiet --upgrade requirements.in
  pip-compile --quiet --upgrade dev-requirements.in

# initialise the database
init-db:
  #!/usr/bin/env bash
  set -euo pipefail
  [ ! -d .pyenv ] && { echo "error: the python environment .pyenv doesn't exist"; false; }
  [ ! -d .venv ] && { echo "error: the virtual environment .venv doesn't exist"; false; }

  [ -e database/flask-list.db ] && { echo "error: the database file already exists"; false; }
  [ -d migrations ] && { echo "error: the migrations directory already exists"; false; }

  export PYENV_ROOT="$PWD/.pyenv"
  export PATH="$PYENV_ROOT/bin:$PATH"
  eval "$(pyenv init - bash)"
  pyenv shell 3.12.7

  source .venv/bin/activate

  flask db init
  sed -i -e '/^import sqlalchemy as sa/a import flask_list' migrations/script.py.mako
  flask db migrate -m 'init db'
  flask db upgrade
  echo '.schema' | sqlite3 database/flask-list.db >| database/flask-list.sql
  # chown -R flask-list:root database
  # chmod 700 database
  # chmod 600 database/flask-list.db

# clean the inactive users from the database
clean-inactive-users:
  #!/usr/bin/env bash
  set -euo pipefail
  [ ! -d .pyenv ] && { echo "error: the python environment .pyenv doesn't exist"; false; }
  [ ! -d .venv ] && { echo "error: the virtual environment .venv doesn't exist"; false; }

  export PYENV_ROOT="$PWD/.pyenv"
  export PATH="$PYENV_ROOT/bin:$PATH"
  eval "$(pyenv init - bash)"
  pyenv shell 3.12.7

  source .venv/bin/activate

  flask auth cleaning

# run the flask application in the development server
run-application:
  #!/usr/bin/env bash
  set -euo pipefail
  [ ! -d .pyenv ] && { echo "error: the python environment .pyenv doesn't exist"; false; }
  [ ! -d .venv ] && { echo "error: the virtual environment .venv doesn't exist"; false; }

  export PYENV_ROOT="$PWD/.pyenv"
  export PATH="$PYENV_ROOT/bin:$PATH"
  eval "$(pyenv init - bash)"
  pyenv shell 3.12.7

  source .venv/bin/activate

  flask --debug run

# run a local memcached server
run-memcached-server:
  memcached -p 11211 -m 64 -c 1024 -l 127.0.0.1,::1 -o modern,drop_privileges

# run a local mail server
run-mail-server:
  python -m smtpd -n -c DebuggingServer localhost:8025
