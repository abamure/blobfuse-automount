# blobfuse-automount

Method to automount blobfuse shares on system startup for RHEL 

## Overview

This method works by combining a systemd mount entry to mount a blobfuse share which depends on a systemd service to generate a blobfuse configuration file. The SAS token to mount the blobfuse share is stored inside an Azure KeyVault.

#TODO - Add diagram

## Setup Instructions

### Azure Setup

This method was built to run on an Azure RHEL 7+ VM. It assumes the VM has a system assigned Managed Identity, blobfuse installed, and python3 installed.

This method depends on an Azure Key Vault with a secret containing a SAS token with access to the container being mounted via blobfuse. The Key Vault needs to allow the VM access secrets via the Managed Identity.

See [this site](https://docs.microsoft.com/en-us/azure/hdinsight/hdinsight-storage-sharedaccesssignature-permissions#create-a-stored-policy-and-sas) for information about creating a SAS token scoped to a single container.

### VM Setup

1. Copy the necessary etc files to your system
```
cp {,/}etc/systemd/system/configure-blobfuse.service
cp {,/}etc/systemd/system/mnt-blobfuse.automount
cp {,/}etc/systemd/system/mnt-blobfuse.mount
cp {,/}etc/sysconfig/configure-blobfuse
```

2. Update the configuration file in `/etc/sysconfig/configure-blobfuse` to match your Azure resources

3. Enable the systemd units
```
systemctl daemon-reload
systemctl enable configure-blobfuse
systemctl enable mnt-blobfuse.automount
```

4. Copy configure-blobfuse utility, mount blobfuse script, and create empty configuration file
```
cp configure-blobfuse.py /usr/local/bin/configure-blobfuse
chmod +x /usr/local/bin/configure-blobfuse
cp mount-blobfuse.sh /usr/local/bin/mount-blobfuse
chmod +x /usr/local/bin/mount-blobfuse
touch /etc/sysconfig/mnt-blobfuse
chmod 0600 /etc/sysconfig/mnt-blobfuse
```

5. Ensure the pip package `requests` is installed on your system (using pip3 if necessary)

6. Create necessary mount points on your system
```
mkdir /mnt/blobfuse
mkdir /mnt/resource/blobfusetmp
```

---

Alternatively to using the `.mount` and `.automount` units, you can mount in your `/etc/fstab` file instead
```
/usr/local/bin/mount-blobfuse   /mnt/blobfuse            fuse     x-systemd.automount,x-systemd.requires=configure-blobfuse.service,_netdev,allow_other 0 0
```
