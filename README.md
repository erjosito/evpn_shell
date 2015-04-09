# Simple EVPN shell v0.1

This is a simple Python module that offers a way to interactively poll, create or delete networks and tenants in a VXLAN environment with an EVPN control plane.

One challenge with EVPN is the amount of config that needs to be deployed to every leaf consistedly, for every network and every tenant that gets created. This project is a kind of proof concept of how easy it is using NXAPI (a REST API for Nexus switches) to build a central point from where deploying this config.

I have tested this with Nexus 9000 switches. With other Nexus the Python modules should work too, but slightly different (as documented by Chris Paggen). You can get the Python modules for Nexus here: https://github.com/datacenter/nexus9000/tree/master/nx-os/python/remote_client.

I am planning to post a quick demo video in youtube, I will put the link here when I have it.

WARNING: this is not designed to be used in a production network. In order to reach that stage some improvings should be done (like for example encrypting the credentials, amongst many other things). This is more a proof of concept, how the problem of complex configurations that need to be kept in sync across multiple devices can be solved.