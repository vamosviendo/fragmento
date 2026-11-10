## Introducción

Como el alfarero que hace la taza en la cual luego va a tomar café, como el herrero
que forja su propio martillo, escribo la herramienta que usaré para escribir.

Voy a tener que vivir muchos años si quiero completar algo de la cantidad de cosas
inútiles que tengo en marcha.

En fin.

## Estructura general

La página principal actual (blog_index_page.html) es en realidad una página de notas.
La llamaremos página de Fragmentos. Y a los posts los llamaremos fragmentos.

Paralelamente a la página de notas, debe haber una página de Texto Principal, que funcione
con sus propias reglas, similares pero no iguales a las de la página de Fragmentos.
(Esta afirmación todavía está en duda. No sabemos todavía si queremos un texto
principal o simplemente un ordenamiento y selección de fragmentos.)

Tanto la página de Fragmentos como la página de Texto principal deben ser privadas.

Por fuera de todo esto, debe haber una página (o más) de visitantes, un front-end que 
muestre, de las otras dos páginas, lo que el autor quiere mostrar, de la manera
en que lo quiere mostrar.

Una página de Fragmentos, una página (opcional) de texto principal y una página
(también opcional) de visitantes constituyen un Proyecto. Puede haber más de un 
Proyecto. En una instancia posterior, podría haber más de un usuario, cada uno
con varios Proyectos.

## Otras funcionalidades a implementar

### Proyectos y Categorías de fragmentos

Ejemplo de categorías de fragmentos: obsoletos, borradores, canónicos, etc.

La diferencia entre proyecto y categoría es semántica. Estructuralmente, son similares: 
campos ForeignKey con un nombre y una descripción en base a los cuales se filtran los fragmentos.
Lo importante es que son filtros separados y con una funcionalidad diferente.

Un proyecto es una obra. Un conjunto de fragmentos que constituye una unidad, 
que tiene una determinada coherencia interna (lo que podríamos llamar "reglas internas")
y se diferencia de otros conjuntos de fragmentos. (En una primera versión de este párrafo
hablaba de "porciones de material creativo" en lugar de "conjuntos de fragmentos" pero
me pareció que podía ser un concepto algo ambiguo.)

Una categoría se refiere al lugar y la función que tiene un fragmento dentro del proyecto
del cual forma parte.

Entonces, dos ForeginKeys para el modelo Fragmento (lo que actualmente es el modelo BlogPage):

- proyecto (campos "nombre", "descripción")
- categoría (campos "nombre", "descripción")

En la página principal se selecciona un proyecto. Cada proyecto tiene una página de fragmentos
(representada actualmente en la template blog_index_page.html)

### Filtrado de fragmentos

En la página de fragmentos, los mismos deben poder filtrarse por categoría o por tags,
de manera inclusiva o excluyente. Ejemplos:

- mostrar los fragmentos de una categoría
- ocultar los fragmentos de una categoría
- mostrar los fragmentos que contengan uno o más tags
- ocultar los fragmentos que contengan uno o más tags
- mostrar los fragmentos que contengan uno o más tag excepto los fragmentos que contengan otros tags

### Ordenamiento de fragmentos

Posibilidad de ordenar los posteos según distintos criterios, incluyendo un orden
arbitrario dado por el autor.

### Control de versiones. 

Cuando un Fragmento es modificado, debe guardar sus versiones anteriores. 
Lo mismo el Texto Principal (si existe) del Proyecto.

### Proyectos de lectura libre o protegida

Un proyecto de lectura libre es un proyecto que permite que cualquier usuario
lea sus fragmentos.

Un proyecto de lectura protegida es un proyecto que permite que solo los usuarios
autorizados lean sus fragmentos.

Para esto, dos categorías de usuarios en relación a un proyecto: escritor y lector autorizado.

### Proyectos cerrados / abiertos / moderados

En un proyecto cerrado sólo el autor/administrador puede escribir fragmentos.

En un proyecto abierto, cualquier usuario puede escribir fragmentos.

En un proyecto moderado, los fragmentos son aprobados o rechazados por el autor/administrador.