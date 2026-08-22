# Próximos pasos

## Frontend

- No hay página principal y página de blog. La página de blog es la página de inicio.
- No hay, por el momento, barra de navegación.
- La página se estructura de la siguiente manera:
- Un panel izquierdo angosto y un panel derecho ancho.
- Panel derecho:
  - Arriba, título. Luego del título, una lista de posts con los últimos posteos.
    - De cada post debe mostrarse el título, el inicio del texto y un menú que permita editar o borrar.
  - Debajo de los posts, un formulario para crear un nuevo post (título, texto, fecha y tags).
- Panel izquierdo:
  - categorías
  - tags
  - posts por fecha
- Por el momento, sólo herramientas de Django y Wagtail. Evitar JavaScript en la medida de lo posible.
- Tests Funcionales con Selenium (cargar post, editar post, eliminar post) y unit tests con pytest.
