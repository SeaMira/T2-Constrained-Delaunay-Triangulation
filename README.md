# Tarea 2 - Triangulaciones de Delaunay Restringidas

Triangulaciones de Delaunay creadas con el algoritmo incremental con FlipEdge. Se realizó con la estructura de datos Half-Edge.

Se necesita tener instalados la librería de CGAL y todas las dependencias asociadas.

Las siguientes instrucciones se deben llevar a cabo en una terminal que se encuentre en el directorio principal del proyecto.
Para generar una build se utiliza el siguiente comando:

```bash
cmake -S . -B ./build
```

Para compilar se puede utilizar el siguiente comando:

```bash
cmake --build ./build -j 10
```

Para ejecutar se utiliza el siguiente comando:

```bash
build/main.exe --points POINTS --size SIZE --output filename.off --rectangular
```

- --points: puntos en la triangulación.
- --size: mitad del tamañodel lado de la geometría contenedora.
- --output: nombre del archivo de salida de la triangulacion, debe ser en extensión .off
- --rectangular: flag booleana. En caso de estar, la representación será una grid regular. En caso contrario será aleatorio.

## Author

Sebastián Mira Pacheco
