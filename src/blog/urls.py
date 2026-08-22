from django.urls import path

from . import views

urlpatterns = [
    path("new/", views.BlogPostCreateView.as_view(), name="post_new"),
    path("<int:pk>/edit/", views.BlogPostUpdateView.as_view(), name="post_edit"),
    path("<int:pk>/delete/", views.BlogPostDeleteView.as_view(), name="post_delete"),
]
