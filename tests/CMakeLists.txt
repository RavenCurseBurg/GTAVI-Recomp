add_executable(
  gtavi_tests
  main.cpp
  error_tests.cpp
  log_tests.cpp
  path_tests.cpp
  platform_tests.cpp
)

target_link_libraries(gtavi_tests PRIVATE gtavi::core gtavi_warnings)

add_test(NAME gtavi_tests COMMAND gtavi_tests)

if(TARGET gtavi_probe)
  add_test(NAME gtavi_probe_mounts
    COMMAND ${CMAKE_COMMAND} -DPROBE=$<TARGET_FILE:gtavi_probe> -P ${CMAKE_CURRENT_SOURCE_DIR}/probe_mounts.cmake)
  if(NOT CMAKE_CROSSCOMPILING AND CMAKE_HOST_SYSTEM_NAME MATCHES "^(Linux|Windows)$")
    add_test(NAME gtavi_probe_host_release
      COMMAND ${CMAKE_COMMAND} -DPROBE=$<TARGET_FILE:gtavi_probe> -P ${CMAKE_CURRENT_SOURCE_DIR}/probe_host_release.cmake)
  endif()
endif()
