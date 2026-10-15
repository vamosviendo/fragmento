## Introducción

Como el alfarero que hace la taza en la cual luego va a tomar café, como el herrero
que forja su propio martillo, escribo la herramienta que usaré para escribir.

Voy a tener que vivir muchos años si quiero completar algo de la cantidad de cosas
inútiles que tengo en marcha.

En fin.

## Estructura general

La página principal actual (blog_page.html) es en realidad una página de notas.
La llamaremos página de Fragmentos

Paralelamente a la página de notas, debe haber una página de Texto Principal, que funcione
con sus propias reglas, similares pero no iguales a las de la página de Fragmentos.

Tanto la página de Fragmentos como la página de Texto principal deben ser privadas.

Por fuera de todo esto, debe haber una página (o más) de visitantes, un front-end que 
muestre, de las otras dos páginas, lo que el autor quiere mostrar, de la manera
en que lo quiere mostrar.

Una página de Fragmentos, una página (opcional) de texto principal y una página
(también opcional) de visitantes constituyen un Proyecto. Puede haber más de un 
Proyecto. En una instancia posterior, podría haber más de un usuario, cada uno
con varios Proyectos.

## Otras funcionalidades a implementar

Control de versiones. Cuando un Fragmento es modificado, debería guardar sus
versiones anteriores. Lo mismo el Texto Principal (si existe) del Proyecto.