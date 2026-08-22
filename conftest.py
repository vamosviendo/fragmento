"""Project-level pytest fixtures.

Provide a clean page tree (Root + HomePage + BlogIndexPage) for tests that
depend on Wagtail's page hierarchy. Runs without DB migrations (pytest-django
--no-migrations), so the Wagtail root page has to be created here.
"""
import pytest

from wagtail.coreutils import get_supported_content_language_variant
from wagtail.models import Page, Site

from blog.models import BlogIndexPage
from core.models import HomePage


WELCOME_TITLES = {"Welcome to your new Wagtail site!"}


@pytest.fixture
def site_tree(db):
    """Ensure the default site points to a HomePage with a BlogIndexPage child."""
    root = Page.objects.filter(depth=1).first()
    if root is None:
        root = Page(
            title="Root",
            slug="root",
            path="0001",
            depth=1,
            path_length=4,
            numchild=0,
        )
        root.save()
        from wagtail.models import i18n as wagtail_i18n
        try:
            root.save_revision().publish()
        except Exception:
            pass

    for stale in root.get_children().filter(title__in=WELCOME_TITLES):
        stale.delete()

    home = HomePage.objects.child_of(root).first()
    if home is None:
        home = HomePage(title="Inicio", slug="home", intro="Bienvenido al escritor.")
        root.add_child(instance=home)

    site = Site.objects.filter(is_default_site=True).first()
    if site is None:
        site = Site.objects.create(
            hostname="localhost",
            port=80,
            root_page=home,
            is_default_site=True,
            site_name="escritor",
        )
    elif site.root_page_id != home.id:
        site.root_page = home
        site.save()

    if BlogIndexPage.objects.child_of(home).first() is None:
        blog = BlogIndexPage(title="Blog", slug="blog", intro="")
        home.add_child(instance=blog)

    return {"root": root, "home": home, "site": site}
