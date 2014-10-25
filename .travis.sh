#!/bin/sh

# Install libgit2 from untrusted source ppa
# sudo add-apt-repository "deb http://ubuntu-archive.mirror.nucleus.be/ utopic main"
# sudo add-apt-repository "deb-src http://ubuntu-archive.mirror.nucleus.be/ utopic main"

# sudo apt-get update -q &> /dev/null && echo "apt-get caches updated."

# if [[ $? != 0 ]]; then
# 	echo "apt-get update failed." > /dev/fd/2
# 	exit 1
# fi

pushd

mkdir banana
cd banana

wget "https://launchpad.net/ubuntu/+source/libgit2/0.21.1-1/+build/6494190/+files/libgit2-21_0.21.1-1_amd64.deb"
wget "https://launchpad.net/ubuntu/+source/libgit2/0.21.1-1/+build/6494190/+files/libgit2-dev_0.21.1-1_amd64.deb"

sudo dpkg -q -i "libgit2-21_0.21.1-1_amd64.deb"
sudo dpkg -q -i "libgit2-dev_0.21.1-1_amd64.deb"

pip install -q cffi && echo "Installed cffi."
sudo apt-get install -q python-qt4 > /dev/null \
	&& echo "Installed python-qt4"
	|| exit 1


apt-show-versions cffi libgit2-dev python-qt4
