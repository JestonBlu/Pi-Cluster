# PySpark Raspberry Pi Cluster Project

This repo is being used to document my project for building a small raspberry pi cluster running spark. Similar to [this article](http://makezine.com/projects/build-a-compact-4-node-raspberry-pi-cluster/) which I used as a guide, I only wanted to have to use a single wall plug for the entire setup. I also wanted to minimize the footprint of the cluster. In this example all of the devices except for the USB hub are powered by USB.

# Shopping List
* 3 - Raspberry Pi 3b, (i also added an old 2b, not shown in pictures)
* 1 - GeauxRobot Raspberry Pi 3 Model B 4-layer Dog Bone Stack (case)
* 1 - Anker PowerPort 6 (60W 6-Port USB Charging Hub) (power supply)
* 1 - Black Box USB-Powered 10/100 5-Port Switch
* 3 - 6" Ethernet Network Cable

# Assembly

1) Assemble the pi's and case. (shown are 3 pi's, but i ended up added a 4th RPI 2b)
![](images/img01.jpg)
![](images/img03.jpg)

2) Attach the network switch to the top of the cluster
![](images/img04.jpg)

3) Attach the USB power supply to the bottom of the cluster
![](images/img05.jpg)

4) Attach the network cable
![](images/img06.jpg)

5) Attach the USB to mini-usb cables from the USB hub to each pi
![](images/img07.jpg)

6) Attach the USB cable to the network switch power input
![](images/img08.jpg)

# Installing the OS
I already use arch on my desktop so im using that on the Pi's. The arch documentation for downloading and setting up the ARM OS is straightfoward so I will not repeat it, but the link to the site is [here](https://archlinuxarm.org/platforms/armv8/broadcom/raspberry-pi-3).

# Networking the Pi's Together
After booting up all of the pi's with a new arch install, the first thing I did was set up a server so the pi's could communicate through the network switch. This was fairily challenging for me and I had to do a lot of searching and reading before I got everything to work.

I designated the pi on the bottom of the stack the head node with hostname rpi1. The others got rpi[2-4]. The steps for setting up the server went like this:

* Assign a static IP to the ethernet device (eth0). In my setup I am using 192.168.1.0 as the domain so the first server (head node) will get 192.168.1.1

```sh
# Assigns the static IP
ip addr add 192.168.1.1/24 broadcast 192.168.1.255 dev eth0
```

* Fill out the dhcpd.conf file

```sh
# Fill out /etc/dhcpd.conf
ddns-update-style none;
authoritative;
log-facility local7;

# The internal cluster network
option broadcast-address 192.168.1.255;
option routers 192.168.1.1;
default-lease-time 600;
max-lease-time 7200;
option domain-name "cluster";
option domain-name-servers 8.8.8.8, 8.8.4.4;
subnet 192.168.1.0 netmask 255.255.255.0 {
   range 192.168.1.14 192.168.1.250;

   host rpi1 {
      hardware ethernet b8:27:eb:22:60:fb;
      fixed-address 192.168.1.1;
   }
   host rpi2 {
      hardware ethernet b8:27:eb:a0:a1:7f;
      fixed-address 192.168.1.2;
   }
   host rpi3 {
      hardware ethernet b8:27:eb:68:b6:a3;
      fixed-address 192.168.1.3;
   }
   host rpi4 {
      hardware ethernet b8:27:eb:0b:4e:2c;
      fixed-address 192.168.1.4;
   }
}

```

* Start the service to see if it works.

```sh
systemctl start dhcpd4@eth0.service

```

**NOTE**: This is where I started running into problems. I was able to assign a static ip address to the pi from the command line, but i was not able to get it to work on boot. There were several guides online that showed how to set up a profile using netctl, but it only seemed to work on wireless. When I went to enable dhcpd systemctl would fail because it was trying to start the service before eth0 had an ip assigned. I got around this by putting the shell commands in a bash script and enabling it to run on boot. See below. I started the script with my intials so I could easily find it later.

* Create the file /usr/bin/jeb-start-dhcpd.sh

```sh
#!/bin/sh
ip addr add 192.168.1.1/24 broadcast 192.168.1.255 dev eth0
systemctl start dhcpd4@eth0.service
```

* Next make it executable

```sh
chmod 755 /usr/bin/jeb-start-dhcpd.sh
```

