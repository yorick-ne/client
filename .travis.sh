#!/bin/sh

# Install libgit2 from untrusted source ppa
sudo add-apt-repository ppa:xav0989/libgit2 -y

sudo apt-get update -q && echo "apt-get caches updated"

if [[ $? != 0 ]]; then
	echo "apt-get update failed." > /dev/fd/2
	exit 1
fi


sudo apt-get install -q cmake && echo "Installed cmake."
pip install -q cffi && echo "Installed cffi."
sudo apt-get install -q libgit2-dev python-qt4
