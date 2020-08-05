#!/bin/bash -x
sudo apt-get install -y wget gnupg2 lsb-release
wget https://repo.percona.com/apt/percona-release_latest.generic_all.deb
sudo dpkg -i percona-release_latest.generic_all.deb
sudo apt-get install -y percona-toolkit

