"""Functional tests: a reader browses published posts from the index list.

Each test performs a user action (click a post, a tag, a month, a pagination
link) and checks the resulting page.
"""
import datetime
import uuid

import pytest
from django.utils import timezone
from selenium.webdriver.common.by import By


pytestmark = pytest.mark.django_db(transaction=True)


class TestOpenPost:
    def test_reader_opens_post_from_list(self, selenium_driver, live_url, make_post):
        unique = uuid.uuid4().hex[:6]
        title = f"Nota {unique}"
        body = f"Cuerpo completo {unique}"
        post = make_post(title=title, intro=f"Resumen {unique}", body=f"<p>{body}</p>")

        driver = selenium_driver
        driver.get(live_url("/"))

        assert title in driver.page_source
        assert f"Resumen {unique}" in driver.page_source

        driver.find_element(By.LINK_TEXT, title).click()

        assert post.url in driver.current_url
        assert title in driver.page_source
        assert body in driver.page_source


class TestFilterPosts:
    def test_reader_filters_posts_by_tag(self, selenium_driver, live_url, make_post):
        unique = uuid.uuid4().hex[:6]
        python_title = f"Py {unique}"
        django_title = f"Dj {unique}"
        make_post(title=python_title, tags=["python"])
        make_post(title=django_title, tags=["django"])

        driver = selenium_driver
        driver.get(live_url("/"))

        driver.find_element(By.LINK_TEXT, "python").click()

        assert "Filtrando por" in driver.page_source
        assert python_title in driver.page_source
        assert django_title not in driver.page_source

    def test_reader_clears_tag_filter(self, selenium_driver, live_url, make_post):
        unique = uuid.uuid4().hex[:6]
        python_title = f"Py {unique}"
        django_title = f"Dj {unique}"
        make_post(title=python_title, tags=["python"])
        make_post(title=django_title, tags=["django"])

        driver = selenium_driver
        driver.get(live_url("/"))
        driver.find_element(By.LINK_TEXT, "python").click()
        driver.find_element(By.LINK_TEXT, "quitar filtros").click()

        assert python_title in driver.page_source
        assert django_title in driver.page_source

    def test_reader_filters_posts_by_month(self, selenium_driver, live_url, make_post):
        unique = uuid.uuid4().hex[:6]
        june_title = f"Junio {unique}"
        january_title = f"Enero {unique}"
        make_post(title=june_title, date=datetime.date(2026, 6, 15))
        make_post(title=january_title, date=datetime.date(2026, 1, 15))

        driver = selenium_driver
        driver.get(live_url("/"))

        driver.find_element(By.XPATH, "//a[contains(@href, 'month=2026-06')]").click()

        assert june_title in driver.page_source
        assert january_title not in driver.page_source


class TestPagination:
    def test_reader_moves_to_next_page(self, selenium_driver, live_url, make_post):
        base = timezone.now()
        for i in range(11):
            make_post(
                title=f"Pagina {i:02d}",
                first_published_at=base + datetime.timedelta(minutes=i),
            )

        driver = selenium_driver
        driver.get(live_url("/"))

        assert "Página 1 de 2" in driver.page_source
        assert "Pagina 10" in driver.page_source
        assert "Pagina 00" not in driver.page_source

        driver.find_element(By.PARTIAL_LINK_TEXT, "Siguientes").click()

        assert "Página 2 de 2" in driver.page_source
        assert "Pagina 00" in driver.page_source
        assert "Pagina 10" not in driver.page_source
