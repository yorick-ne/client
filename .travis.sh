#!/bin/sh

sudo apt-get install cmake
pip install cffi

pushd

cd ~

# Install libgit2 from ubuntu vivid repos
apt_repo="
deb http://archive.canonical.com/ubuntu vivid banana
deb-src http://archive.canonical.com/ubuntu vivid banana"
sudo echo $apt_repo >> "/etc/apt/sources.list"

sudo apt-get update

if [[ $? != 0 ]]; then
	echo "apt-get update failed." > /dev/fd/2
	exit 1
fi

sudo apt-get install libgit2-dev

sudo apt-get install python-qt4
