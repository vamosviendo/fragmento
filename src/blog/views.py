from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse, reverse_lazy
from django.utils.decorators import method_decorator
from django.views.generic import CreateView, DeleteView, UpdateView

from .forms import BlogPostForm
from .models import BlogIndexPage, BlogPage


def _get_blog_index():
    return (
        BlogIndexPage.objects.filter(depth__gt=1)
        .order_by("path")
        .first()
    )


@method_decorator(login_required, name="dispatch")
class BlogPostCreateView(CreateView):
    model = BlogPage
    form_class = BlogPostForm
    template_name = "blog/post_form.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["form_mode"] = "create"
        return context

    def form_valid(self, form):
        blog_index = _get_blog_index()
        if blog_index is None:
            form.add_error(None, "No existe BlogIndexPage; ejecuta init_site.")
            return self.form_invalid(form)

        post = form.save(commit=False)
        post.live = True
        blog_index.add_child(instance=post)
        form.save_m2m()
        post.save_revision().publish()
        return redirect(self.get_success_url())

    def get_success_url(self):
        return reverse("wagtail_serve", args=[""])


@method_decorator(login_required, name="dispatch")
class BlogPostUpdateView(UpdateView):
    model = BlogPage
    form_class = BlogPostForm
    template_name = "blog/post_form.html"
    context_object_name = "post"
    pk_url_kwarg = "pk"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["form_mode"] = "edit"
        return context

    def form_valid(self, form):
        post = form.save(commit=False)
        post.save_revision().publish()
        form.save_m2m()
        return redirect(self.get_success_url())

    def get_success_url(self):
        return reverse("wagtail_serve", args=[""])


@method_decorator(login_required, name="dispatch")
class BlogPostDeleteView(DeleteView):
    model = BlogPage
    template_name = "blog/post_confirm_delete.html"
    context_object_name = "post"
    pk_url_kwarg = "pk"
    success_url = reverse_lazy("wagtail_serve", args=[""])

    def get_object(self, queryset=None):
        return get_object_or_404(BlogPage, pk=self.kwargs[self.pk_url_kwarg])

    def form_valid(self, form):
        post = self.get_object()
        if post.live:
            post.unpublish()
        return redirect(self.get_success_url())
