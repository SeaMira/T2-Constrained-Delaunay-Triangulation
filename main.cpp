#include <iostream>
#include <random>
#include <stdexcept>
#include <chrono>  // Para cronometrar el tiempo
#include <string>
#include <sstream>
#include <fstream>
#include <cmath>

#include "src/Vertex.h"
#include "src/HalfEdge.h"
#include "src/Facet.h"
#include "src/Mesh.h"
#include <glad/glad.h>
#include <GLFW/glfw3.h>
#include "src/camera3.h"
#include "src/shader_m.h"


struct Vertex3 {
    double x, y, z;
};
bool loadOFF(const std::string& filename, std::vector<Vertex3>& vertices, std::vector<unsigned int>& indices);

void framebuffer_size_callback(GLFWwindow* window, int width, int height);
void mouse_callback(GLFWwindow* window, double xpos, double ypos);
void scroll_callback(GLFWwindow* window, double xoffset, double yoffset);
void processInput(GLFWwindow *window, float deltaTime);
void updateTriangleColor(HalfEdgeMesh& mesh, Camera& camera);

Camera* globCamera;

std::vector<Vertex3> selectedTriangle = {
    { 0.0, 0.0, 0.0 }, // Primer vértice
    { 0.0, 0.0, 0.0 }, // Segundo vértice
    { 0.0, 0.0, 0.0 }  // Tercer vértice
};

float deltaTime = 0.0f;	
float lastFrame = 0.0f;



// Función para parsear las opciones con flags
void parse_arguments(int argc, char const* argv[], double& SIZE, int& POINTS, bool& rectangular, std::string& filename, int& num_restrictions, double& rest_len) {
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
        } else if (arg == "--restrictions" && i + 1 < argc) {
            num_restrictions = std::stoi(argv[++i]);
        } else if (arg == "--rest_len" && i + 1 < argc) {
            rest_len = std::stod(argv[++i]);
        } else {
            std::cerr << "Argumento desconocido o incompleto: " << arg << std::endl;
            exit(1);
        }
    }
}

// Función para generar restricciones aleatorias sin intersecciones
void generate_random_restrictions(HalfEdgeMesh& mesh, int num_restrictions, double SIZE, double max_length) {
    std::random_device rd;
    std::mt19937 gen(rd());
    std::uniform_real_distribution<double> dis(-SIZE*0.99, SIZE*0.99);

    int restrictions_added = 0;
    while (restrictions_added < num_restrictions) {
        // Generar dos puntos aleatorios para la restricción
        double x1 = dis(gen);
        double y1 = dis(gen);
        double x2 = dis(gen);
        double y2 = dis(gen);

        // Verificar que no sean el mismo punto y que la distancia no exceda max_length
        double length = std::sqrt((x2 - x1) * (x2 - x1) + (y2 - y1) * (y2 - y1));
        if (length == 0 || length > max_length) continue;

        Vertex v1(x1, y1);
        Vertex v2(x2, y2);

        // Verificar que la nueva restricción no intersecta con las existentes
        bool intersects = false;
        const auto& restrictions = *(mesh.get_restrictions());

        for (size_t i = 0; i < restrictions.size(); i += 2) {
            // Cada restricción es un segmento definido por restrictions[i] y restrictions[i+1]
            if (i + 1 < restrictions.size()) {
                if (do_segments_intersect(
                        v1.to_cgal_point(), v2.to_cgal_point(),
                        restrictions[i].to_cgal_point(), restrictions[i + 1].to_cgal_point())) {
                    intersects = true;
                    break;
                }
            }
        }

        // Si no intersecta, agregar la restricción
        if (!intersects) {
            mesh.add_restriction(v1, v2);
            restrictions_added++;
        }
    }
}


