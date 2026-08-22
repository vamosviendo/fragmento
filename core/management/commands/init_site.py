"""Management command to bootstrap a default site tree.

Creates (idempotently):
    - A HomePage as a direct child of the Wagtail root, replacing the default
      'Welcome to your new Wagtail site!' page.
    - A BlogIndexPage under the HomePage.
    - Ensures the default Site's root_page points to the HomePage.
"""
from django.core.management.base import BaseCommand

from wagtail.models import Page, Site

from blog.models import BlogIndexPage
from core.models import HomePage


WELCOME_TITLES = {"Welcome to your new Wagtail site!"}


class Command(BaseCommand):
    help = "Crea la HomePage y BlogIndexPage por defecto si no existen."

    def handle(self, *args, **options):
        root = Page.objects.filter(depth=1).first()
        if root is None:
            self.stderr.write("No existe una página raíz Wagtail. ¿Migraciones aplicadas?")
            return

        # 1) Eliminar cualquier página welcome de Wagtail que estorbe.
        deleted = 0
        for stale in root.get_children().filter(title__in=WELCOME_TITLES):
            stale.delete()
            deleted += 1
        if deleted:
            self.stdout.write(self.style.SUCCESS(
                f"{deleted} página(s) welcome por defecto eliminada(s)."
            ))

        # 2) Asegurar una HomePage hija directa de root.
        home = HomePage.objects.child_of(root).first()
        if home is None:
            home = HomePage(title="Inicio", slug="home", intro="Bienvenido al escritor.")
            root.add_child(instance=home)
            self.stdout.write(self.style.SUCCESS("HomePage creada."))
        else:
            self.stdout.write(self.style.WARNING("HomePage ya existe; no se modifica."))

        # 3) Asegurar que existe un Site por defecto apuntando a la HomePage.
        site = Site.objects.filter(is_default_site=True).first()
        if site is None:
            Site.objects.create(
                hostname="localhost",
                port=80,
                root_page=home,
                is_default_site=True,
                site_name="escritor",
            )
            self.stdout.write(self.style.SUCCESS("Site por defecto creado."))
        elif site.root_page_id != home.id:
            site.root_page = home
            site.save()
            self.stdout.write(self.style.SUCCESS("Site.root_page actualizado a HomePage."))

        # 4) BlogIndexPage bajo HomePage.
        existing_blog = BlogIndexPage.objects.child_of(home).first()
        if existing_blog:
            self.stdout.write(self.style.WARNING("BlogIndexPage ya existe; no se modifica."))
            return

        blog = BlogIndexPage(
            title="Blog",
            slug="blog",
            intro="Artículos, notas y demás.",
        )
        home.add_child(instance=blog)
        self.stdout.write(self.style.SUCCESS("BlogIndexPage creada."))
