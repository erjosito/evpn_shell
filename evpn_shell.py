#!/usr/bin/python
#
#     VXLAN EVPN Shell
#     v0.1
#
#     Jose Moreno (josemor@cisco.com)
#       April 2015
#
#     This program provides a CLI to manage a VXLAN EVPN
#       environment distributed on multiple switches. It
#       helps creating tenants and VLANs.
#     It is built on the REST API of NXOS (NX-API) and
#       the python modules on it (nxapi_utils).
#
#     This is NOT thought to be run in a production
#       network, there are some things that would need
#       to be improved (for example password encryption).
#
#
import sys
import cmd2
import json
# This file is supposed to be located in the remote_client folder
#  after unpacking the N9K Python SDK modules
#  (https://developer.cisco.com/fileMedia/download/0eb10f7e-b1ee-432a-9bef-680cb3ced417)
sys.path.append("./cisco")
sys.path.append("./utils")
from nxapi_utils import NXAPITransport 
from cisco.interface import Interface

############################
# Multi-switch class
############################
class multicli:
  switches={'spines':[], 'leafs':[]}

  # Runs a command on multiple switches (defined in the class variable
  #  multicli.switches) and returns the results in a bidimensional matrix
  #  where the first column contains the switch name, and the second the
  #  JSON output
  def mclid(self, switches, command):
    output=[]
    for switch in switches:
      target_url = "http://"+switch[1]+"/ins"
      myswitchname = switch[0]
      #print " --DEBUG: switch: %s" % myswitchname
      myusername = switch[2]
      mypassword = switch[3]
      NXAPITransport.init(target_url=target_url, username=myusername, password=mypassword)
      try:
        thisoutput = NXAPITransport.clid (command)
        output.append ( [myswitchname, thisoutput] )
      except:
        #print "Error sending command '%s' to switch %s" % (command, myswitchname)
        pass
    return output

  # Runs a command on multiple switches (defined in the class variable
  #  multicli.switches) and returns the results in a bidimensional matrix
  #  where the first column contains the switch name, and the second the
  #  raw output
  def mcli(self, switches, command):
    output=[]
    for switch in switches:
      target_url = "http://"+switch[1]+"/ins"
      myswitchname = switch[0]
      #print " --DEBUG: switch: %s" % myswitchname
      myusername = switch[2]
      mypassword = switch[3]
      NXAPITransport.init(target_url=target_url, username=myusername, password=mypassword)
      try:
        thisoutput = NXAPITransport.cli (command)
        output.append ( [myswitchname, thisoutput] )
      except:
        #print "Error sending command '%s' to switch %s" % (command, myswitchname)
        return False
    return output

  # Runs a command on multiple switches (defined in the class variable
  #  multicli.switches). No values are returned
  def mclic(self, switches, command):
    output=[]
    for switch in switches:
      target_url = "http://"+switch[1]+"/ins"
      myswitchname = switch[0]
      #print " --DEBUG: switch: %s" % myswitchname
      myusername = switch[2]
      mypassword = switch[3]
      NXAPITransport.init(target_url=target_url, username=myusername, password=mypassword)
      try:
        NXAPITransport.clic (command)
      except:
        #print "Error sending command '%s' to switch %s" % (command, myswitchname)
        pass

  # Runs a command on a single switch, taking the parameters out of the
  #  class variable 'switches'. Output as JSON
  def sclid (self, switchName, command):
    for switch in self.switches['leafs']:
      if switch[0] == switchName:
        target_url = "http://"+switch[1]+"/ins"
        username = switch[2]
        password = switch[3]
        NXAPITransport.init(target_url=target_url, username=username, password=password)
        try:
          output = NXAPITransport.clid (command)
        except:
          #print "Error sending command '%s' to switch %s" % (command, switchName)
          return False
        return output
    if not output:
      print "Switch %s not found!" % switchName
      return False

  # Runs a command on a single switch, taking the parameters out of the
  #  class variable 'switches'. Output as a raw string
  def scli (self, switchName, command):
    for switch in self.switches['leafs']:
      if switch[0] == switchName:
        target_url = "http://"+switch[1]+"/ins"
        username = switch[2]
        password = switch[3]
        NXAPITransport.init(target_url=target_url, username=username, password=password)
        try:
          output = NXAPITransport.cli (command)
        except:
          #print "Error sending command '%s' to switch %s" % (command, switchName)
          return False
        return output
    if not output:
      print "Switch %s not found!" % switchName
      return False


#####################################
# NXAPI init block (deprecated, initialization
#   happens now in the multicli class
#####################################
target_url = "http://10.1.51.155/ins"
username = "admin"
password = "cisco123"
NXAPITransport.init(target_url=target_url, username=username, password=password)


