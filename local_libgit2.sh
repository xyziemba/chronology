#!/bin/sh

set -e

if [ -z ${LIBGIT2+x} ]; then
	echo "Variable LIBGIT2 is not set. Please specify the location for LIBGIT2.";
	exit 1;
fi

if [ ! -d "$LIBGIT2/lib" ]; then
	curl -L -o libgit2-0.23.0.tar.gz https://github.com/libgit2/libgit2/archive/v0.23.0.tar.gz;
	tar xzf libgit2-0.23.0.tar.gz;
	cd libgit2-0.23.0;
	mkdir build;
	cd build;
	cmake .. -DBUILD_CLAR=NO -DCMAKE_BUILD_TYPE=Release -DCMAKE_INSTALL_PREFIX=$LIBGIT2;
	make install;
else
	echo 'Using cached copy of libgit2.';
fi