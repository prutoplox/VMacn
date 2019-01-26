from mininet.topo import Topo
from mininet.link import TCIntf
from mininet.net import Mininet
from mininet.cli import CLI

from gobgp_api import BGPHelper

from router import SpineRouter, LeafRouter


class LeafSpineTopo(Topo):

    def __init__(self, *args, **params):

        self.__bgp_helper = BGPHelper.get_instance()

        Topo.__init__(self, *args, **params)

    def build(self):
        # Define constants which are used throughout this method
        linkBandwidth = 1
        numSpines = 3
        numLeafs = 5

        # Create lists which hold the routers and hosts which could be any number
        spineRouters = []
        leafRouters = []
        hosts = []

        # create the spine routers
        for x in range(numSpines):
            spineX = self.addSwitch("s" + x, role=SpineRouter)  # TODO proper config
            spineRouters.append(spineX)

        # create the leaf routers
        for x in range(numLeafs):
            leafX = self.addSwitch("l" + x, role=LeafRouter)  # TODO proper config
            leafRouters.append(leafX)

        # create the hosts, there is always 1 host per leaf
        for x in range(numLeafs):
            hostX = self.addHost("n" + x, ip='10.0.1.12/24',  # TODO proper config
                                 defaultRoute='via 10.0.1.254',
                                 role=1)

        # Building up a list which holds the spine/leaf combinations and connect all leafs with all spines
        # see https://stackoverflow.com/a/39064769
        leafSpineCombinations = [(leaf, spine) for leaf in leafRouters for spine in spineRouters]
        for spine, leaf in leafSpineCombinations:
            self.addLink(spine, leaf,
                         cls1=TCIntf, cls2=TCIntf,
                         intfName1=spine + '-' + leaf,
                         intfName2=leaf + '-' + spine,
                         params1={'ip': '10.0.2.254/24', 'bw': linkBandwidth},  # TODO proper ip
                         params2={'bw': linkBandwidth})

        # Connect all hosts with their respective leafs
        for host, leaf in zip(hosts, leafRouters):
            self.addLink(host, leaf,
                         cls1=TCIntf, cls2=TCIntf,
                         intfName1=host + '-' + leaf,
                         intfName2=leaf + '-' + host,
                         params1={'ip': '10.0.2.254/24', 'bw': linkBandwidth},  # TODO proper ip
                         params2={'bw': linkBandwidth})


def run():
    topo = LeafSpineTopo()
    net = Mininet(topo=topo)
    net.start()

    for node in net.topo.nodes():
        print(net[node].params['role'])

    CLI(net)
    net.stop()


if __name__ == '__main__':
    run()