##################
# NXAPI funtions
##################

def createTenant (tenant, l3Vlan, l3Vni, bgpId):
   mymulticli = multicli()
   # Create VLAN for symmetric routing
   #print ("Creating VLAN " + str(l3Vlan))
   command="conf t ; vlan " + str(l3Vlan) + " ; name L3_VNI_" + tenant + " ; vn-segment " + str(l3Vni)
   try:
      mymulticli.mclic(multicli.switches['leafs'], command)
   except:
      print ("Error creating VLAN " + str(l3Vlan))
   # Create VRF
   #print ("Creating VRF " + tenant)
   command="conf t ; vrf context " + tenant + " ; vni " + str(l3Vni) + " ; rd auto ; address-family ipv4 unicast ; route-target import "+str(l3Vni)+":"+str(l3Vni)+" ; route-target import "+str(l3Vni)+":"+str(l3Vni)+" evpn ; route-target export "+str(l3Vni)+":"+str(l3Vni)+" ; route-target export "+str(l3Vni)+":"+str(l3Vni)+" evpn"
   try:
      mymulticli.mclic(multicli.switches['leafs'], command)
   except:
      print ("Error creating VRF " + tenant)
   # Create SVI for symmetric routing
   #print ("Creating SVI Vlan" + str(l3Vlan))
   command="conf t ; interface vlan " + str(l3Vlan) + " ; vrf member " + tenant + " ; no shutdown"
   try:
      mymulticli.mclic(multicli.switches['leafs'], command)
   except:
      print ("Error creating SVI Vlan" + str(l3Vlan))
   # Associate VNI to NVE interface
   #print "Associating VNI to interface vne1"
   command="conf t ; interface nve1 ; member vni " + str(l3Vni) + " associate-vrf"
   try:
      mymulticli.mclic(multicli.switches['leafs'], command)
   except:
      print ("Error associating VNI to interface nve1")
   # Add VRF to BGP
   #print "Inserting VRF into BGP"
   command="conf t ; router bgp "+str(bgpId)+" ; vrf " + tenant + " ; address-family ipv4 unicast ; advertise l2vpn evpn"
   try:
      mymulticli.mclic(multicli.switches['leafs'], command)
   except:
      print "Error inserting VRF into BGP %s" % str(bgpId)

def deleteTenant (tenant, l3Vlan, l3Vni, bgpId):
   mymulticli = multicli()
   # Add VRF to BGP
   #print "Removing VRF from BGP"
   command="conf t ; router bgp "+str(bgpId)+" ; no vrf " + tenant
   try:
      mymulticli.mclic(multicli.switches['leafs'], command)
   except:
      print "Error removing VRF '%s' from BGP %s" % (tenant, str(bgpId))
   # Remove VNI from NVE interface
   #print "Deassociating VNI from interface vne1"
   command="conf t ; interface nve1 ; no member vni " + str(l3Vni) + " associate-vrf"
   try:
      mymulticli.mclic(multicli.switches['leafs'], command)
   except:
      print ("Error deassociating VNI from interface nve1")
   # Remove SVI for symmetric routing
   #print ("Removing SVI Vlan" + str(l3Vlan))
   command="conf t ; no interface vlan " + str(l3Vlan)
   try:
      mymulticli.mclic(multicli.switches['leafs'], command)
   except:
      print ("Error removing SVI Vlan" + str(l3Vlan))
   # Remove VLAN for symmetric routing
   #print ("Removing VLAN " + str(l3Vlan))
   command="conf t ; no vlan " + str(l3Vlan)
   try:
      mymulticli.mclic(multicli.switches['leafs'], command)
   except:
      print ("Error removing VLAN " + str(l3Vlan))
   # Remove VRF
   #print ("Removing VRF " + tenant)
   command="conf t ; no vrf context " + tenant
   try:
      mymulticli.mclic(multicli.switches['leafs'], command)
   except:
      print ("Error removing VRF " + tenant)

