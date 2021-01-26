# L2 MAC Learning Controller

This l2switch should forward ARP requests/replies to a controller that learns
the MAC/port mappings and installs the appropriate table entries on the switch.

## Overview

`maclearning.p4app/main.py` sets up a topology with two hosts and a controller
connected to a switch. The controller, which runs on a normal Mininet host, is
connected to port 1, while the other hosts are on ports 2 and 3.

When host `h2` tries pinging `h3`, it first has to find the MAC address for
`h3`, which it does by broadcasting an ARP request. The switch should listen
for these ARP requests in order to learn which host (MAC address) is connected
to each port. The switch can then insert these MAC/port mappings in a L2 (MAC)
table to forward future packets.

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

In the switch, you must implement the parser, forward ARP requests to the
controller, decap packets received from the controller, and apply L2 (MAC)
forwarding. In the controller, you have to handle packets received from the
switch. They should be encapsulated in the `cpu_metadata` header, which is
already defined in both the data plane (`l2switch.p4`) and control plane
(`cpu_metadata.py`). This metadata header communicates packet information
(e.g., original ingress port) between the data and control plane.
