"""Functional tests: an author creates, edits and deletes posts through the UI.

Every test follows the same shape: the user performs an action in the browser
and the resulting page is checked, mirroring how the site is actually used.
"""
import uuid

import pytest
from selenium.webdriver.common.by import By

from blog.models import BlogPage


pytestmark = pytest.mark.django_db(transaction=True)


def _row_for(driver, title):
    """The post list row (`<li data-testid="post">`) whose link shows `title`."""
    return driver.find_element(
        By.XPATH,
        f"//li[@data-testid='post'][.//a[normalize-space()='{title}']]",
    )


class TestAnonymousAccess:
    def test_anonymous_does_not_see_crud_controls(self, selenium_driver, live_url, make_post):
        post = make_post(title=f"Solo lectura {uuid.uuid4().hex[:6]}", intro="Resumen")

        driver = selenium_driver
        driver.get(live_url("/"))

        assert post.title in driver.page_source
        assert not driver.find_elements(By.LINK_TEXT, "Editar")
        assert not driver.find_elements(By.LINK_TEXT, "Borrar")
        assert "Nuevo post" not in driver.page_source

    def test_anonymous_cannot_open_create_form(self, selenium_driver, live_url):
        driver = selenium_driver
        driver.get(live_url("/posts/new/"))

        assert "login" in driver.current_url
        assert not driver.find_elements(By.NAME, "title")


class TestCreatePost:
    def test_author_creates_post_from_index_form(self, selenium_driver, live_url, author, login_as, fill_body):
        driver = selenium_driver
        login_as(driver, author)
        driver.get(live_url("/"))

        unique = uuid.uuid4().hex[:6]
        title = f"Creado {unique}"
        body = f"Cuerpo de prueba {unique}"
        driver.find_element(By.NAME, "title").send_keys(title)
        driver.find_element(By.NAME, "date").send_keys("2026-08-22")
        driver.find_element(By.NAME, "intro").send_keys("Resumen de prueba")
        fill_body(driver, body)
        driver.find_element(By.XPATH, "//button[normalize-space()='Publicar']").click()

        assert title in driver.page_source

        post = BlogPage.objects.get(title=title)
        assert post.live is True
        assert body in post.body


class TestEditPost:
    def test_author_edits_post_from_list(self, selenium_driver, live_url, author, login_as, make_post):
        unique = uuid.uuid4().hex[:6]
        original = f"Original {unique}"
        post = make_post(title=original, intro="Resumen")

        driver = selenium_driver
        login_as(driver, author)
        driver.get(live_url("/"))

        _row_for(driver, original).find_element(By.LINK_TEXT, "Editar").click()

        assert "Editar post" in driver.page_source
        title_input = driver.find_element(By.NAME, "title")
        assert title_input.get_attribute("value") == original

        edited = f"Editado {unique}"
        title_input.clear()
        title_input.send_keys(edited)
        driver.find_element(By.XPATH, "//button[normalize-space()='Guardar']").click()

        assert edited in driver.page_source
        assert original not in driver.page_source

        post.refresh_from_db()
        assert post.title == edited


class TestDeletePost:
    def test_author_deletes_post_from_list(self, selenium_driver, live_url, author, login_as, make_post):
        title = f"A borrar {uuid.uuid4().hex[:6]}"
        post = make_post(title=title, intro="")

        driver = selenium_driver
        login_as(driver, author)
        driver.get(live_url("/"))

        _row_for(driver, title).find_element(By.LINK_TEXT, "Borrar").click()

        assert "Borrar post" in driver.page_source
        assert title in driver.page_source

        driver.find_element(By.XPATH, "//button[normalize-space()='Confirmar borrado']").click()

        assert title not in driver.page_source

        post.refresh_from_db()
        assert post.live is False
        assert BlogPage.objects.filter(pk=post.pk).exists()
