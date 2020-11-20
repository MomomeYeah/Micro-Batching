# -*- mode: ruby -*-
# vi: set ft=ruby :

VAGRANTFILE_API_VERSION = '2'

@script = <<SCRIPT
# update apt
sudo apt-get update
sudo apt-get install -y python3-pip
sudo pip3 install -r /vagrant/requirements.txt
SCRIPT

Vagrant.configure(VAGRANTFILE_API_VERSION) do |config|
  config.vm.box = 'bento/ubuntu-20.04'
  config.vm.network "forwarded_port", guest: 8000, host: 8000
  config.vm.provision 'shell', inline: @script

  config.vm.provider "virtualbox" do |vb|
    vb.customize ["modifyvm", :id, "--cableconnected1", "on"]
    vb.customize ["modifyvm", :id, "--memory", "1024"]
    vb.customize ["modifyvm", :id, "--name", "Micro-Batching - Ubuntu 20.04"]
  end
end