# Create a VLAN definition
def createVlan (vlanId, vlanName, vni, ipAddress, mcastAddress, tenantName):
   mymulticli = multicli ()
   #Create VLAN
   #print ("Creating VLAN " + str(vlanId))
   command="conf t ; vlan " + str(vlanId) + " ; name " + vlanName + " ; vn-segment " + str(vni)
   try:
      mymulticli.mclic(multicli.switches['leafs'], command)
   except:
      print ("Error creating VLAN " + str(vlanId))
   # Create SVI
   #print ("Creating SVI Vlan" + str(l3Vlan))
   command="conf t ; interface vlan " + str(vlanId) + " ; vrf member " + tenantName + " ; ip address " + ipAddress + " ; fabric forwarding mode anycast-gateway ; no shutdown"
   try:
      mymulticli.mclic(multicli.switches['leafs'], command)
   except:
      print ("Error creating SVI Vlan" + str(vlanId)+" with IP address "+ipAddress+" on VRF "+tenantName)
   # Add to interface NVE1
   #print ("Adding VNI to VNE1")
   command="conf t ; interface nve1 ; member vni " + str(vni) + " ; suppress-arp ; mcast-group " + mcastAddress
   try:
      mymulticli.mclic(multicli.switches['leafs'], command)
   except:
      print ("Error adding VNI to NVE1")
   # Add to EVPN
   #print ("Adding VNI to EVPN")
   command="conf t ; evpn ; vni " + str(vni) + " l2 ; rd auto ; route-target import auto ; route-target export auto"
   try:
      mymulticli.mclic(multicli.switches['leafs'], command)
   except:
      print ("Error adding VNI to EVPN")

# Create SVI
def createSVI (vlanId, tenant, ipAddress):
   command="conf t ; interface vlan " + str(vlanId) + " ; vrf member " + tenant + " ; ip address " + ipAddress + " ; fabric forwarding mode anycast-gateway ; no shutdown"
   #print ("Creating SVI Vlan" + str(vlanId))
   try:
      mymulticli = multicli ()
      mymulticli.mclic(multicli.switches['leafs'], command)
   except:
      print ("Error creating SVI Vlan" + str(vlanId))

# Delete a VLAN (only the L2 definition)
def deleteVlan (vlanId, vni):
   mymulticli = multicli ()
   # Remove from EVPN
   #print ("Removing VNI from EVPN")
   command="conf t ; evpn ; no vni " + str(vni) + " l2"
   try:
      mymulticli.mclic(multicli.switches['leafs'], command)
   except:
      print ("Error removing VNI from EVPN")
   # Remove from interface NVE1
   #print ("Removing VNI from VNE1")
   command="conf t ; interface nve1 ; no member vni " + str(vni)
   try:
      mymulticli.mclic(multicli.switches['leafs'], command)
   except:
      print ("Error removing VNI from NVE1")
   # Remove SVI
   #print ("Removing SVI Vlan" + str(l3Vlan))
   command="conf t ; no interface vlan " + str(vlanId)
   try:
      mymulticli.mclic(multicli.switches['leafs'], command)
   except:
      print ("Error removing SVI Vlan" + str(vlanId))
   #Remove VLAN
   #print ("Removing VLAN " + str(vlanId))
   command="conf t ; no vlan " + str(vlanId)
   try:
      mymulticli.mclic(multicli.switches['leafs'], command)
   except:
      print ("Error removing VLAN " + str(vlanId))

# Delete an SVI
def deleteSVI (vlanId):
   command="config t ;no interface vlan " + str(vlanId)
   #print ("Deleting SVI Vlan" + str(vlanId))
   try:
      mymulticli=multicli()
      mymulticli.mclic(multicli.switches['leafs'], command)
   except:
      print ("Error deleting SVI Vlan" + str(vlanId) + ". SVI did not exist?")

# New version to get the new VLANs defined on all leafs
def getVlan ():
    command="show vlan"
    try:
      mymulticli = multicli()
      outputs=mymulticli.mclid(multicli.switches['leafs'], command)
    except:
      print "Error getting VLAN information"
      return None
    if not outputs:
      print "No VLAN information could be retrieved"
      return False
    print "SWITCH       VLAN ID     VLAN Name        VNI    Tenant         IP Address"
    print "======       =======     =========        ===    ======         =========="
    for output in outputs:
      try:
        vlans=json.loads(output[1])
      except:
        print "Error processing JSON output '%s'" % output[1]
        return None
      for vlan in vlans['TABLE_vlanbrief']['ROW_vlanbrief']:
        switchName=output[0]
        vlanId=vlan['vlanshowbr-vlanid-utf']
        vlanName=vlan['vlanshowbr-vlanname']
        vni =getVNI (switchName, vlanId)
        tenantName=getTenant (switchName, vlanId)
        ipAddress=getSviIp (switchName, vlanId)
        print ('{:<13}{:7d}     {:<16} {:<7}{:<15}{:<15}'.format(switchName,int(vlanId), vlanName, vni, tenantName, ipAddress))