int main(int argc, char const* argv[]) {
    double SIZE = 1000;  // Valor por defecto
    int POINTS = 100;    // Valor por defecto
    bool rectangular = false;
    int num_restrictions = 1;  
    double rest_len = 20.0;  // Valor por defecto
    std::string filename = "output.off";  // Valor por defecto

    // Parsear los argumentos
    parse_arguments(argc, argv, SIZE, POINTS, rectangular, filename, num_restrictions, rest_len);

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
                // std::cout << "Punto: " << x << ", " << y << std::endl;
                mesh.add_vertex(x, y);
            } catch (const std::runtime_error& e) {
                std::cerr << "Couldn't add vertex: " << e.what() << std::endl;
            }
        }
        auto construction__time = std::chrono::high_resolution_clock::now();
        std::chrono::duration<double> contruction_elapsed = construction__time - start_time;
        std::cout << "Tiempo de inserción de puntos: " << contruction_elapsed.count() << " segundos." << std::endl;
        std::cout << "Anadiendo restricciones" << std::endl;
        
        // Generar restricciones aleatorias
        generate_random_restrictions(mesh, num_restrictions, SIZE, rest_len);
    } else {
        // Si la bandera rectangular está activada, generar una cuadrícula
        int grid_size = static_cast<int>(std::sqrt(POINTS));  // Número de columnas y filas
        double x_step = 2 * (SIZE*0.9) / grid_size;  // Espaciado horizontal
        double y_step = 2 * (SIZE*0.9) / grid_size;  // Espaciado vertical
        double start_x = -(SIZE*0.9);
        double start_y = -(SIZE*0.9);

        // Generar los vértices en la cuadrícula
        for (int i = 0; i < grid_size; ++i) {
            for (int j = 0; j < grid_size; ++j) {
                double x = start_x + i * x_step;
                double y = start_y + j * y_step;

                // Agregar el vértice a la malla
                try {
                    // std::cout << "Punto: " << x << ", " << y << std::endl;
                    mesh.add_vertex(x, y);
                } catch (const std::runtime_error& e) {
                    std::cerr << "Couldn't add vertex: " << e.what() << std::endl;
                }
            }
        }
        // Generar restricciones aleatorias
        generate_random_restrictions(mesh, num_restrictions, SIZE*0.9, rest_len);
    }

    // Detener el cronómetro
    auto end_time = std::chrono::high_resolution_clock::now();
    std::chrono::duration<double> elapsed = end_time - start_time;

    // Imprimir el tiempo de inserción
    std::cout << "Tiempo de construccion total: " << elapsed.count() << " segundos." << std::endl;

    // Guardar la malla en un archivo .off
    mesh.write_to_off(filename);


    std::vector<Vertex3> vertices;
    std::vector<unsigned int> indices;
    if (!loadOFF(filename, vertices, indices)) {
        return -1;
    }



    // Inicializar GLFW
    if (!glfwInit()) {
        std::cerr << "Error al inicializar GLFW" << std::endl;
        return -1;
    }
    glfwWindowHint(GLFW_CONTEXT_VERSION_MAJOR, 3);
    glfwWindowHint(GLFW_CONTEXT_VERSION_MINOR, 3);
    glfwWindowHint(GLFW_OPENGL_PROFILE, GLFW_OPENGL_CORE_PROFILE);

    // Crear una ventana
    GLFWwindow* window = glfwCreateWindow(800, 600, "Delaunay Triangulation", nullptr, nullptr);
    if (!window) {
        std::cerr << "Error al crear la ventana" << std::endl;
        glfwTerminate();
        return -1;
    }
    glfwMakeContextCurrent(window);

    if (!gladLoadGLLoader((GLADloadproc)glfwGetProcAddress))
    {
        std::cout << "Failed to initialize GLAD" << std::endl;
        return -1;
    }

    glfwSetFramebufferSizeCallback(window, framebuffer_size_callback);
    glfwSetCursorPosCallback(window, mouse_callback);
    glfwSetScrollCallback(window, scroll_callback);

    glEnable(GL_DEPTH_TEST);

    Shader shader("vertex_shader.glsl", "fragment_shader.glsl");
    Shader restriction_shader("vertex_shader.glsl", "restriction_fragment_shader.glsl");

    glPolygonMode(GL_FRONT_AND_BACK, GL_LINE);

    shader.use();

    Camera camera(800, 600);
    camera.SetPosition((float) SIZE/2.0, -(float) SIZE, (float) SIZE/2.0);
    globCamera = &camera;



    // Configurar VBO, VAO y EBO
    unsigned int VBO, VAO, EBO;
    glGenVertexArrays(1, &VAO);
    glGenBuffers(1, &VBO);
    glGenBuffers(1, &EBO);

    glBindVertexArray(VAO);

    glBindBuffer(GL_ARRAY_BUFFER, VBO);
    glBufferData(GL_ARRAY_BUFFER, vertices.size() * sizeof(Vertex3), vertices.data(), GL_STATIC_DRAW);

    glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, EBO);
    glBufferData(GL_ELEMENT_ARRAY_BUFFER, indices.size() * sizeof(unsigned int), indices.data(), GL_STATIC_DRAW);

    // Configurar los atributos del vértice
    glVertexAttribPointer(0, 3, GL_DOUBLE, GL_FALSE, sizeof(Vertex3), (void*)0);
    glEnableVertexAttribArray(0);

    glBindBuffer(GL_ARRAY_BUFFER, 0);
    glBindVertexArray(0);

    std::vector<Vertex3> restrictions;
    for (const auto& restriction : *(mesh.get_restrictions())) {
        restrictions.push_back(Vertex3({restriction.x, 0.0, restriction.y}));
    }

    unsigned int restrictionVBO, restrictionVAO;
    glGenVertexArrays(1, &restrictionVAO);
    glGenBuffers(1, &restrictionVBO);

    glBindVertexArray(restrictionVAO);
    glBindBuffer(GL_ARRAY_BUFFER, restrictionVBO);
    glBufferData(GL_ARRAY_BUFFER, restrictions.size() * sizeof(Vertex3), restrictions.data(), GL_STATIC_DRAW);

    // Configurar los atributos del vértice para las restricciones
    glVertexAttribPointer(0, 3, GL_DOUBLE, GL_FALSE, sizeof(Vertex3), (void*)0);
    glEnableVertexAttribArray(0);

    glBindBuffer(GL_ARRAY_BUFFER, 0);
    glBindVertexArray(0);


    // selected T buffers
    unsigned int triangleVAO, triangleVBO;
    glGenVertexArrays(1, &triangleVAO);
    glGenBuffers(1, &triangleVBO);

    // Enlazar el VAO
    glBindVertexArray(triangleVAO);

    // Enlazar el VBO y cargar los datos
    glBindBuffer(GL_ARRAY_BUFFER, triangleVBO);
    glBufferData(GL_ARRAY_BUFFER, selectedTriangle.size() * sizeof(Vertex3), selectedTriangle.data(), GL_STATIC_DRAW);

    // Configurar los atributos del vértice (posición)
    glVertexAttribPointer(0, 3, GL_DOUBLE, GL_FALSE, sizeof(Vertex3), (void*)0);
    glEnableVertexAttribArray(0);

    // Desenlazar el VBO y el VAO
    glBindBuffer(GL_ARRAY_BUFFER, 0);
    glBindVertexArray(0);


    // Bucle de renderizado
    while (!glfwWindowShouldClose(window)) {
        glClearColor(1.0f, 1.0f, 1.0f, 1.0f);
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT);

        float currentFrame = static_cast<float>(glfwGetTime());
        deltaTime = currentFrame - lastFrame;
        lastFrame = currentFrame;

        processInput(window, deltaTime);
        updateTriangleColor(mesh, camera);
        // Enviar los datos actualizados al VBO
        glBindBuffer(GL_ARRAY_BUFFER, triangleVBO);
        glBufferSubData(GL_ARRAY_BUFFER, 0, selectedTriangle.size() * sizeof(Vertex3), selectedTriangle.data());
        glBindBuffer(GL_ARRAY_BUFFER, 0);

        glPolygonMode(GL_FRONT_AND_BACK, GL_LINE);
        shader.use();
        glLineWidth(1);
        shader.setMat4("model", camera.getModel());
        shader.setMat4("projection", globCamera->getProjection());
        shader.setMat4("view", globCamera->getView());

        // Dibujar la triangulación
        glBindVertexArray(VAO);
        glDrawElements(GL_TRIANGLES, indices.size(), GL_UNSIGNED_INT, 0);
        glBindVertexArray(0);

        glPolygonMode(GL_FRONT_AND_BACK, GL_FILL);
        // Dibujar el triángulo seleccionado
        glBindVertexArray(triangleVAO);
        glDrawArrays(GL_TRIANGLES, 0, 3);
        glBindVertexArray(0);

        // Dibujar restricciones
        restriction_shader.use();
        glLineWidth(3); 
        restriction_shader.setMat4("model", camera.getModel());
        restriction_shader.setMat4("projection", globCamera->getProjection());
        restriction_shader.setMat4("view", globCamera->getView());

        glBindVertexArray(restrictionVAO);
        glDrawArrays(GL_LINES, 0, restrictions.size());
        glBindVertexArray(0);

        camera.OnRender(deltaTime*10.0f);

        glfwSwapBuffers(window);
        glfwPollEvents();
    }

    glfwDestroyWindow(window);
    glfwTerminate();

    return 0;
}



