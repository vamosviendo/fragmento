"""Conftest for functional (Selenium) tests.

Provides:
    - an autouse fixture that ensures the default Wagtail Locale and page
      tree are present for every functional test;
    - helpers/fixtures shared by the browser-level tests (`author`,
      `login_as`, `make_post`, `set_body`).
"""
import datetime
import uuid

from django.contrib.auth import get_user_model
from django.db import connection, transaction

import pytest

from wagtail.models import Locale, Page, Site

from blog.models import BlogIndexPage, BlogPage


User = get_user_model()

CREDENTIAL = "test-pw"


@pytest.fixture(autouse=True)
def _ensure_locale(transactional_db):
    """Recreate the default Wagtail Locale and rebuild the page tree.

    Wagtail's `Locale.get_default()` looks up a Locale by the language code
    normalized via `get_supported_content_language_variant`, which for
    settings.LANGUAGE_CODE='es-es' resolves to 'es'. We create the Locale
    with the normalized code so the lookup succeeds.
    """
    transaction.commit()
    connection.close()

    if not Locale.objects.exists():
        Locale.objects.create(language_code="es")

    root = Page.objects.filter(depth=1).first()
    if root is None:
        try:
            root = Page.add_root(instance=Page(title="Root", slug="root", depth=1, numchild=0))
            root.save_revision().publish()
        except Exception:
            pass

    if BlogIndexPage.objects.child_of(root).first() is None:
        blog = BlogIndexPage(title="Blog", slug="blog", intro="")
        root.add_child(instance=blog)

    blog = BlogIndexPage.objects.child_of(root).first()
    site = Site.objects.filter(is_default_site=True).first()
    if site is None:
        Site.objects.create(
            hostname="localhost",
            port=80,
            root_page=blog,
            is_default_site=True,
            site_name="escritor",
        )
    elif site.root_page_id != blog.id:
        site.root_page = blog
        site.save()


@pytest.fixture
def author(transactional_db):
    """A staff/superuser that can log into the Django admin."""
    username = f"author-{uuid.uuid4().hex[:6]}"
    user = User.objects.create_user(
        username=username,
        is_staff=True,
        is_superuser=True,
    )
    user.set_password(CREDENTIAL)
    user.save()
    return {"username": username, "credential": CREDENTIAL, "user": user}


@pytest.fixture
def login_as(live_url):
    """Return a callable that logs `author` in through the admin login form."""

    def _login(driver, author):
        driver.get(live_url("/django-admin/login/"))
        driver.find_element("name", "username").send_keys(author["username"])
        driver.find_element("name", "password").send_keys(author["credential"])
        driver.find_element("css selector", "input[type=submit]").click()

    return _login


@pytest.fixture
def make_post(site_tree_live):
    """Publish a BlogPage under the blog index and return it.

    `first_published_at` can be pinned to make list ordering deterministic.
    """
    blog_index = site_tree_live["blog"]

    def _make(
        title=None,
        intro="",
        body="",
        tags=None,
        date=None,
        live=True,
        first_published_at=None,
    ):
        unique = uuid.uuid4().hex[:6]
        title = title or f"Post {unique}"
        post = BlogPage(
            title=title,
            slug=f"post-{unique}",
            date=date or datetime.date(2026, 1, 1),
            intro=intro,
            body=body,
        )
        if first_published_at is not None:
            post.first_published_at = first_published_at
        blog_index.add_child(instance=post)
        if tags:
            post.tags.add(*tags)
        if live:
            post.save_revision().publish()
        return post

    return _make


@pytest.fixture
def fill_body():
    """Return a callable that types into the post body field.

    The body widget is a plain <textarea>, progressively enhanced by a TinyMCE
    CDN script. When TinyMCE has initialised the textarea is hidden, so the
    content must be set through the editor API instead.
    """

    def _fill(driver, text):
        if driver.execute_script("return typeof window.tinymce !== 'undefined';"):
            driver.execute_script(
                "var ed = tinymce.get('id_body') || tinymce.activeEditor;"
                "ed.setContent(arguments[0]);"
                "tinymce.triggerSave();",
                f"<p>{text}</p>",
            )
        else:
            driver.find_element("name", "body").send_keys(text)

    return _fill
