from p4app import P4Mininet
from mininet.topo import Topo
from controller import MacLearningController

class SingleSwitchTopo(Topo):
    def __init__(self, n, **opts):
        Topo.__init__(self, **opts)
        s1 = self.addSwitch('s1')
        cpu = self.addHost('cpu')
        self.addLink(cpu, s1, port2=1)
        for i in range(1, n+1):
            h = self.addHost('h%d'%i, ip="10.0.0.%d"%i, mac='00:00:00:00:00:%02x'%i)
            self.addLink(h, s1, port2=1+i)

# Add three hosts. Port 1 (h1) is reserved for the CPU.
N = 3

topo = SingleSwitchTopo(N)
net = P4Mininet(program='l2switch.p4', topo=topo, auto_arp=False)
net.start()

# Add a mcast group for all ports (except for the CPU port)
bcast_mgid = 1
s1 = net.get('s1')
s1.addMulticastGroup(mgid=bcast_mgid, ports=range(2, N+1))

# Send MAC bcast packets to the bcast multicast group
s1.insertTableEntry(table_name='MyIngress.fwd_l2',
        match_fields={'hdr.ethernet.dstAddr': ["ff:ff:ff:ff:ff:ff"]},
        action_name='MyIngress.set_mgid',
        action_params={'mgid': bcast_mgid})

# Start the MAC learning controller
cpu = MacLearningController(s1)
cpu.start()

h1, h2, h3 = net.get('h1', 'h2', 'h3')

print(h1.cmd('arping -c1 10.0.0.2'))
assert cpu.req_cnt == 1, "The ARP req from h1 is learned"
assert cpu.rep_cnt == 1, "The ARP rep from h2 is learned"

print(h3.cmd('arping -c1 10.0.0.1'))
assert cpu.req_cnt == 2, "The ARP req from h3 is learned"
assert cpu.rep_cnt == 1, "No more ARP replies shoud be sent to the data plane"

print(h3.cmd('arping -c1 10.0.0.2'))
assert cpu.req_cnt + cpu.rep_cnt == 3, "The data plane shouldn't receive any more ARP packets"

net.ping([h1, h2, h3])

# These table entries were added by the CPU:
s1.printTableEntries()
