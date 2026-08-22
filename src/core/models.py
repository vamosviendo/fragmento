from django.db import models

from wagtail.models import Page


class HomePage(Page):
    intro = models.TextField(blank=True)

    template = "core/home_page.html"

    content_panels = Page.content_panels + [
        "intro",
    ]

    max_count = 1

    def get_context(self, request):
        context = super().get_context(request)
        from blog.models import BlogPage

        context["latest_posts"] = (
            BlogPage.objects.live()
            .public()
            .order_by("-first_published_at")[:5]
        )
        return context
