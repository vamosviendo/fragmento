from django import forms

from .models import BlogPage


class BlogPostForm(forms.ModelForm):
    class Meta:
        model = BlogPage
        fields = ["title", "date", "intro", "body", "tags"]
        widgets = {
            "date": forms.DateInput(attrs={"type": "date"}, format="%Y-%m-%d"),
            "intro": forms.TextInput(),
            "body": forms.Textarea(attrs={"rows": 12, "class": "w-full"}),
            "tags": forms.TextInput(attrs={"class": "w-full"}),
        }
        labels = {
            "intro": "Resumen",
            "body": "Texto",
        }
