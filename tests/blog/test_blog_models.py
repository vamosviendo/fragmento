import datetime
import uuid

import pytest
from django.test import RequestFactory
from django.http import Http404

from blog.models import BlogIndexPage, BlogPage


@pytest.fixture
def blog_index(site_tree):
    return BlogIndexPage.objects.child_of(site_tree["home"]).first()


@pytest.fixture
def make_posts(blog_index):
    def _make(count, tags=None, base_date=None):
        posts = []
        base = base_date or datetime.date(2026, 1, 1)
        for i in range(count):
            unique = uuid.uuid4().hex[:8]
            post = BlogPage(
                title=f"Post {unique}",
                slug=f"post-{unique}",
                date=base + datetime.timedelta(days=i),
                intro=f"Intro {unique}",
            )
            blog_index.add_child(instance=post)
            if tags:
                tag_list = [tags] if isinstance(tags, str) else tags
                post.tags.add(*tag_list)
                post.save_revision().publish()
            posts.append(post)
        return posts

    return _make


@pytest.mark.django_db
class TestBlogIndexPageContext:
    def test_contains_posts_key(self, blog_index):
        request = RequestFactory().get("/blog/")
        context = blog_index.get_context(request)

        assert "posts" in context
        assert "page_obj" in context
        assert "paginator" in context
        assert "all_tags" in context

    def test_pagination_defaults_to_first_page(self, blog_index, make_posts):
        make_posts(15)
        request = RequestFactory().get("/blog/")
        context = blog_index.get_context(request)

        assert len(context["posts"]) == 10
        assert context["page_obj"].number == 1
        assert context["paginator"].num_pages == 2

    def test_pagination_respects_page_param(self, blog_index, make_posts):
        make_posts(15)
        request = RequestFactory().get("/blog/?page=2")
        context = blog_index.get_context(request)

        assert context["page_obj"].number == 2
        assert len(context["posts"]) == 5

    def test_invalid_page_falls_back_to_first(self, blog_index, make_posts):
        make_posts(3)
        request = RequestFactory().get("/blog/?page=not-a-number")
        context = blog_index.get_context(request)

        assert context["page_obj"].number == 1

    def test_filters_by_tag(self, blog_index, make_posts):
        make_posts(3, tags=["python"])
        make_posts(2, tags=["django"])
        request = RequestFactory().get("/blog/?tag=python")
        context = blog_index.get_context(request)

        assert len(context["posts"]) == 3
        assert context["current_tag"].slug == "python"

    def test_unknown_tag_raises_404(self, blog_index, make_posts):
        make_posts(3, tags=["python"])
        request = RequestFactory().get("/blog/?tag=nonexistent")
        with pytest.raises(Http404):
            blog_index.get_context(request)

    def test_collects_all_tags(self, blog_index, make_posts):
        make_posts(1, tags=["python"])
        make_posts(1, tags=["django", "python"])
        request = RequestFactory().get("/blog/")
        context = blog_index.get_context(request)

        tag_names = sorted(t.name for t in context["all_tags"])
        assert tag_names == ["django", "python"]


@pytest.mark.django_db
class TestBlogPageContext:
    def test_prev_and_next_are_distinct(self, blog_index, make_posts):
        posts = make_posts(3)
        middle = posts[1]
        request = RequestFactory().get("/")
        context = middle.get_context(request)

        assert context["prev_post"] is not None
        assert context["next_post"] is not None
        assert context["prev_post"].id != middle.id
        assert context["next_post"].id != middle.id
        assert context["prev_post"].id != context["next_post"].id

    def test_newest_post_has_no_prev(self, blog_index, make_posts):
        """El post más reciente no tiene un post anterior (más nuevo) en el blog."""
        posts = make_posts(2)
        newest = max(posts, key=lambda p: p.date)
        request = RequestFactory().get("/")
        context = newest.get_context(request)

        assert context["prev_post"] is None
        assert context["next_post"] is not None

    def test_oldest_post_has_no_next(self, blog_index, make_posts):
        """El post más antiguo no tiene un post siguiente (más antiguo) en el blog."""
        posts = make_posts(2)
        oldest = min(posts, key=lambda p: p.date)
        request = RequestFactory().get("/")
        context = oldest.get_context(request)

        assert context["prev_post"] is not None
        assert context["next_post"] is None

    def test_tag_list_property(self, blog_index):
        unique = uuid.uuid4().hex[:8]
        post = BlogPage(title=f"Tagged {unique}", slug=f"tagged-{unique}")
        blog_index.add_child(instance=post)
        post.tags.add("alpha", "beta")

        names = sorted(t.name for t in post.tag_list)
        assert names == ["alpha", "beta"]
