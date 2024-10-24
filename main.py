from src.HalfEdgeMesh import HalfedgeMesh
from src.vertex import Vertex
from src.HalfEdge import Halfedge
from src.facet import Facet
import argparse
import random
import sys
import pygame
import time
import math

# Argumentos por consola
parser = argparse.ArgumentParser(description="Generar una malla de Delaunay con valores personalizados.")
parser.add_argument('--size', type=int, default=100000, help='Tamaño del contenedor (default: 100000)')
parser.add_argument('--points', type=int, default=50, help='Número de puntos a insertar (default: 50)')
parser.add_argument('--rectangular', action='store_true', help='Indica si la malla debe ser rectangular')

args = parser.parse_args()

# Asignar los valores recibidos o usar los predeterminados
SIZE = args.size
POINTS = args.points
rectangular = args.rectangular

# Crear el objeto HalfedgeMesh
mesh = HalfedgeMesh()
random.seed(time.time())
start  = time.time()

# Agregar vertices
mesh.vertices = [
    Vertex(SIZE*2, SIZE*2, 0, 0),
    Vertex(-SIZE*2, SIZE*2, 1, 2),
    Vertex(-SIZE*2, -SIZE*2, 2, 3),
    Vertex(SIZE*2, -SIZE*2, 3, 4)
]

# Agregar caras
halfedge_0 = Halfedge(None, None, None, 0, None, 0)
halfedge_1 = Halfedge(None, None, None, 1, None, 1)
halfedge_2 = Halfedge(None, None, None, 1, None, 2)
halfedge_3 = Halfedge(None, None, None, 2, None, 3)
halfedge_4 = Halfedge(None, None, None, 3, None, 4)
halfedge_5 = Halfedge(None, None, None, 3, None, 5)

halfedge_0.next = 1
halfedge_1.next = 4
halfedge_4.next = 0
halfedge_2.next = 3
halfedge_3.next = 5
halfedge_5.next = 2

halfedge_0.facet = 0
halfedge_1.facet = 0
halfedge_4.facet = 0
halfedge_2.facet = 1
halfedge_3.facet = 1
halfedge_5.facet = 1

halfedge_0.prev = 4
halfedge_1.prev = 0
halfedge_4.prev = 1
halfedge_2.prev = 5
halfedge_3.prev = 2
halfedge_5.prev = 3

halfedge_1.opposite = 5
halfedge_5.opposite = 1

mesh.halfedges = [halfedge_0, halfedge_1, halfedge_2, halfedge_3, halfedge_4, halfedge_5]
facet = Facet(0, 1, 3, 0, 0)
facet2 = Facet(1, 2, 3, 1, 3)
mesh.facets = [facet, facet2]



print("Adding vertices...")
if rectangular:
    # Si la bandera 'rectangular' está activada, generar una cuadrícula
    grid_size = int(math.sqrt(POINTS))  # Número de columnas y filas
    x_step = 2 * (SIZE*0.9) / grid_size  # Espaciado horizontal
    y_step = 2 * (SIZE*0.9) / grid_size  # Espaciado vertical
    start_x = -(SIZE*0.9)
    start_y = -(SIZE*0.9)

    for i in range(grid_size):
        for j in range(grid_size):
            x = start_x + i * x_step
            y = start_y + j * y_step
            new_vertex = Vertex(x, y, 0)
            # print("punto (", x, ", ", y, ")",i, ", ", j)
            mesh.add_vertex(new_vertex)
    print("Adding restrictions:", time.time()-start)
    mesh.add_restriction(Vertex(start_x + x_step*(grid_size/2)*0.72 , y_step*1.5), Vertex(start_x + x_step*(grid_size/2)*0.75, y_step*0.5))
    mesh.add_restriction(Vertex(start_x + x_step*(grid_size/2)*0.72 , y_step*2.5), Vertex(start_x + x_step*(grid_size/2)*0.75, y_step*1.5))
    mesh.add_restriction(Vertex(start_x + x_step*(grid_size/2)*0.72 , y_step*3.5), Vertex(start_x + x_step*(grid_size/2)*0.75, y_step*2.5))
