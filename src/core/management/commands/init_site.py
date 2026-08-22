"""Management command to bootstrap a default site tree.

Creates (idempotently):
    - Deletes any stale HomePage (legacy) under root.
    - Moves any orphan BlogIndexPage under root.
    - Ensures a BlogIndexPage exists as a direct child of the Wagtail root.
    - Ensures the default Site's root_page points to the BlogIndexPage.
"""
from django.core.management.base import BaseCommand

from wagtail.models import Page, Site

from blog.models import BlogIndexPage


WELCOME_TITLES = {"Welcome to your new Wagtail site!"}


class Command(BaseCommand):
    help = "Crea la BlogIndexPage por defecto bajo root si no existe."

    def handle(self, *args, **options):
        root = Page.objects.filter(depth=1).first()
        if root is None:
            self.stderr.write("No existe una página raíz Wagtail. ¿Migraciones aplicadas?")
            return

        for stale in root.get_children().filter(title__in=WELCOME_TITLES):
            stale.delete()

        from django.contrib.contenttypes.models import ContentType  # noqa: PLC0415

        legacy_ct = ContentType.objects.filter(app_label="core", model="homepage").first()
        if legacy_ct is not None:
            legacy_ids = list(
                Page.objects.filter(content_type=legacy_ct).values_list("id", flat=True)
            )
            for legacy_home in Page.objects.filter(id__in=legacy_ids):
                for child in list(legacy_home.get_children()):
                    child.move(root, pos="last-child")
                legacy_home.delete()
            self.stdout.write(self.style.SUCCESS(f"{len(legacy_ids)} HomePage(s) legacy eliminada(s)."))

        blog = BlogIndexPage.objects.child_of(root).first()
        if blog is None:
            blog = BlogIndexPage(
                title="Blog",
                slug="blog",
                intro="Artículos, notas y demás.",
            )
            root.add_child(instance=blog)
            self.stdout.write(self.style.SUCCESS("BlogIndexPage creada bajo root."))
        else:
            self.stdout.write(self.style.WARNING("BlogIndexPage ya existe; no se modifica."))

        site = Site.objects.filter(is_default_site=True).first()
        if site is None:
            Site.objects.create(
                hostname="localhost",
                port=80,
                root_page=blog,
                is_default_site=True,
                site_name="escritor",
            )
            self.stdout.write(self.style.SUCCESS("Site por defecto creado."))
        elif site.root_page_id != blog.id:
            site.root_page = blog
            site.save()
            self.stdout.write(self.style.SUCCESS("Site.root_page actualizado a BlogIndexPage."))
