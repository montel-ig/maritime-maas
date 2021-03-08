# Maritime MaaS

Django application that acts as an integration layer that mediates the connection between ticket sales platforms and MaaS providers.

## Architecture

See [Architecture](doc/ARCHITECTURE.md)

## Development with [Docker](https://docs.docker.com/)

Prerequisites:

-   Docker
-   Docker Compose

1.  Create a `docker-compose.env.yaml` file in the project folder:
    -   Use `docker-compose.env.yaml.example` as a base, it does not need any changes for getting the project running.
    -   Set entrypoint/startup variables according to taste.
        -   `DEBUG`, controls debug mode on/off
        -   `APPLY_MIGRATIONS`, applies migrations on startup
        -   `CREATE_ADMIN_USER`, creates an admin user with credentials `kuva-admin`:(password, see below)
            (kuva-admin@hel.ninja)
        -   `ADMIN_USER_PASSWORD`, the admin user's password. If this is not given, a random password is generated
            and written into stdout when an admin user is created automatically.

2.  Run `docker-compose up`
    -   The project is now running at [localhost:8081](http://localhost:8081)

**Optional steps**

1.  Run migrations:
    -   Taken care by the example env
    -   `docker exec maritime-maas-backend python manage.py migrate`

2.  Create superuser:
    -   Taken care by the example env
    -   `docker exec -it maritime-maas-backend python manage.py add_admin_user`

## Development without Docker

Prerequisites:

-   PostgreSQL 11
-   Python 3.8

### Installing Python requirements

-   Run `pip install -r requirements.txt`
-   Run `pip install -r requirements-dev.txt` (development requirements)

### Database

To setup a database compatible with default database settings:

Create user and database

    sudo -u postgres createuser -P -R -S maritime_maas  # use password `maritime_maas`
    sudo -u postgres createdb -O maritime_maas maritime_maas

Allow user to create test database

    sudo -u postgres psql -c "ALTER USER maritime_maas CREATEDB;"

### Daily running

-   Create `.env` file: `touch .env`
-   Set the `DEBUG` environment variable to `1`.
-   Run `python manage.py migrate`
-   Run `python manage.py add_admin_user`
-   Run `python manage.py runserver 0:8000`

The project is now running at [localhost:8000](http://localhost:8000)

## Keeping Python requirements up to date

1.  Install `pip-tools`:
    -   `pip install pip-tools`

2.  Add new packages to `requirements.in` or `requirements-dev.in`

3.  Update `.txt` file for the changed requirements file:
    -   `pip-compile requirements.in`
    -   `pip-compile requirements-dev.in`

4.  If you want to update dependencies to their newest versions, run:
    -   `pip-compile --upgrade requirements.in`

5.  To install Python requirements run:
    -   `pip-sync requirements.txt`

## Code format

This project uses
[`black`](https://github.com/ambv/black),
[`flake8`](https://gitlab.com/pycqa/flake8) and
[`isort`](https://github.com/timothycrosley/isort)
for code formatting and quality checking. Project follows the basic
black config, without any modifications.

Basic `black` commands:

-   To let `black` do its magic: `black .`
-   To see which files `black` would change: `black --check .`

[`pre-commit`](https://pre-commit.com/) can be used to install and
run all the formatting tools as git hooks automatically before a
commit.

## Running tests

-   Set the `DEBUG` environment variable to `1`.
-   Run `pytest`.
