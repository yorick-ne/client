#!/bin/sh

# Install libgit2 from ubuntu vivid repos
apt_repo="
deb http://archive.canonical.com/ubuntu vivid banana
deb-src http://archive.canonical.com/ubuntu vivid banana
"
sudo echo $apt_repo >> "/etc/apt/sources.list"

sudo apt-get update -q && echo "apt-get caches updated"

if [[ $? != 0 ]]; then
	echo "apt-get update failed." > /dev/fd/2
	exit 1
fi


sudo apt-get install -q cmake && echo "Installed cmake."
pip install -q cffi && echo "Installed cffi."
sudo apt-get install -q libgit2-dev python-qt4
