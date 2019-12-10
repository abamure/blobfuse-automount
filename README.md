# blobfuse-automount

Method to automount blobfuse shares on system startup for RHEL 

## Overview

This method works by combining a fstab entry to mount a blobfuse share which depends on a systemd service to generate a blobfuse configuration file. The SAS token to mount the blobfuse share is stored inside an Azure KeyVault.

#TODO - Add diagram

## Setup Instructions

### Azure Setup

This method was built to run on an Azure RHEL 7+ VM. It assumes the VM has a system assigned Managed Identity, blobfuse installed, and python3 installed.

This method depends on an Azure Key Vault with a secret containing a SAS token with access to the container being mounted via blobfuse. The Key Vault needs to allow the VM access secrets via the Managed Identity.

### VM Setup

1. Install systemd service
    - Copy files from etc in this repository to etc in your system (recursively)
    - Fill out the configuration in /etc/sysconfig/configure-blobfuse
    - Execute `systemctl daemon-reload` and `systemctl enable configure-blobfuse`

2. Copy configure-blobfuse utility
```
cp configure-blobfuse.py /usr/local/bin/configure-blobfuse
chmod +x /usr/local/bin/configure-blobfuse
```

3. Ensure the pip package `requests` is installed on your system (using pip3 if necessary)

4. Create necessary mount points on your system
```
mkdir /mnt/<your-mount-point>
mkdir /mnt/resource/blobfusetmp
```

5. Setup your fstab file to auto-mount the container
- Add this line to your fstab file
```
/tmp/mount_blobfuse.sh   /mnt/loading            fuse     x-systemd.automount,x-systemd.requires=configure-blobfuse.service,_netdev,allow_other 0 0
```
- Copy `mount-blobfuse.sh` to the `/tmp` directory on your VM