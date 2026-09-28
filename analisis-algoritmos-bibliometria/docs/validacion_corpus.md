Articulo 3 "englishwritten" a "english" y "written"
Articulo 4 "problemsolving" a "problem" y "solving"
Articulo 5 "de"+"fi"+"nitions" combinado a definitions
Articulo 6 "aiedrelated" a "aied" y "related"
Articulo 7 "dataintensive" a "data" y "intensive", "humancentred" a "human" y "centred", "laaied" a "la" y "aied", "enduser" a "end" y "user"
Articulo 8 "metaanalyses" a "meta" y "analyses"
Articulo 9 "aiedspecialized" a "aied" y "specialized", "metatrends" a "meta" y "trends", "largescaled" a "large" y "scaled"
Articulo 10 "simulationbased" a "simulation" y "based", "fiftynine" a "fifty" y "nine", "yearofstudy" a "year" "of" y "study"
Articulo 11 "forwardthinking" a "forward" y "thinking", "selfregulated" a "self" y "regulated"
Articulo 12 "domesticonly" a "domestic" y "only"
Articulo 13 "designmethodologyapproach" a "design" "methodology" y "approach", "originalityvalue" a "originality" y "value"
Articulo 15 "metaanalyses" a "meta" y "analyses", "sourcesauthors" a "sources" y "authors", "aigenerated" a "ai" y "generated"
Articulo 16 "madeup" a "made" y "up"
Articulo 17 "aidriven" a "ai" y "driven"
Articulo 18 "everevolving" a "ever" y "evolving", "gaienhanced" a "gai" y "enhanced", "longterm" a "long" y "term"
Articulo 19 "intelligencebased" a "intelligence" y "based"

## Actualización (Sprint 3)

Las correcciones anteriores se aplicaban editando a mano la lista `abstract_preprocesado`, pero no el campo `abstract_preprocesado_texto`, y se perdían al volver a ejecutar `preprocessing.py`. Además quedaban casos sin corregir (`humanai` en el artículo 4, `computerbased` en el 5, `aidriven` en el 17).

La causa era que `word_tokenize` conserva `problem-solving` como un solo token y luego la limpieza de puntuación borraba el guion. Se corrigió en `preprocessing.py` con la función `_resolver_compuestos()`: separa las palabras unidas por guion o barra (o las une si el resultado es una palabra válida del diccionario, como `inter-disciplinary`). El caso del artículo 5 (`de ﬁ- nitions`) quedó en la tabla `CORRECCIONES_PUNTUALES`. Con esto, todas las correcciones de esta lista se reproducen automáticamente al regenerar el corpus.
