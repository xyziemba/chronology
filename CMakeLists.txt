cmake_minimum_required (VERSION 3.2)
project (TimeTravel)

# On Windows, we need help finding LIBGIT2 and LIBUV
if (WIN32)
	set(GIT2_LIB_PATH "" CACHE PATH "Path to git2.dll")
	set(GIT2_INCLUDE_PATH "" CACHE PATH "Path to git2.h")
	set(UV_LIB_PATH "" CACHE PATH "Path to libuv.lib")
	set(UV_INCLUDE_PATH "" CACHE PATH "Path to uv.h")

	find_library(
		GIT2_LIB
		git2
		PATHS ${GIT2_LIB_PATH}
		)

	find_file(
		GIT2_HEADER
		git2.h
		PATHS ${GIT2_INCLUDE_PATH}
		)

	find_library (
		UV_LIB
		libuv
		PATHS ${UV_LIB_PATH}
		)

	find_file (
		UV_HEADER
		uv.h
		PATHS ${UV_INCLUDE_PATH}
		)

	if (NOT EXISTS ${GIT2_LIB})
		message( SEND_ERROR "Unable to find git2.dll. Set GIT2_LIB_PATH.")
	endif()
	if (NOT EXISTS ${GIT2_HEADER})
		message( SEND_ERROR "Unable to find git2.h. Set GIT2_INCLUDE_PATH.")
	endif()
	if (NOT EXISTS ${UV_LIB})
		message( SEND_ERROR "Unable to find uv.lib. Set UV_LIB_PATH.")
	endif()
	if (NOT EXISTS ${UV_HEADER})
		message( SEND_ERROR "Unable to find uv.h. Set UV_INCLUDE_PATH.")
	endif()

endif()

add_subdirectory(src)