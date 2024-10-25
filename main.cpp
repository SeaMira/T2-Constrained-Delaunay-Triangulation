#include <iostream>
#include <random>
#include <stdexcept>
#include <chrono>  // Para cronometrar el tiempo
#include <string>
#include <cmath>
#include "src/Vertex.h"
#include "src/HalfEdge.h"
#include "src/Facet.h"
#include "src/Mesh.h"

// Función para parsear las opciones con flags
void parse_arguments(int argc, char const* argv[], double& SIZE, int& POINTS, bool& rectangular, std::string& filename) {
    for (int i = 1; i < argc; ++i) {
        std::string arg = argv[i];
        if (arg == "--size" && i + 1 < argc) {
            SIZE = std::stod(argv[++i]);
        } else if (arg == "--points" && i + 1 < argc) {
            POINTS = std::stoi(argv[++i]);
        } else if (arg == "--rectangular") {
            rectangular = true;
        } else if (arg == "--output" && i + 1 < argc) {
            filename = argv[++i];
        } else {
            std::cerr << "Argumento desconocido o incompleto: " << arg << std::endl;
            exit(1);
        }
    }
}

int main(int argc, char const* argv[]) {
    double SIZE = 1000;  // Valor por defecto
    int POINTS = 100;    // Valor por defecto
    bool rectangular = false;
    std::string filename = "output.off";  // Valor por defecto

    // Parsear los argumentos
    parse_arguments(argc, argv, SIZE, POINTS, rectangular, filename);

    // Inicializar la malla
    HalfEdgeMesh mesh(SIZE, POINTS);

    // Configurar generador de números aleatorios
    std::random_device rd;
    std::mt19937 gen(rd());
    std::uniform_real_distribution<double> dis(-SIZE + 10, SIZE - 10);

    // Iniciar el cronómetro
    auto start_time = std::chrono::high_resolution_clock::now();

    if (!rectangular) {
        // Insertar puntos aleatorios
        for (int i = 0; i < POINTS; ++i) {
            double x = dis(gen);
            double y = dis(gen);

            // Intentar agregar el vértice
            try {
                mesh.add_vertex(x, y);
            } catch (const std::runtime_error& e) {
                std::cerr << "Couldn't add vertex: " << e.what() << std::endl;
            }
        }
    } else {
        // Si la bandera rectangular está activada, generar una cuadrícula
        int grid_size = static_cast<int>(std::sqrt(POINTS));  // Número de columnas y filas
        double x_step = 2 * (SIZE - 500) / grid_size;  // Espaciado horizontal
        double y_step = 2 * (SIZE - 500) / grid_size;  // Espaciado vertical
        double start_x = -(SIZE - 500);
        double start_y = -(SIZE - 500);

        // Generar los vértices en la cuadrícula
        for (int i = 0; i < grid_size; ++i) {
            for (int j = 0; j < grid_size; ++j) {
                double x = start_x + i * x_step;
                double y = start_y + j * y_step;

                // Agregar el vértice a la malla
                try {
                    mesh.add_vertex(x, y);
                } catch (const std::runtime_error& e) {
                    std::cerr << "Couldn't add vertex: " << e.what() << std::endl;
                }
            }
        }
        mesh.add_restriction(Vertex(start_x + x_step*(grid_size/2)*0.72 , y_step*1.5), Vertex(start_x + x_step*(grid_size/2)*0.75, y_step*0.5));
    }

    // Detener el cronómetro
    auto end_time = std::chrono::high_resolution_clock::now();
    std::chrono::duration<double> elapsed = end_time - start_time;

    // Imprimir el tiempo de inserción
    std::cout << "Tiempo de inserción de puntos: " << elapsed.count() << " segundos." << std::endl;

    // Guardar la malla en un archivo .off
    mesh.write_to_off(filename);

    return 0;
}
