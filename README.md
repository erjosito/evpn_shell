# Simple EVPN shell v0.2

This is a simple Python module that offers a way to interactively poll, create or delete networks and tenants in a VXLAN environment with an EVPN control plane.

One challenge with EVPN is the amount of config that needs to be deployed to every leaf consistedly, for every network and every tenant that gets created. This project is a kind of proof concept of how easy it is using NXAPI (an API for Nexus switches) to build a central point from where deploying this config.

I have tested this with Nexus 9000 switches. With other Nexus the Python modules should work too, but slightly different (as documented by Chris Paggen). You can get the Python modules for Nexus here: https://github.com/datacenter/nexus9000/tree/master/nx-os/python/remote_client.

Here you can see a demo of how this thing looks like, without you having to install anything: https://youtu.be/9T1qs-lBGqg

INSTALLATION: download and unpack the NXAPI libraries in https://developer.cisco.com/fileMedia/download/0eb10f7e-b1ee-432a-9bef-680cb3ced417. This will create a “remote_client” directory. Download the evpn_shell.py script into that directory, and run it from there. Install the required Python modules if missing (cmd2, sys, json, datetime). You will probably need to install the lxml and pexpect Python modules, so that the NXAPI libraries work correctly.

WARNING: this is not designed to be used in a production network. In order to reach that stage some improvings should be done (like for example encrypting the credentials, amongst many other things). This is more a proof of concept, how the problem of complex configurations that need to be kept in sync across multiple devices can be solved.

v0.2:
 * Added per switch creation/deletion
 * Debug log (defaults to logging to a file)
 * getTenants bug fixed
 * Consolidated switch list (instead of one for leafs and another one for spines)
