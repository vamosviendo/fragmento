"""Project-wide pytest fixtures.

Provides a clean page tree (Root + BlogIndexPage) plus functional-test
helpers (selenium_driver, live_url, auth_client).
"""
import os
import shutil

import pytest

from django.conf import settings
from django.contrib.auth import get_user_model
from django.test import Client

from wagtail.models import Locale, Page, Site

from blog.models import BlogIndexPage

from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service


User = get_user_model()


WELCOME_TITLES = {"Welcome to your new Wagtail site!"}


def _build_site_tree():
    root = Page.objects.filter(depth=1).first()
    if root is None:
        try:
            root = Page.add_root(instance=Page(title="Root", slug="root", depth=1, numchild=0))
            root.save_revision().publish()
        except Exception:
            pass

    for stale in root.get_children().filter(title__in=WELCOME_TITLES):
        stale.delete()

    blog = BlogIndexPage.objects.child_of(root).first()
    if blog is None:
        blog = BlogIndexPage(title="Blog", slug="blog", intro="")
        root.add_child(instance=blog)

    site = Site.objects.filter(is_default_site=True).first()
    if site is None:
        site = Site.objects.create(
            hostname="localhost",
            port=80,
            root_page=blog,
            is_default_site=True,
            site_name="escritor",
        )
    elif site.root_page_id != blog.id:
        site.root_page = blog
        site.save()

    return {"root": root, "blog": blog, "site": site}


def _purge_tree():
    """Delete the entire Wagtail page tree so it can be rebuilt cleanly."""
    Page.objects.filter(depth__gt=1).delete()
    Page.objects.filter(depth=1).delete()


@pytest.fixture
def site_tree(db):
    """Build a Root + BlogIndexPage + Site tree under `db` (transactional).

    Requires Wagtail's default Locale to exist. Normally it does (post_migrate
    runs the first time), but if migrations are skipped we create it here.
    """
    if not Locale.objects.exists():
        Locale.objects.create(language_code="es")
    return _build_site_tree()


@pytest.fixture
def site_tree_live(transactional_db):
    """Same as `site_tree` but uses `transactional_db` so commits are visible
    to other connections (e.g. the live_server thread used in Selenium tests).

    The functional tests/functional/conftest.py already rebuilds the tree
    via an autouse fixture; here we just return it.
    """
    root = Page.objects.filter(depth=1).first()
    blog = BlogIndexPage.objects.child_of(root).first()
    site = Site.objects.filter(is_default_site=True).first()
    return {"root": root, "blog": blog, "site": site}


@pytest.fixture
def user(db):
    return User.objects.create_user(username="alice", password="secret-pass")


@pytest.fixture
def auth_client(user):
    client = Client()
    client.login(username="alice", password="secret-pass")
    return client


@pytest.fixture(scope="session")
def geckodriver_path():
    path = os.environ.get("GECKODRIVER") or shutil.which("geckodriver")
    if not path:
        pytest.skip("geckodriver no encontrado en PATH ni en $GECKODRIVER")
    if not os.path.isabs(path):
        path = os.path.abspath(path)
    return path


@pytest.fixture
def selenium_driver(geckodriver_path):
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    service = Service(executable_path=geckodriver_path)
    driver = webdriver.Firefox(service=service, options=options)
    driver.implicitly_wait(5)
    try:
        yield driver
    finally:
        driver.quit()


@pytest.fixture
def live_url(live_server):
    def _build(path="/"):
        return f"{live_server.url}{path}"
    return _build
