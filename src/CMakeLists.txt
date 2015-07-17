add_executable(timetravel main.c)

if (WIN32)
	if (MSVC)
		# /MTd and /MT instructs MSVC to build against the debug and release,
		# respectively, static CRT link libraries. The default is to use the
		# CRT DLL.
		target_compile_options(timetravel PUBLIC "$<$<CONFIG:DEBUG>:/MTd>")
		target_compile_options(timetravel PUBLIC "$<$<CONFIG:RELEASE>:/MT>")

		# TODO: don't use dangerous string functions
		target_compile_definitions(timetravel PUBLIC _CRT_SECURE_NO_WARNINGS)
	endif()
	target_include_directories(timetravel PUBLIC ${GIT2_INCLUDE_PATH} ${UV_INCLUDE_PATH})
	target_link_libraries(timetravel ${GIT2_LIB} ${UV_LIB} psapi Ws2_32 iphlpapi userenv)
else()
	target_link_libraries(timetravel uv git2)
endif()