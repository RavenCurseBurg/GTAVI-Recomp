add_test_executable(project_regular_file_mode "${CMAKE_CURRENT_LIST_DIR}/regular_file_mode.cpp")
target_include_directories(project_regular_file_mode PRIVATE "${LIBS_INCLUDE_DIR}")
target_link_libraries(project_regular_file_mode PRIVATE libkernel libc)
configure_windows_unwind(project_regular_file_mode)
add_test(NAME project_regular_file_mode COMMAND project_regular_file_mode)
set_tests_properties(project_regular_file_mode PROPERTIES
  WORKING_DIRECTORY "${CMAKE_CURRENT_BINARY_DIR}/mode-fixture")
file(MAKE_DIRECTORY "${CMAKE_CURRENT_BINARY_DIR}/mode-fixture")
