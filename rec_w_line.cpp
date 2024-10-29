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
    float x, y, z;
};
bool loadOFF(const std::string& filename, std::vector<Vertex3>& vertices, std::vector<unsigned int>& indices);

void framebuffer_size_callback(GLFWwindow* window, int width, int height);
void mouse_callback(GLFWwindow* window, double xpos, double ypos);
void scroll_callback(GLFWwindow* window, double xoffset, double yoffset);
void processInput(GLFWwindow *window, float deltaTime);

Camera* globCamera;

float deltaTime = 0.0f;	
float lastFrame = 0.0f;



// Función para parsear las opciones con flags
void parse_arguments(int argc, char const* argv[], double& SIZE, int& POINTS, std::string& filename) {
    for (int i = 1; i < argc; ++i) {
        std::string arg = argv[i];
        if (arg == "--size" && i + 1 < argc) {
            SIZE = std::stod(argv[++i]);
        } else if (arg == "--points" && i + 1 < argc) {
            POINTS = std::stoi(argv[++i]);
        }  else if (arg == "--output" && i + 1 < argc) {
            filename = argv[++i];
        } else {
            std::cerr << "Argumento desconocido o incompleto: " << arg << std::endl;
            exit(1);
        }
    }
}


int main(int argc, char const* argv[]) {
    double SIZE = 1000;  // Valor por defecto
    int POINTS = 0;    // Valor por defecto
    bool rectangular = false;
    std::string filename = "rec_w_line.off";  // Valor por defecto

    // Parsear los argumentos
    parse_arguments(argc, argv, SIZE, POINTS, filename);

    // Inicializar la malla
    HalfEdgeMesh mesh(SIZE, POINTS);

    // Configurar generador de números aleatorios
    std::random_device rd;
    std::mt19937 gen(rd());
    std::uniform_real_distribution<double> disx(-0.98*SIZE/2.0, 0.98*SIZE);
    std::uniform_real_distribution<double> disy(-0.98*SIZE/4.0, 0.98*SIZE/4.0);

    // Iniciar el cronómetro
    auto start_time = std::chrono::high_resolution_clock::now();

    // mesh.add_vertex(-SIZE/2.0, SIZE/4.0);
    // mesh.add_vertex(-SIZE/2.0, -SIZE/4.0);
    mesh.add_restriction(Vertex(-SIZE/2.0, SIZE/4.0), Vertex(-SIZE/2.0, -SIZE/4.0));
    mesh.add_restriction(Vertex(-SIZE/2.0, -SIZE/4.0), Vertex(SIZE/2.0, -SIZE/4.0));
    mesh.add_restriction(Vertex(SIZE/2.0, -SIZE/4.0), Vertex(SIZE/2.0, SIZE/4.0));
    mesh.add_restriction(Vertex(SIZE/2.0, SIZE/4.0), Vertex(-SIZE/2.0, SIZE/4.0));
    mesh.add_restriction(Vertex(-SIZE/4.0, 0.0), Vertex(SIZE/4.0, 0.0));

    if ( POINTS > 0) {
        // Insertar puntos aleatorios
        for (int i = 0; i < POINTS; ++i) {
            double x = disx(gen);
            double y = disy(gen);

            // Intentar agregar el vértice
            try {
                // std::cout << "Punto: " << x << ", " << y << std::endl;
                mesh.add_vertex(x, y);
            } catch (const std::runtime_error& e) {
                std::cerr << "Couldn't add vertex: " << e.what() << std::endl;
            }
        }
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

    // glLineWidth(3); 
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
    glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, sizeof(Vertex3), (void*)0);
    glEnableVertexAttribArray(0);

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



        shader.setMat4("model", camera.getModel());
        shader.setMat4("projection", globCamera->getProjection());
        shader.setMat4("view", globCamera->getView());

        // Dibujar la triangulación
        glBindVertexArray(VAO);
        glDrawElements(GL_TRIANGLES, indices.size(), GL_UNSIGNED_INT, 0);
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
