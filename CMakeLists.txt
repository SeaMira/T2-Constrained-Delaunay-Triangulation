cmake_minimum_required(VERSION 3.20)

project(delaunay_mesh_project CXX)
set(CXX_STANDARD 20)

find_package(CGAL REQUIRED)
find_package(OpenGL REQUIRED)
find_package(GLFW3 REQUIRED)

add_subdirectory(src)
add_subdirectory(extern)

find_package(CGAL REQUIRED OPTIONAL_COMPONENTS Qt5)
if(CGAL_Qt5_FOUND)
  #required to use basic_viewer
  add_definitions(-DCGAL_USE_BASIC_VIEWER -DQT_NO_KEYWORDS)
endif()

if ( CGAL_FOUND )
  #create the executable of the application
  create_single_source_cgal_program("main.cpp")
  if(CGAL_Qt5_FOUND )
    #link it with the required CGAL libraries
    target_link_libraries(Triangulation PUBLIC CGAL::CGAL_Qt5 CGAL::CGAL_Basic_viewer glad glm)
    target_link_libraries(main PUBLIC Triangulation glfw3 glad)
    target_include_directories(main PUBLIC ${OPENGL_INCLUDE_DIRS} ${GLFW3_INCLUDE_DIRS})
  endif()
else()
    message(STATUS "This program requires the CGAL library, and will not be compiled.")
endif()