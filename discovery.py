from topo_graph import TopologyGraph, NodeTypes, EdgeTypes
from gobgp_api import BGPHelper


class TopologyDiscovery(object):
  
  __instance = None
   
  @staticmethod
  def get_instance():
    if TopologyDiscovery.__instance is None:
      TopologyDiscovery()
    return TopologyDiscovery.__instance 

  def __init__(self):
    
    self.__bgp_helper = BGPHelper.get_instance()
    self.__topo_graph = TopologyGraph.get_instance()
    
    TopologyDiscovery.__instance = self
    
  def discover(self, num_router):
    '''TODO: Automatisierte Aufdeckung der BGP-Topologie bzw. der Leaf-Spine-Architektur'''
    pass
        
  def get_paths(self, source_prefix, destination_prefix):
    '''TODO: Bestimmung des Pfades/der Pfade zwischen zwei Netzen'''
    pass