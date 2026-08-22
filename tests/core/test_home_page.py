import pytest
from django.test import RequestFactory

from core.models import HomePage


@pytest.mark.django_db
class TestHomePageContext:
    def test_provides_latest_posts(self, site_tree):
        home = site_tree["home"]
        request = RequestFactory().get("/")
        context = home.get_context(request)

        assert "latest_posts" in context
        assert hasattr(context["latest_posts"], "__iter__")

    def test_home_page_is_subclass_of_page(self):
        from wagtail.models import Page
        assert issubclass(HomePage, Page)