# Returns the VNI corresponding to a specific VLAN, on a specific switch
def getVNI (switchName, vlanId):
      command="show vlan id " + str(vlanId) + " vn-segment"
      mymulticli = multicli()
      output=mymulticli.sclid(switchName, command)
      try:
         segment=json.loads(output)
         vni=segment['TABLE_seginfoid']['ROW_seginfoid']['vlanshowinfo-segment-id']
      except:
         vni=None
      return vni

# In construction
# Returns the tenant under which a VLAN is configured in a specific switch
def getTenant (switchName, vlanId):
      command="show vrf interface vlan " + str(vlanId)
      mymulticli = multicli()
      output=mymulticli.sclid(switchName, command)
      try:
         segment=json.loads(output)
         tenantName=segment['TABLE_if']['ROW_if']['vrf_name']
      except:
         tenantName=None
      return tenantName

# In construction
# Returns the VNI corresponding to a specific VLAN, on a specific switch
def getSviIp (switchName, vlanId):
      command="show ip interface vlan " + str(vlanId)
      mymulticli = multicli()
      output=mymulticli.sclid(switchName, command)
      try:
         segment=json.loads(output)
         ipAddress=segment['TABLE_intf']['ROW_intf']['prefix']
         ipAddress=ipAddress+"/"+segment['TABLE_intf']['ROW_intf']['masklen']
      except:
         ipAddress=None
      return ipAddress

# In construction
# Returns a list of tenants configured across all switches
def getTenants ():
    command="show runn | i 'member vni'"
    try:
      mymulticli = multicli()
      outputs=mymulticli.mcli(multicli.switches['leafs'], command)
    except:
      print "Error getting Tenant information"
      return None
    if not outputs:
      print "No Tenant information could be retrieved"
      return False
    print "Switch       Tenant      L3 VLAN ID       L3 VNI"
    print "======       ======      ==========       ======"
    for output in outputs:
      switchName=output[0]
      lines=output[1].split('\n')
      for line in lines:
        words=line.split()
        try:
          vni=words[2]
          vlanId=getVlanFromVni (switchName, vni)
          tenantName=getTenant (switchName, vlanId)
          print ("{:<13}{:<12}{:<17}{}".format(switchName, tenantName, vlanId, vni))
        except:
          #print "No VNI found in string '%s'" % line
          pass

# In construction
# Returns a list of tenants configured across all switches
def getVlanFromVni (switchName, vni):
    command="show vxlan"
    try:
      mymulticli = multicli()
      output=mymulticli.scli(switchName, command)
    except:
      print "Error getting VXLAN information"
      return None
    if not output:
      print "No VXLAN information could be retrieved"
      return False
    #print " *DEBUG* output = '%s'" % output
    lines=output.split('\n')
    for line in lines:
      words=line.split()
      try:
        thisVlanId=words[0]
        thisVni=words[1]
        #print " *DEBUG* VlanID = '%s', VNI = '%s'" % (thisVlanId, thisVni)
        if thisVni == vni:
          return thisVlanId
      except:
        #print "No VNI found in string '%s'" % line
        pass


############################
# Shell
############################