void processInput(GLFWwindow *window, float deltaTime)
{
    if (glfwGetKey(window, GLFW_KEY_ESCAPE) == GLFW_PRESS)
        glfwSetWindowShouldClose(window, true);

    if (glfwGetKey(window, GLFW_KEY_W) == GLFW_PRESS)
        globCamera->OnKeyboard(1, deltaTime);
    if (glfwGetKey(window, GLFW_KEY_S) == GLFW_PRESS)
        globCamera->OnKeyboard(2, deltaTime);
    if (glfwGetKey(window, GLFW_KEY_A) == GLFW_PRESS)
        globCamera->OnKeyboard(3, deltaTime);
    if (glfwGetKey(window, GLFW_KEY_D) == GLFW_PRESS)
        globCamera->OnKeyboard(4, deltaTime);
    if (glfwGetKey(window, GLFW_KEY_SPACE) == GLFW_PRESS)
        globCamera->OnKeyboard(5, deltaTime);
    if (glfwGetKey(window, GLFW_KEY_LEFT_SHIFT) == GLFW_PRESS)
        globCamera->OnKeyboard(6, deltaTime);
    if (glfwGetKey(window, GLFW_KEY_E) == GLFW_PRESS)
        globCamera->OnKeyboard(7, deltaTime);
    if (glfwGetKey(window, GLFW_KEY_Q) == GLFW_PRESS)
        globCamera->OnKeyboard(8, deltaTime);
    
    
}

