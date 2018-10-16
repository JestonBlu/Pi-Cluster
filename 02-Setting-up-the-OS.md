# Installing the OS
I already use arch on my desktop so im using that on the Pi's. The arch documentation for downloading and setting up the ARM OS is straightfoward so I will not repeat it, but the link to the site is [here](https://archlinuxarm.org/platforms/armv8/broadcom/raspberry-pi-3).

Get a working internet connection

```sh
# As root
wifi-menu
netctl enable [wifi-menu profile]

# Upgrade the system
pacman -Syu
```

# Networking the Pi's Together
After booting up all of the pi's with a new arch install, the first thing I did was set up a server so the pi's could communicate through the network switch. I designated the pi on the bottom of the stack the head node with hostname rpi1. The others got rpi[2-4]. The steps for setting up the server went like this:

* Assign a static IP to the ethernet device (eth0). In my setup I am using 192.168.1.0 as the domain so the first server (head node) will get 192.168.1.1
* I initially used dhcp to connect the network, but I repeatedly ran into problems so in the end I had each pi assign a static IP on boot.
* For each of the pi's repeat all of the steps in this section for each pi. Be sure to make the appropriate ip changes or each pi.

```sh
# Assigns the static IP
ip addr add 192.168.1.1/24 broadcast 192.168.1.255 dev eth0
```

* Create the file /usr/bin/jeb-set-ip.sh

```sh
#!/bin/sh
ip addr add 192.168.1.1/24 broadcast 192.168.1.255 dev eth0
```

* Next make it executable

```sh
chmod 755 /usr/bin/jeb-set-ip.sh
```

* Create a custom .service file to start the script on boot. `/etc/systemd/system/jeb-set-ip.service`

```sh
[Unit]
Description=Set a static IP

[Service]
ExecStart=/usr/bin/jeb-set-ip.sh

[Install]
WantedBy=multi-user.target
```

* Enable the service

```sh
systemctl enable jeb-set-ip.service
```

# Configuring the OS

```sh
systemctl enable sshd.service

echo rpi1 > /etc/hostname

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
for i in $(cat repo.list) ; do (cd ~/cluster.repo && curl -O $i); done
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
# Log into each Pi and edit
# /etc/fstab
rpi1:/var/cache/pacman/pkg/ /home/[username]/cluster.repo nfs auto 0 0
rpi1:/srv/nfs/              /home/[username]/nfs          nfs auto 0 0

# Now we have created a mount point that pacman is already using as a repository
# Delete the packages that are currently in cluster.repo and then start and enable
# the nfs client on each of the pis
sudo systemctl enable nfs-client.target
rm cluster.repo/*

# You also need up update /etc/pacman.conf to update the alarm user to your username
SigLevel = Never
[cluster.repo]
Server = file:///home/username/cluster.repo/

# Now reboot each machine and everything should be good to go!
```

The only downside now is that you have to rebuild the package db anytime you want to install new packages, I created a little script for convenience.

Create a blank script, i called mine jeb-build-repo.sh

```sh
#!/bin/sh
sudo pacman -Sc
sudo repo-add -n /var/cache/pacman/pkg/cluster.repo.db.tar.gz /var/cache/pacman/pkg/*.pkg.tar.xz

# Make is executable
sudo chmod 755 /usr/bin/jeb-build-repo.sh
```
