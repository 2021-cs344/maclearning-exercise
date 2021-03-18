# L2 MAC Learning

This l2switch should forward ARP requests/replies to a controller that learns
the MAC/port mappings and installs the appropriate table entries on the switch.

## Overview

`maclearning.p4app/main.py` sets up a topology with three hosts and a controller (CPU)
connected to a switch. The controller, which runs on a normal Mininet host, is
connected to port 1, while the other hosts are on ports 2, 3 and 4.

When host `h1` tries pinging `h2`, it first has to find the MAC address for
`h2`, which it does by broadcasting an ARP request. The switch should listen
for these ARP requests in order to learn which host (MAC address) is connected
to each port. When the switch receives an ARP packet from a host that it has
not yet learned, it should forward the packet to the controller. The controller
can then insert these MAC/port mappings in a L2 (MAC) table to forward future
packets. Furthermore, the controller should insert table entries in an ARP
cache table on the switch, which allows the switch to reply directly to future
ARP requests, without involving the control plane.
```
                   
                     +----- Add srcPort/MAC/IP -------- Send back to --+
                     |      mappings.                   data plane.    |
Control plane        |              \                                  |
.....................................\.................................................
Data plane           |                \                                |
                     |                 \                               |
                    No         Insert table entries.        Forward/bcast original pkt.
                     |                                                 |
                     |                                                 v
ARP pkt >---- Already learned? ----Yes---> If req, is it ----No-----> L2 table ------->
                                           in ARP cache?
                                                |
                                                |
                                               Yes
                                                |
                                                +----- Reply to req ------------------>
```

## Running

First, make sure you have p4app (which requires Docker):

    cd ~/
    git clone --branch rc-2.0.0 https://github.com/p4lang/p4app.git

Then run the p4app:

    ~/p4app/p4app run maclearning.p4app

This will print errors because of missing functionality in the P4 and
controller code.

## Instructions

You should implement the missing functionality in `l2switch.p4` and
`controller.py` (look for `TODO`s).

On the switch, you must:
- implement the parser;
- forward ARP packets (requests or responses) for new hosts to the controller;
- reply to ARP requests when possible (the dstIP was already learned);
- decap packets received from the controller; and
- apply L2 (MAC) forwarding.

In the controller, you have to handle packets received from the switch. They
should be encapsulated in the `cpu_metadata` header, which is already defined
in both the data plane (`l2switch.p4`) and control plane (`cpu_metadata.py`).
This metadata header communicates packet information (e.g., original ingress
port) between the data and control plane. The controller should maintain shadow
tables mapping MAC addresses to switch ports, and IP addresses to MAC addresses.
When the controller adds a new mapping to a shadow table, it should add a
coresponding entry to the table on the switch by calling
`self.sw.insertTableEntry(table_name='MyIngress.fwd_l2'...`.