// glfw: whenever the window size changed (by OS or user resize) this callback function executes
// ---------------------------------------------------------------------------------------------
void framebuffer_size_callback(GLFWwindow* window, int width, int height){
    // make sure the viewport matches the new window dimensions; note that width and 
    // height will be significantly larger than specified on retina displays.
    globCamera->SetScrSize(width, height);
    glViewport(0, 0, width, height);
}


void mouse_callback(GLFWwindow* window, double xposIn, double yposIn) {
    globCamera->OnMouse((float)xposIn, (float)yposIn);
}

// // glfw: whenever the mouse scroll wheel scrolls, this callback is called
// // ----------------------------------------------------------------------
void scroll_callback(GLFWwindow* window, double xoffset, double yoffset) {
    globCamera->OnScroll(static_cast<float>(yoffset));
}





// Función para leer el archivo .off y cargar vértices e índices
bool loadOFF(const std::string& filename, std::vector<Vertex3>& vertices, std::vector<unsigned int>& indices) {
    std::ifstream file(filename);
    if (!file.is_open()) {
        std::cerr << "No se pudo abrir el archivo: " << filename << std::endl;
        return false;
    }

    std::string line;
    std::getline(file, line);

    // Verificar si el archivo empieza con "OFF"
    if (line != "OFF") {
        std::cerr << "Archivo no tiene formato OFF válido." << std::endl;
        return false;
    }

    int num_vertices, num_faces, num_edges;
    file >> num_vertices >> num_faces >> num_edges;

    // Leer todos los vértices
    vertices.resize(num_vertices);
    for (int i = 0; i < num_vertices; ++i) {
        file >> vertices[i].x >> vertices[i].z >> vertices[i].y;
    }

    // Leer las caras (triángulos)
    for (int i = 0; i < num_faces; ++i) {
        int num_vertices_in_face;
        file >> num_vertices_in_face;  // Esto debería ser siempre 3 para triángulos
        if (num_vertices_in_face != 3) {
            std::cerr << "Se encontró una cara que no es un triángulo." << std::endl;
            continue;
        }

        unsigned int idx1, idx2, idx3;
        file >> idx1 >> idx2 >> idx3;

        // Añadir los índices del triángulo al vector de índices
        indices.push_back(idx1);
        indices.push_back(idx2);
        indices.push_back(idx3);
    }

    file.close();
    return true;
}


void updateTriangleColor(HalfEdgeMesh& mesh, Camera& camera) {
    // Calcular el punto de intersección en el plano z=0
    glm::vec3 camPos = camera.getPosition();
    glm::vec3 camFront = camera.getFront();
    float t = -camPos.y / camFront.y;
    glm::vec3 intersectionPoint = camPos + t * camFront;

    // Buscar el triángulo en la intersección y cambiar su color
    std::shared_ptr<HalfEdge> hf = mesh.locate_triangle(Vertex(intersectionPoint.x, intersectionPoint.z));
    if (hf != nullptr) {
       std::shared_ptr<Facet> f = hf->facet;
       selectedTriangle[0].x = f->a->x;
       selectedTriangle[0].y = 0.01;
       selectedTriangle[0].z = f->a->y;
       selectedTriangle[1].x = f->b->x;
       selectedTriangle[1].y = 0.01;
       selectedTriangle[1].z = f->b->y;
       selectedTriangle[2].x = f->c->x;
       selectedTriangle[2].y = 0.01;
       selectedTriangle[2].z = f->c->y;
    } else {
       selectedTriangle[0] = Vertex3({0.0, 0.0, 0.0});
       selectedTriangle[1] = Vertex3({0.0, 0.0, 0.0});
       selectedTriangle[2] = Vertex3({0.0, 0.0, 0.0});

    }
}