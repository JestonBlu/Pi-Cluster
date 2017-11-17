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

* You should also enable the DHCPCD client serivce on each of the other pi's. While you are in there is a good idea to change the host name and enable SSHD and a few other items.

```sh
systemctl enable dhcpcd@eth0.service
systemctl enable sshd.service

echo rpi[2-4] > /etc/hostname

# Uncomment `en_US.UTF-8` in `/etc/locale.gen`, then run
locale-gen
echo LANG=en_US.UTF-8 > /etc/locale.conf
export LANG=en_US.UTF-8

ln -s /usr/share/zoneinfo/America/Chicago > /etc/localtime

# I went ahead anc created swap files for each of the pis
fallocate -l 2G /swap
dd if=/dev/zero of=/swap bs=1M count=1024
mkswap /swap
swapon /swap

# nano /etc/fstab
swap none swap defaults 0 0

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
mkdir cluster.repo
sudo pacman -Sp base-devel bash-completion git rsync nfs-utils yajl > ~/repo.list
wget -P ~/cluster.repo/ -i repo.list
cd cluster.repo
repo-add cluster.repo.db.tar.gz *.pkg.tar.xz

# Temporarily copy the repos to each pi, once credentials are set up we should link
# each pi to the rpi1 repository make sure the cluster-repo folder exists on each pi
scp ~/cluster.repo/* alarm@rpi2:~/cluster.repo
scp ~/cluster.repo/* alarm@rpi3:~/cluster.repo
scp ~/cluster.repo/* alarm@rpi4:~/cluster.repo
```


* Next you should log in to each pi, add the local rpi1 repo and install sudo so you can create the same user on all of the pis as well.

```sh
# Using RPI2 as an example
# Add a repo pointing to rpi:~/cluster-repo
nano /etc/pacman.conf

# Append this to the conf file
SigLevel = Never
[cluster.repo]
Server = file:///home/alarm/cluster.repo/

# update pacman
pacman -Syyu

# install sudo and others
pacman -S sudo nfs-utils bash-completion base-devel git rsync yajl
```

* Now you should be able to set up a new user with sudo rights and change password on each of the other pis.

```bash
# Using RPI2 as an example
# Change the root password
passwd

# Add a new user and change password
useradd -m -g users -G wheel,storage,power -s /bin/bash someusername
passwd someusername

EDITOR=nano visudo
# uncomment
# %wheel ALL=(ALL) ALL

# Delete the default user alarm on all of the pis
userdel -r alarm

# Set up the ssh key for communicating between the pis
ssh-keygen

# copy id_rsa.pub to rpi1: .ssh/authorized_keys
scp .ssh/id_rsa.pub rpi1:~/.ssh/id_rsa_rpi2.pub

# Append the key to the authorized_keys file
cat .ssh/id_rsa_rpi2.pub >> .ssh/authorized_keys

# Copy the authorized_keys file back to rpi2
scp ~/.ssh/authorized_keys rpi2:~/.ssh
```

* Lastly I want to create a repository on RPI1 that the other pis can link to so I dont have to copy all of the packges to each machine. In order to do this I am going to create a NFS share on RPI and I am going to point it to the pacman cache on rpi1 that way when i install a package on rpi1, the other pis can access the packages without me having to copy it. Im also going to create a separate nfs folder that can be used to exchange data between the Pi's.

```sh
# On RPI1
mkdir -p /srv/nfs /home/[username]/nfs
mount --bind /home/[username]/nfs /srv/nfs

# /etc/fstab
# NFS on RPI1
/home/[username]/nfs /srv/nfs none bind 0 0

# Edit /etc/exports and Append
/var/cache/pacman/pkg        *(rw,sync)
/srv/nfs                     *(rw,sync)

# Start the server
sudo systemctl enable nfs-server.service
```

```sh
# Net log into each Pi and edit
# /etc/fstab
rpi1:/var/cache/pacman/pkg/ /home/[username]/cluster.repo nfs auto 0 0
rpi1:/srv/nfs/              /home/[username]/nfs          nfs auto 0 0

# Now we have created a mount point that pacman is already using as a repository
# Delete the packages that are currently in cluster.repo and then start and enable
# the nfs client on each of the pis
sudo systemctl enable nfs-client.target
rm cluster.repo/*

# Now reboot each machine and everything should be good to go!
```

The only downside now is that you have to rebuild the package db anytime you want to install new packages, I created a little script for convenience.

```sh
#!/bin/sh
repo-add -n /var/cache/pacman/pkg/cluster.repo.db.tar.gz /var/cache/pacman/pkg/*.pkg.tar.xz

# Make is executable
sudo chmod 755 /usr/bin/jeb-build-repo.sh
```
