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
    '''TODO: Konstruktion der Beispiel-Topologie'''
    pass

  
def run():
  '''TODO: Ausführung der Beispiel-Topologie inkl. automatisierter BGP-Konfiguration'''
  pass


if __name__ == '__main__':
  run()