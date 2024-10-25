cmake_minimum_required(VERSION 3.20)

project(delaunay_mesh_project CXX)
set(CXX_STANDARD 20)

find_package(CGAL REQUIRED)

add_subdirectory(src)

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
    target_link_libraries(Triangulation PUBLIC CGAL::CGAL_Qt5 CGAL::CGAL_Basic_viewer)
    target_link_libraries(main PUBLIC Triangulation)
  endif()
else()
    message(STATUS "This program requires the CGAL library, and will not be compiled.")
endif()