cmake_minimum_required(VERSION 3.21)

# On a host without a version backend, --help still prints usage and the
# host-only invocation reports the unavailable facts.
foreach(option IN ITEMS "" "--help" "--mount;D:/music")
  execute_process(COMMAND "${PROBE}" ${option}
    RESULT_VARIABLE result OUTPUT_VARIABLE output ERROR_VARIABLE errors)
  if(NOT result STREQUAL "1" OR NOT errors MATCHES "\\[error\\] platform query failed")
    message(FATAL_ERROR "Host query (${option}) returned ${result}: ${errors}")
  endif()
  if(output MATCHES "os version:" OR (option STREQUAL "--help" AND NOT errors MATCHES "usage:"))
    message(FATAL_ERROR "Unexpected host or usage output: ${output}\n${errors}")
  endif()
endforeach()

execute_process(COMMAND "${PROBE}" --to-posix [[D:\Music]]
  RESULT_VARIABLE result OUTPUT_VARIABLE output ERROR_VARIABLE errors)
if(NOT result STREQUAL "0" OR NOT output MATCHES "/mnt/d/Music" OR
   NOT errors MATCHES "\\[warn\\] platform query failed")
  message(FATAL_ERROR "Fallback translation returned ${result}: ${output}\n${errors}")
endif()