else:
# Añadir puntos aleatorios a la malla
    for i in range(POINTS):
        x = random.uniform(-SIZE+10, SIZE-10)
        y = random.uniform(-SIZE+10, SIZE-10)
        new_vertex = Vertex(x, y, 0)
        
        # Intentar agregar el vértice
        try:
            mesh.add_vertex(new_vertex)
        except ValueError as e:
            print(f"Couldn't add vertex: {e}")
    print("Adding restrictions:", time.time()-start)
    mesh.add_restriction(Vertex(-SIZE/2, 5.0), Vertex(SIZE/2, 5.0))
    mesh.add_restriction(Vertex(-SIZE/2, 10.0), Vertex(SIZE/2, 10.0))
    mesh.add_restriction(Vertex(-SIZE/2, 15.0), Vertex(SIZE/2, 15.0))


end  = time.time()
mesh.remove_border_vertex(0)
mesh.remove_border_vertex(1)
mesh.remove_border_vertex(2)
mesh.remove_border_vertex(3)

print("Construction time:", end-start, " seconds")
print("Generating Delaunay Mesh...")

# Parámetros iniciales para movimiento y zoom
offset_x, offset_y = 0, 0  # Desplazamiento para mover la vista
zoom_factor = 1  # Factor de zoom
is_dragging = False  # Controlar si el ratón está arrastrando
mouse_last_pos = (0, 0)  # Posición anterior del ratón

def transform_coordinates(x, y, offset_x, offset_y, zoom_factor, screen_width, screen_height):
    # Aplicar desplazamiento y escalado (zoom)
    new_x = int((x * zoom_factor) + offset_x + screen_width / 2)
    new_y = int((y * zoom_factor) + offset_y + screen_height / 2)
    return new_x, new_y

# Inicializar pygame
pygame.init()
screen_width, screen_height = 1024, 768
show_vertexes = False
show_deleted_edges = False
screen = pygame.display.set_mode([screen_width, screen_height])
pygame.display.set_caption("Delaunay Mesh with Pan and Zoom (Mouse)")

# Función para dibujar la malla
def draw_mesh():
    screen.fill((0, 0, 0))  # Limpiar la pantalla

    # Dibujar los vértices
    if show_vertexes:
        for v in mesh.vertices:
            transformed_x, transformed_y = transform_coordinates(v.x, v.y, offset_x, offset_y, zoom_factor, screen_width, screen_height)
            pygame.draw.circle(screen, (255, 255, 255), (transformed_x, transformed_y), 3)

    # Dibujar los halfedges (líneas)
    for he in mesh.halfedges:
        start_vertex = mesh.vertices[he.vertex]
        end_vertex = mesh.vertices[mesh.halfedges[he.next].vertex]
        transformed_start = transform_coordinates(start_vertex.x, start_vertex.y, offset_x, offset_y, zoom_factor, screen_width, screen_height)
        transformed_end = transform_coordinates(end_vertex.x, end_vertex.y, offset_x, offset_y, zoom_factor, screen_width, screen_height)
        if not he.deleted:
            if he.is_restricted:
                pygame.draw.line(screen, (255, 0, 0), transformed_start, transformed_end)
            else:  
                pygame.draw.line(screen, (0, 255, 0), transformed_start, transformed_end)
        elif show_deleted_edges:
            pygame.draw.line(screen, (255, 255, 255), transformed_start, transformed_end)
    pygame.display.update()

# Bucle principal para mover y hacer zoom con el ratón
running = True
while running:
    draw_mesh()     # Dibujar la malla con el desplazamiento y el zoom actuales
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_a:
                show_vertexes = not show_vertexes
            elif event.key == pygame.K_s:
                show_deleted_edges = not show_deleted_edges

        # Movimiento (Pan) con el botón izquierdo del ratón
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Botón izquierdo del ratón
                is_dragging = True
                mouse_last_pos = pygame.mouse.get_pos()  # Registrar la posición inicial del ratón
        
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:  # Botón izquierdo del ratón
                is_dragging = False  # Dejar de arrastrar
        
        elif event.type == pygame.MOUSEMOTION:
            if is_dragging:  # Solo mover la vista si se está arrastrando
                mouse_current_pos = pygame.mouse.get_pos()
                dx = mouse_current_pos[0] - mouse_last_pos[0]
                dy = mouse_current_pos[1] - mouse_last_pos[1]
                offset_x += dx  # Actualizar el desplazamiento horizontal
                offset_y += dy  # Actualizar el desplazamiento vertical
                mouse_last_pos = mouse_current_pos  # Actualizar la posición del ratón
        
        # Zoom con la rueda del ratón
        elif event.type == pygame.MOUSEWHEEL:
            if event.y > 0:  # Scroll hacia arriba (zoom in)
                zoom_factor *= 1.1
            elif event.y < 0:  # Scroll hacia abajo (zoom out)
                zoom_factor /= 1.1

pygame.quit()
sys.exit()