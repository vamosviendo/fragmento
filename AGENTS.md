# AGENTS.md - Development Guidelines for escritor

This file provides guidance for AI agents working on this codebase.

## Project Overview

- **Type**: Django + Wagtail CMS website (classic blog structure)
- **Python**: 3.x
- **Database**: SQLite (dev), PostgreSQL (prod)
- **Testing**: pytest + pytest-django

---

## Project Layout

```
escritor/                  # Django project package
  settings/
    base.py                # Shared settings
    dev.py                 # Development overrides (DEBUG=True)
    production.py          # PostgreSQL + env-driven settings
    local.py               # Local-only overrides (not in git)
  urls.py
  wsgi.py / asgi.py
core/                      # Site-level app (HomePage + base template)
  models.py                # HomePage (max_count=1)
  templates/core/base.html # Layout principal (header, footer)
  templates/core/home_page.html
  management/commands/init_site.py  # Crea HomePage, BlogIndexPage y Site por defecto
blog/                      # Blog app
  models.py                # BlogIndexPage, BlogPage, BlogPageTag
  migrations/
  templates/blog/
    blog_index_page.html
    blog_page.html
    includes/blog_card.html
    includes/pagination.html
tests/                     # Tests pytest (ubicación canónica)
  core/test_home_page.py
  blog/test_blog_models.py
static/css/site.css        # Estilos globales (complemento a clases Tailwind)
src/                       # Datos generados (sqlite, media, static)
  db.sqlite3
  media/
  static/
manage.py
pytest.ini
conftest.py                # Fixture `site_tree`
requirements.txt
```

---

## Build / Lint / Test Commands

### Django Management

```bash
# Run development server
python manage.py runserver

# Initialise site tree (idempotent: HomePage + BlogIndexPage + default Site)
python manage.py init_site

# Apply migrations
python manage.py migrate

# Create migrations
python manage.py makemigrations

# Collect static files
python manage.py collectstatic --noinput
```

### Running Tests

```bash
# Run all tests
pytest

# Run a single file
pytest tests/blog/test_blog_models.py

# Run a single class
pytest tests/blog/test_blog_models.py::TestBlogIndexPageContext

# Run a single method
pytest tests/blog/test_blog_models.py::TestBlogIndexPageContext::test_filters_by_tag

# Verbose
pytest -v
```

---

## General behavior

- Atenerse al modo Plan a menos que esté seleccionado explícitamente el modo build.
- No aplicar directamente cambios al código, sino presentarlos en pantalla para su revisión. Indicar con un comentario los lugares específicos del código en los que se han hecho cambios.
- Cuando falte información, solicitarla. Comprobar en vez de inferir o suponer. Empiria.

---

## Code Style Guidelines

### General Principles

- **Minuciosidad controlada**: Balance between quality and progress.
- **ATDD**: Write functional tests first, then unit tests.
- **Clean code**: Clear names, comments only when essential.

### Imports

- **Standard library** first, then **third-party**, then **local**.
- Always use absolute imports (no relative imports like `from ..models`).
- Group imports: stdlib, third-party, local.
- Imports at the beginning of the file, not local to function, method or class, unless necessary.

```python
# Correct
from django.db import models
from wagtail.admin.panels import FieldPanel
from core.models import HomePage
```

### Formatting

- **Line length**: Max 120 characters.
- **Indentation**: 4 spaces.
- **Blank lines**: Two between top-level definitions, one between methods.
- **No trailing whitespace**.

### Naming Conventions

- **Classes**: `PascalCase` (e.g., `BlogIndexPage`, `BlogPage`).
- **Functions/methods**: `snake_case` (e.g., `make_posts`).
- **Variables**: `snake_case` (e.g., `blog_index`, `site_tree`).
- **Constants**: `UPPER_SNAKE_CASE`.
- **Templates**: Lowercase with underscores (e.g., `blog_index_page.html`).

### Django/Wagtail Patterns

- **Models**: Define in `models.py` per app, inheriting from `wagtail.models.Page`.
- **Templates**: Store in `<app>/templates/<app>/`.
- **Static files**: Store in `static/<app>/`.
- **Settings**: Modular (`settings/base.py`, `settings/dev.py`, `settings/production.py`).
- **Test files**: `test_*.py` inside `tests/<app>/`.

### Test Organization

Follow this structure in tests:

1. **Functional tests**: Test from user perspective using templates (Selenium). *Not yet implemented.*
2. **Unit tests**: Test models, template tags, views.
3. Tests must be based on pytest.
4. Canonical location for tests is `tests/`.

### Unit tests

- They primarily test functions or methods.
- Tests for a method must cover:
  - What value it must return
  - What side effects it must have
  - In which cases it must raise an exception
- Tests must be organised in classes or files according to the method being tested.

---

## Initialising a Fresh Database

After running `migrate`, the Wagtail tree only contains the root page. To get a working site (HomePage + BlogIndexPage + default Site pointing at HomePage) run:

```bash
python manage.py init_site
```

This is idempotent and safe to re-run.

---

## Key Files

| Path                                              | Description                                |
|---------------------------------------------------|--------------------------------------------|
| `escritor/settings/base.py`                       | Main Django settings                       |
| `escritor/settings/dev.py`                        | Development settings                       |
| `core/models.py`                                  | HomePage model                             |
| `blog/models.py`                                  | BlogIndexPage and BlogPage models          |
| `core/management/commands/init_site.py`           | Bootstrap default site tree                |
| `pytest.ini`                                      | pytest configuration                       |
| `conftest.py`                                     | Project-wide pytest fixtures               |
| `src/db.sqlite3`                                  | SQLite database file                       |
| `src/media`                                       | Uploaded media                             |
| `src/static`                                      | Collected static files                     |
