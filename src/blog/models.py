import datetime

from django.db import models
from django.shortcuts import get_object_or_404
from django.template.defaultfilters import truncatechars
from django.utils.html import strip_tags

from modelcluster.contrib.taggit import ClusterTaggableManager
from modelcluster.fields import ParentalKey

from taggit.models import Tag, TaggedItemBase

from wagtail.admin.panels import FieldPanel, MultiFieldPanel
from wagtail.fields import RichTextField
from wagtail.images import get_image_model_string
from wagtail.models import Page
from wagtail.search import index


class BlogIndexPage(Page):
    intro = models.TextField(blank=True)

    template = "blog/blog_index_page.html"

    parent_page_types = ["wagtailcore.Page"]
    subpage_types = ["blog.BlogPage"]

    content_panels = Page.content_panels + [
        "intro",
    ]

    def get_context(self, request, *args, **kwargs):
        from blog.forms import BlogPostForm

        context = super().get_context(request, *args, **kwargs)

        tag = request.GET.get("tag")
        month = request.GET.get("month")

        posts = BlogPage.objects.live().public().order_by("-first_published_at")

        if tag:
            tag_obj = get_object_or_404(Tag, slug=tag)
            posts = posts.filter(tags__slug=tag)
            context["current_tag"] = tag_obj

        if month:
            try:
                year_str, month_str = month.split("-")
                year, month_num = int(year_str), int(month_str)
            except (TypeError, ValueError):
                year, month_num = None, None
            if year and month_num:
                posts = posts.filter(date__year=year, date__month=month_num)
                context["current_month"] = {"year": year, "month": month_num}

        page = request.GET.get("page", 1)
        try:
            page = int(page)
        except (TypeError, ValueError):
            page = 1

        paginator_per_page = 10
        context["paginator"], context["page_obj"] = _paginate(posts, page, paginator_per_page)
        context["posts"] = context["page_obj"].object_list
        context["all_tags"] = (
            Tag.objects.filter(blog_blogpagetag_items__isnull=False)
            .distinct()
            .order_by("name")
        )
        context["archive"] = (
            BlogPage.objects.live().public()
            .dates("date", "month", order="DESC")
        )
        context["form"] = BlogPostForm()

        return context


class BlogPageTag(TaggedItemBase):
    content_object = ParentalKey("BlogPage", related_name="tagged_items", on_delete=models.CASCADE)


class BlogPage(Page):
    date = models.DateField(default=datetime.date.today)
    intro = models.CharField(max_length=250, blank=True)
    body = RichTextField(blank=True)
    tags = ClusterTaggableManager(through=BlogPageTag, blank=True)
    cover_image = models.ForeignKey(
        get_image_model_string(),
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )

    template = "blog/blog_page.html"

    parent_page_types = ["blog.BlogIndexPage"]
    subpage_types = []

    search_fields = Page.search_fields + [
        index.SearchField("intro"),
        index.SearchField("body"),
        index.FilterField("date"),
    ]

    content_panels = Page.content_panels + [
        MultiFieldPanel(
            [
                "date",
                FieldPanel("cover_image"),
            ],
            heading="Información de la entrada",
        ),
        MultiFieldPanel(
            [
                "intro",
                "body",
                "tags",
            ],
            heading="Contenido",
        ),
    ]

    @property
    def tag_list(self):
        return self.tags.all()

    @property
    def excerpt(self):
        if self.intro:
            return self.intro
        plain = strip_tags(self.body)
        return truncatechars(plain, 240)

    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)
        siblings = (
            BlogPage.objects.live()
            .public()
            .order_by("-date", "-id")
        )
        try:
            siblings.values_list("id", flat=True).get(pk=self.pk)
        except BlogPage.DoesNotExist:
            context["prev_post"] = None
            context["next_post"] = None
            return context

        context["prev_post"] = siblings.filter(date__gt=self.date).first()
        context["next_post"] = siblings.filter(date__lt=self.date).first()
        return context


def _paginate(queryset, page, per_page):
    from django.core.paginator import Paginator

    paginator = Paginator(queryset, per_page)
    try:
        page_obj = paginator.page(page)
    except Exception:
        page_obj = paginator.page(1)
    return paginator, page_obj
