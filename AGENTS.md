# AGENTS.md - Development Guidelines for escritor

Este archivo complementa el `AGENTS.md` global
(`~/.config/opencode/AGENTS.md`). Aquí vive sólo lo específico del
proyecto. Ante conflicto, este archivo tiene prioridad sobre el global.

## Modo de trabajo
- En este proyecto en particular, a diferencia de establecido en el 
  AGENTS.md global, se operará alternando entre modo plan y modo build.

## Project Overview

- **Type**: Django + Wagtail CMS website (classic blog structure)
- **Propósito**: Aplicación de escritura basada en fragmentos de texto
- **Python**: 3.x
- **Database**: SQLite
- **Testing**: pytest + pytest-django

## Project Layout

```
./
  AGENTS.md
  conftest.py
  pytest.ini
  requirements.txt
  tests/                     # Tests pytest (ubicación canónica)
    core/test_home_page.py
    blog/test_blog_models.py
  src/                       # Código + datos generados
    manage.py
    db.sqlite3
    static/css/site.css
    media/
    blog/                    # Blog app
      models.py              # BlogIndexPage, BlogPage, BlogPageTag
      migrations/
      templates/blog/
        blog_index_page.html
        blog_page.html
        includes/blog_card.html
        includes/pagination.html
    core/                    # Site-level app (HomePage + base template)
      models.py              # HomePage (max_count=1)
      templates/core/base.html
      templates/core/home_page.html
      management/commands/init_site.py  # Crea HomePage, BlogIndexPage y Site por defecto
    escritor/                # Django project package
      settings/
        base.py
        dev.py
        production.py
        local.py
      urls.py
      wsgi.py / asgi.py
```

## Build / Lint / Test Commands

Todos los comandos Django se ejecutan desde `src/`:

```bash
cd src

python manage.py runserver 8014
python manage.py init_site
python manage.py migrate
python manage.py makemigrations
python manage.py collectstatic --noinput
```

Los tests se ejecutan desde la raíz del repo (no requieren `cd`):

```bash
pytest
pytest tests/blog/test_blog_models.py
pytest tests/blog/test_blog_models.py::TestBlogIndexPageContext
pytest tests/blog/test_blog_models.py::TestBlogIndexPageContext::test_filters_by_tag
pytest -v
```

## Django/Wagtail Patterns del proyecto

- **Models**: en `models.py` por app, heredando de `wagtail.models.Page`.
- **Static files**: en `src/static/`.
- **Test files**: `test_*.py` dentro de `tests/<app>/` (hermano de `src/`).

## Initialising a Fresh Database

Después de correr `migrate`, el árbol de Wagtail sólo contiene la root
page. Para tener un sitio funcional (HomePage + BlogIndexPage + Site por
defecto apuntando a HomePage) hay que ejecutar:

```bash
cd src && python manage.py init_site
```

Es idempotente y seguro de re-ejecutar. El sitio por defecto escucha en
`hostname=localhost, port=80`, pero Wagtail resuelve primero por
hostname, así que cualquier puerto (e.g. `runserver 8014`) se sirve en
`http://localhost:8014/`.

## Key Files

| Path | Description |
|---|---|
| `src/escritor/settings/base.py` | Main Django settings |
| `src/escritor/settings/dev.py` | Development settings |
| `src/escritor/urls.py` | Root URLconf (no i18n prefix) |
| `src/core/models.py` | HomePage model |
| `src/blog/models.py` | BlogIndexPage and BlogPage models |
| `src/core/management/commands/init_site.py` | Bootstrap default site tree |
| `pytest.ini` | pytest configuration |
| `conftest.py` | Project-wide pytest fixtures |
| `src/db.sqlite3` | SQLite database file |
| `src/media` | Uploaded media |
| `src/static` | Static source files |

## Consideraciones generales

Al momento de escribir este texto la aplicación se encuentra aún en una
fase embrionaria. Puede consultarse lo que tenga hasta el momento de un
plan de trabajo a futuro en `PLAN.md`. En él se encontrará una
descripción general de la aplicación y su estructura y funciones aún no
implementadas.
