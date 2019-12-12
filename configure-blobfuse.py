#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import argparse
import requests
import os
import sys


class Program:
    config_file_path = "/etc/sysconfig/mnt-blobfuse"

    def __init__(self):
        self.parser = argparse.ArgumentParser(description="Create configuration file to mount blobfuse")
        self.parser.add_argument("kv_name", help="Key Vault name holding SAS token")
        self.parser.add_argument("secret_name", help="Secret Name holding SAS token")
        self.parser.add_argument("account_name", help="Storage Account to be specified in configuration")
        self.parser.add_argument("container_name", help="Container to be specifed in configuration")
        self.parser.add_argument("--bearer", help="(Optional) Use provided bearer token instead of pulling using service identity")
        self.options = self.parser.parse_args()

    def get_bearer(self):
        r = requests.get(
            "http://169.254.169.254/metadata/identity/oauth2/token",
            params={"api-version": "2018-02-01", "resource": "https://vault.azure.net"},
            headers={"Metadata": "true"},
        )
        if r.status_code == 200:
            return r.json()["access_token"]
        else:
            sys.stderr.write("Error: attempt to obtain MSI access token failed due to invalid HTTP status code %d\n" % r.status_code)
            sys.exit(1)

    def get_secret(self):
        r = requests.get(
            f"https://{self.options.kv_name}.vault.azure.net/secrets/{self.options.secret_name}",
            params={"api-version": "7.0"},
            headers={"Authorization": f"Bearer {self.options.bearer}", "Content-Type": "application/json"},
        )
        if r.status_code == 200:
            return r.json()["value"]
        else:
            sys.stderr.write("Error: attempt to obtain Azure Key Vault Secret failed due to invalid HTTP status code %d\n" % r.status_code)
            sys.exit(1)

    def write_config(self, token):
        if os.path.exists(config_file_path):
            os.remove(config_file_path)
        with open(config_file_path, "w+") as f:
            f.write(f"accountName {self.options.account_name}")
            f.write("\n")
            f.write(f"sasToken {token}")
            f.write("\n")
            f.write(f"containerName {self.options.container_name }")
            f.write("\n")

    def run(self):
        # Fetch the bearer token from MSI if not provided
        if self.options.bearer is None:
            self.options.bearer = self.get_bearer()
        self.write_config(self.get_secret())

if __name__ == "__main__":
    p = Program()
    p.run()