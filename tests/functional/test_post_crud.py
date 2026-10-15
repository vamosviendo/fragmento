"""Selenium functional tests: create / edit / delete a post through the browser."""
import datetime
import uuid

import pytest
from django.contrib.auth import get_user_model

from blog.models import BlogPage


User = get_user_model()


pytestmark = pytest.mark.django_db(transaction=True)


@pytest.fixture
def superuser(site_tree_live):
    """A staff/superuser with valid credentials for login."""
    username = f"selenium-{uuid.uuid4().hex[:6]}"
    user = User.objects.create_user(
        username=username,
        password="secret-pass",
        is_staff=True,
        is_superuser=True,
    )
    return {
        "username": username,
        "password": "secret-pass",
        "user": user,
        "blog_index": site_tree_live["blog"],
    }


def _login(driver, live_url, username, password):
    driver.get(live_url("/django-admin/login/"))
    driver.find_element("name", "username").send_keys(username)
    driver.find_element("name", "password").send_keys(password)
    driver.find_element("css selector", "input[type=submit]").click()


def test_user_can_create_post(selenium_driver, live_url, superuser):
    driver = selenium_driver

    _login(driver, live_url, superuser["username"], superuser["password"])
    driver.get(live_url("/posts/new/"))
    has_tinymce = driver.execute_script("return typeof window.tinymce != 'undefined';")

    driver.find_element("name", "title").send_keys("Post desde Selenium")
    driver.find_element("name", "date").send_keys("2026-08-22")
    driver.find_element("name", "intro").send_keys("Resumen desde UI")
    if has_tinymce:
        driver.execute_script(
            "tinymce.get(tinymce.activeEditor.id).setContent('<p>Cuerpo del post</p>');"
            "tinymce.triggerSave();"
        )
    else:
        driver.find_element("name", "body").send_keys("Cuerpo del post")
    driver.find_element("name", "tags").send_keys("alpha, beta")
    driver.find_element("css selector", "button[type=submit]").click()

    driver.get(live_url("/"))
    body = driver.page_source
    assert "Post desde Selenium" in body
    assert "Resumen desde UI" in body


def test_user_can_edit_post(selenium_driver, live_url, superuser, site_tree_live):
    blog_index = site_tree_live["blog"]
    unique = uuid.uuid4().hex[:6]
    post = BlogPage(
        title=f"Original {unique}",
        slug=f"original-{unique}",
        date=datetime.date(2026, 1, 1),
        intro="Resumen original",
        body="Cuerpo original",
    )
    blog_index.add_child(instance=post)
    post.save_revision().publish()

    driver = selenium_driver

    _login(driver, live_url, superuser["username"], superuser["password"])
    driver.get(live_url("/"))
    assert f"Original {unique}" in driver.page_source

    driver.get(live_url(f"/posts/{post.pk}/edit/"))

    title_input = driver.find_element("name", "title")
    title_input.clear()
    title_input.send_keys(f"Editado {unique}")
    driver.find_element("css selector", "button[type=submit]").click()

    driver.get(live_url("/"))
    body = driver.page_source
    assert f"Editado {unique}" in body
    assert f"Original {unique}" not in body

    post.refresh_from_db()
    assert post.title == f"Editado {unique}"


def test_user_can_delete_post(selenium_driver, live_url, superuser, site_tree_live):
    blog_index = site_tree_live["blog"]
    unique = uuid.uuid4().hex[:6]
    post = BlogPage(
        title=f"A borrar {unique}",
        slug=f"borrar-{unique}",
        date=datetime.date(2026, 1, 1),
        intro="",
        body="Cuerpo",
    )
    blog_index.add_child(instance=post)
    post.save_revision().publish()

    driver = selenium_driver

    _login(driver, live_url, superuser["username"], superuser["password"])
    driver.get(live_url(f"/posts/{post.pk}/delete/"))

    assert "Borrar post" in driver.page_source
    assert f"A borrar {unique}" in driver.page_source

    driver.find_element("css selector", "button[type=submit]").click()

    driver.get(live_url("/"))
    assert f"A borrar {unique}" not in driver.page_source

    post.refresh_from_db()
    assert post.live is False
    assert BlogPage.objects.filter(pk=post.pk).exists()