class evpnCli(cmd2.Cmd):
   '''Welcome to Simple VXLAN EVPN CLI v0.1'''
   prompt='evpn# '
   intro='Simple VXLAN EVPN CLI'

   # Add a new switch
   def do_add_switch (self, line):
      '''Add a switch to the list of managed devices
      Syntax: add_switch leaf|spine <switch_name> <switch_ip> <username> <password>
      Example:
              add_switch leaf n9k-1 10.1.51.155 admin cisco123'''
      args=line.split()
      if len(args)<5:
        print "Not enough arguments provided, please type 'help add_switch' for information on this command"
        return False 
      try:
        switchType=args[0]
        switchName=args[1]
        switchIp=args[2]
        userName=args[3]
        password=args[4]
      except:
        print "Invalid parameters. Type 'help add_switch' for help"
        return False
      if switchType == 'leaf':
        multicli.switches['leafs'].append ( [switchName, switchIp, userName, password] )
      elif switchType == 'spine':
        multicli.switches['spines'].append ( [switchName, switchIp, userName, password] )
      else:
        print "Invalid switch type %s, please select either 'leaf' or 'spine'" % switchType
        return False

   # Display the switches configred
   def do_show_switches (self, line):
     '''Show the switches configured in the system
     Example:  show_switches'''
     print "Type       Name         IP address        Username       Password"
     print "====       ====         ==========        ========       ========"
     for switch in multicli.switches['leafs']:
       print ('Leaf       {:<13}{:<18}{:<15}{:<15}'.format(switch[0], switch[1], switch[2], switch[3]))
     for switch in multicli.switches['spines']:
       print ('Spine      {:<13}{:<18}{:<15}{:<15}'.format(switch[0], switch[1], switch[2], switch[3]))

   # Save switch config to a file
   def do_save_switches (self, filename):
     '''Save the switch definitions to a file in JSON format
     Example: save_switches my_lab.conf'''
     jsonstring = json.dumps(multicli.switches)
     try:
       configfile=open(filename, "w")
       configfile.write (jsonstring)
       configfile.close()
     except:
       print "Error writing to %s" % filename

   # Load switch config from a file
   def do_load_switches (self, filename):
      '''Load the switch definitions from a file in JSON format (previously saved with save_switches)
      Example: load_switches my_lab.conf'''
      try:
        with open(filename) as json_file:
          multicli.switches = json.load(json_file)
        # Update prompt with filename (without exception)
        fileshort=filename.split(".")[0]
        self.prompt = fileshort+"# "
      except:
       print "Error loading data from %s" % filename
  
   # Add a new VLAN (with SVI, NVI, etc) 
   def do_add_vlan (self, line):
     '''Create one VLAN, including SVI, nve interface definition and evpn definition
     Syntax:  add_vlan <vlan_id> <vlan_name> <vni> <anycast_gw_address> <tenant> <mcast_address>
     Example:
            add_vlan 300 VLAN0300 30300 192.168.30.1/24 Tenant3 224.1.1.30'''
     args=line.split()
     if len(args)<6:
        print "Not enough arguments provided, please type 'help add_vlan' for information on this command"
        return False
     try:
        vlanId=int(args[0])
        vlanName=args[1]
        vni=int(args[2])
        sviIp=args[3]
        tenant=args[4]
        mcast=args[5]
     except:
        print "Invalid parameters. Type 'help add_vlan' for help"
        return False
     createVlan (vlanId,vlanName,vni,sviIp,mcast,tenant)

   # Create a new tenant
   def do_add_tenant (self, line):
     '''Create one tenant, including L3 VLAN/SVI, nve interface definition and evpn definition
     Syntax:  add_tenant <tenant_name> <l3_vlan_id> <l3_vni> <bgp_id>
     Example:
            add_tenant tenant1 3900 39000 100'''
     args=line.split()
     if len(args)<4:
        print "Not enough arguments provided, please type 'help add_tenant' for information on this command"
        return False
     try:
        tenantName=args[0]
        l3VlanId=int(args[1])
        l3Vni=int(args[2])
        bgpId=int(args[3])
     except:
        print "Invalid parameters. Type 'help add_tenant' for help"
        return False
     createTenant (tenantName, l3VlanId, l3Vni, bgpId)

   def do_delete_tenant(self, line):
     '''Delete one tenant, including L3 VLAN/SVI, nve interface definition and evpn definition
     Syntax:  delete_tenant <tenant_name> <l3_vlan_id> <l3_vni> <bgp_id>
     Example:
            delete_tenant tenant1 3900 39000 100'''
     args=line.split()
     if len(args)<4:
        print "Not enough arguments provided, please type 'help delete_tenant' for information on this command"
        return False
     try:
        tenantName=args[0]
        l3VlanId=int(args[1])
        l3Vni=int(args[2])
        bgpId=int(args[3])
     except:
        print "Invalid parameters. Type 'help delete_tenant' for help"
        return False
     deleteTenant (tenantName, l3VlanId, l3Vni, bgpId)

   def do_delete_vlan(self, line):
     '''Remove one VLAN, including SVI, nve interface definition and evpn definition
     Syntax:  delete_vlan <vlan_id> <vni>
     Example:
            delete_vlan 300 30300'''
     args=line.split()
     if len(args)<2:
        print "Not enough arguments provided, please type 'help add_vlan' for information on this command"
        return False
     try:
        vlanId=int(args[0])
        vni=int(args[1])
     except:
        print "Invalid parameters. Type 'help add_vlan' for help"
        return False
     deleteVlan (vlanId,vni)

   def do_get_vlans (self, arg):
     '''Get a VLAN list
     Example: get_vlans'''
     getVlan ()

   def do_get_tenants (self, arg):
     '''Get a Tenant list
     Example: get_tenants'''
     getTenants ()

   def do_quit (self, arg):
     '''Exit VXLAN EVPN CLI'''
     print ('Bye!')
     return True
   def do_exit (self, arg):
     '''Exit VXLAN EVPN CLI'''
     print ('Bye!')
     return True

   def default (self, arg):
     print ('What???')

   def emptyline(self):
     return None

if __name__ == '__main__':
   evpnCli().cmdloop()