* Create a custom .service file to start the script on boot. `/etc/systemd/system/jeb-start-dhcpd.service`

```sh
[Unit]
Description=Custom DHCPD Start up Script

[Service]
ExecStart=/usr/bin/jeb-start-dhcpd.sh

[Install]
WantedBy=multi-user.target
```

* Enable the service

```sh
systemctl enable jeb-start-dhcpd.service
```

* You should also enable the DHCPCD client serivce on each of the other pi's. While you are in there is a good idea to change the host name and enable SSHD and a few other items. Also go ahead and create the user and change the default password.

```sh
systemctl enable dhcpcd@eth0.service
systemctl enable sshd.service

echo rpi[2-4] > /etc/hostname

# Uncomment `en_US.UTF-8` in `/etc/locale.gen`, then run
locale-gen
echo LANG=en_US.UTF-8 > /etc/locale.conf
export LANG=en_US.UTF-8

ln -s /usr/share/zoneinfo/America/Chicago > /etc/localtime
```








* Append these IPs to the /etc/hosts file

```sh
192.168.1.1     rpi1      rpi1
192.168.1.2     rpi2      rpi2
192.168.1.3     rpi3      rpi3
192.168.1.4     rpi4      rpi4
```

# Configuring the OS

Now install some packages. Only rpi1 has access to the internet so Im going to install the packages there and then copy the packages over to each of the other pi's and install them locally. First, I want to set up my user and change the default passwords.

```sh
# get wget first
pacman -S wget sudo

# Change the root password
passwd

# Add a new user and change password
useradd -m -g users -G wheel,storage,power -s /bin/bash someusername
passwd someusername

EDITOR=nano visudo
# uncomment
# %wheel ALL=(ALL) ALL

# Log out and log back in as the new username
# Delete the default user alarm
userdel -r alarm

# From rpi1, create a list of packages to download and create a local repo
mkdir cluster-repo
sudo pacman -Sp base-devel bash-completion git rsync > ~/repo.list
wget -P ~/cluster-repo/ -i repo.list
cd cluster-repo
repo-add cluster.repo.db.tar.gz *.pkg.tar.xz

# Temporarily copy the repos to each pi, once credentials are set up we should link each pi to the rpi1 repository
# make sure the cluster-repo folder exists on each pi
scp ~/cluster-repo/* alarm@rpi2:~/cluster-repo
scp ~/cluster-repo/* alarm@rpi3:~/cluster-repo
scp ~/cluster-repo/* alarm@rpi4:~/cluster-repo
```

* Next you should log in to each pi, add the local rpi1 repo and install sudo so you can create the same user on all of the pis as well.

```sh
# Using RPI2 as an example
# Add a repo pointing to rpi:~/cluster-repo
nano /etc/pacman.conf

# Append this to the conf file
SigLevel = Never
[cluster.repo]
Server = file:///home/alarm/cluster-repo/

# update pacman
pacman -Sy

# install sudo
pacman -S sudo
```


* Now you should be able to set up a new user with sudo rights and change password on each of the other pis.

```bash
# Change the root password
passwd

# Add a new user and change password
useradd -m -g users -G wheel,storage,power -s /bin/bash someusername
passwd someusername

EDITOR=nano visudo
# uncomment
# %wheel ALL=(ALL) ALL

# Delete the default user alarm, you will have to log out and log back in as your new user
userdel -r alarm

# Set up the ssh key for communicating between the pis
ssh-keygen

# copy id_rsa.pub and copy it to rpi1: .ssh/authorized_keys
# do this for all of the pis, then copy the authorized_keys file from
# rpi1 to all of the other pis
scp ~/.ssh/authorized_keys rpi2:~/.ssh
scp ~/.ssh/authorized_keys rpi3:~/.ssh
scp ~/.ssh/authorized_keys rpi4:~/.ssh
```









# Setting up Spark

Set up Environmental variables

```sh
export JAVA_HOME=/usr/lib/jvm/java-8-openjdk
export PYTHONPATH=~/Apps/Miniconda3/envs/py35
export SPARK_HOME=~/Apps/Spark21

export PATH="$PYTHONPATH/bin:$PATH"
export PATH="$SPARK_HOME/bin:$PATH"
export PATH="$JAVA_HOME/bin:$PATH"

export SPARK_LOCAL_IP=localhost
```
