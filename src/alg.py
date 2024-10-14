from . import config
import math
from functools import reduce
from mpmath import mp


def norm(vec):
    """ Return the Euclidean norm of a 3d vector.

    vec - a 3d vector expressed as a list of 3 floats.
    """
    return math.sqrt(reduce((lambda x, y: x + y * y), vec, 0.0))


def normalize(vec):
    """Normalize a vector

    vec - python list

    Return normalized vector
    """
    if norm(vec) < 1e-6:
        return [0 for i in xrange(len(vec))]
    return map(lambda x: x / norm(vec), vec)


# def cross_product(v1, v2, v3):
#     v1v2 = (v2.x - v1.x, v2.y - v1.y)
#     v1v3 = (v3.x - v1.x, v3.y - v1.y)
    
#     cross_product = (v1v2[0] * v1v3[1]) - (v1v2[1] * v1v3[0])
    
#     if abs(cross_product) < config.EPSILON:
#         return 0
#     elif cross_product > 0:
#         return 1  # Point is to the left
#     else:
#         return -1  # Point is to the right

def cross_product(p1, p2, p3):
    """
    Determina la orientación de tres puntos usando mpmath para precisión arbitraria.
    """
    # Configurar la precisión (opcional)
    mp.dps = 60  # Ejemplo: 50 dígitos de precisión

    # Convertir las coordenadas a mpmath.mpf para precisión arbitraria
    x1, y1 = mp.mpf(p1.x), mp.mpf(p1.y)
    x2, y2 = mp.mpf(p2.x), mp.mpf(p2.y)
    x3, y3 = mp.mpf(p3.x), mp.mpf(p3.y)

    # Calcular el determinante con precisión arbitraria
    det = (x1 * (y2 - y3)) + (x2 * (y3 - y1)) + (x3 * (y1 - y2))

    if abs(det) < config.EPSILON:
        return 0
    elif det > 0:
        return 1  # Point is to the left
    else:
        return -1  # Point is to the right

def is_point_in_circumcircle(p, a, b, c):
    """
    Verifica si el punto `p` está dentro del circuncírculo formado por los puntos `a`, `b` y `c`.
    """
    # Convertir las coordenadas de los puntos a una matriz
    mat = [
        [a.x - p.x, a.y - p.y, (a.x - p.x)**2 + (a.y - p.y)**2],
        [b.x - p.x, b.y - p.y, (b.x - p.x)**2 + (b.y - p.y)**2],
        [c.x - p.x, c.y - p.y, (c.x - p.x)**2 + (c.y - p.y)**2]
    ]
    
    # Calcular el determinante de la matriz 3x3
    det = (mat[0][0] * (mat[1][1] * mat[2][2] - mat[2][1] * mat[1][2]) -
           mat[0][1] * (mat[1][0] * mat[2][2] - mat[2][0] * mat[1][2]) +
           mat[0][2] * (mat[1][0] * mat[2][1] - mat[2][0] * mat[1][1]))
    
    return det > 0  # Si el determinante es positivo, el punto está dentro del circuncírculo