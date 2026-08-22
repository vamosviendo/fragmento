import datetime
import uuid

import pytest
from django.contrib.auth import get_user_model
from django.test import Client
from django.urls import reverse

from blog.models import BlogIndexPage, BlogPage


User = get_user_model()


@pytest.fixture
def blog_index(site_tree):
    return site_tree["blog"]


@pytest.fixture
def user(db):
    return User.objects.create_user(username="alice", password="secret-pass")


@pytest.fixture
def auth_client(user):
    client = Client()
    client.login(username="alice", password="secret-pass")
    return client


@pytest.fixture
def make_post(blog_index):
    def _make(title="Un post", intro="Resumen", body="Cuerpo"):
        unique = uuid.uuid4().hex[:8]
        post = BlogPage(
            title=f"{title} {unique}",
            slug=f"post-{unique}",
            date=datetime.date(2026, 1, 1),
            intro=intro,
            body=body,
        )
        blog_index.add_child(instance=post)
        post.save_revision().publish()
        return post

    return _make


@pytest.mark.django_db
class TestBlogPostCreateView:
    def test_get_redirects_when_anonymous(self, blog_index):
        client = Client()
        response = client.get(reverse("post_new"))
        assert response.status_code == 302
        assert "login" in response["Location"]

    def test_get_renders_form_when_authenticated(self, auth_client):
        response = auth_client.get(reverse("post_new"))
        assert response.status_code == 200
        assert b"<form" in response.content
        assert b"Nuevo post" in response.content

    def test_post_creates_live_post(self, auth_client, blog_index):
        url = reverse("post_new")
        data = {
            "title": "Post creado",
            "date": "2026-08-22",
            "intro": "Intro",
            "body": "Cuerpo",
            "tags": "alpha, beta",
        }
        response = auth_client.post(url, data)
        assert response.status_code == 302

        created = BlogPage.objects.filter(title="Post creado").first()
        assert created is not None
        assert created.live is True
        assert created.get_parent().id == blog_index.id
        assert sorted(t.name for t in created.tags.all()) == ["alpha", "beta"]

    def test_post_without_title_returns_form_with_errors(self, auth_client):
        url = reverse("post_new")
        data = {"title": "", "date": "2026-08-22", "intro": "", "body": ""}
        response = auth_client.post(url, data)
        assert response.status_code == 200
        assert b"form" in response.content

        assert not BlogPage.objects.filter(title="").exists()


@pytest.mark.django_db
class TestBlogPostUpdateView:
    def test_get_redirects_when_anonymous(self, make_post):
        post = make_post()
        client = Client()
        response = client.get(reverse("post_edit", args=[post.pk]))
        assert response.status_code == 302

    def test_get_renders_form_with_post(self, auth_client, make_post):
        post = make_post(title="Original")
        response = auth_client.get(reverse("post_edit", args=[post.pk]))
        assert response.status_code == 200
        assert b"Editar post" in response.content
        assert b"Original" in response.content

    def test_post_updates_fields(self, auth_client, make_post):
        post = make_post(title="Viejo", intro="Resumen viejo")
        url = reverse("post_edit", args=[post.pk])
        data = {
            "title": "Nuevo título",
            "date": post.date.isoformat(),
            "intro": "Resumen nuevo",
            "body": post.body,
            "tags": "",
        }
        response = auth_client.post(url, data)
        assert response.status_code == 302

        post.refresh_from_db()
        assert post.title == "Nuevo título"
        assert post.intro == "Resumen nuevo"
        assert post.live is True


@pytest.mark.django_db
class TestBlogPostDeleteView:
    def test_get_redirects_when_anonymous(self, make_post):
        post = make_post()
        client = Client()
        response = client.get(reverse("post_delete", args=[post.pk]))
        assert response.status_code == 302

    def test_get_shows_confirmation(self, auth_client, make_post):
        post = make_post(title="A borrar")
        response = auth_client.get(reverse("post_delete", args=[post.pk]))
        assert response.status_code == 200
        assert b"Borrar post" in response.content
        assert b"A borrar" in response.content

    def test_post_unpublishes_instead_of_deleting(self, auth_client, make_post):
        post = make_post()
        url = reverse("post_delete", args=[post.pk])

        response = auth_client.post(url)
        assert response.status_code == 302

        post.refresh_from_db()
        assert post.live is False

        assert BlogPage.objects.filter(pk=post.pk).exists()

    def test_get_404_for_missing_post(self, auth_client):
        response = auth_client.get(reverse("post_delete", args=[99999]))
        assert response.status_code == 404


@pytest.mark.django_db
class TestIndexRendersCrudControls:
    def test_anonymous_sees_no_crud_links(self, make_post):
        post = make_post()
        index_url = BlogIndexPage.objects.first().url
        response = Client().get(index_url)
        assert response.status_code == 200
        assert b"Editar" not in response.content
        assert b"Borrar" not in response.content
        assert b"Nuevo post" not in response.content

    def test_authenticated_sees_crud_links_and_form(self, auth_client, make_post):
        post = make_post()
        index_url = BlogIndexPage.objects.first().url
        response = auth_client.get(index_url)
        assert response.status_code == 200
        assert b"Editar" in response.content
        assert b"Borrar" in response.content
        assert b"Nuevo post" in response.content
