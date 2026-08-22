"""Conftest for functional (Selenium) tests.

Adds an autouse fixture that ensures the default Wagtail Locale and page
tree are present for every functional test.
"""
from django.db import connection, transaction

import pytest

from wagtail.models import Locale, Page, Site

from blog.models import BlogIndexPage


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





