from enum import IntEnum
from py2neo import Node, Relationship


# Typen von Graph-Knoten
class NodeTypes(IntEnum):
  NETWORK = 0
  LEAF_ROUTER = 1
  SPINE_ROUTER = 2


# Typen von Graph-Kanten
class EdgeTypes(IntEnum):
  NETWORK_LINK = 0
  BGP_PEERING = 1


class TopologyGraph(object):

  __NODE_TYPES = ['NETWORK', 'LEAF_ROUTER', 'SPINE_ROUTER']
  __EDGE_TYPES = ['NETWORK_LINK', 'BGP_PEERING']

  __instance = None
   
  @staticmethod
  def get_instance():
    if TopologyGraph.__instance is None:
      TopologyGraph()
    return TopologyGraph.__instance  

  def __init__(self):
    
    # {node_id: Node, ...} (Node => py2neo)
    self.__nodes = {}
    # {edge_id: Relationship, ...} (Relationship => py2neo)
    self.__edges = {}
    
    TopologyGraph.__instance = self

  # Konstruktion eines Graph-Knotens
  # node_type: Typ des Graph-Knotens (siehe NodeTypes)
  # node_id: Eindeutige ID des Graph-Knotens
  # properties: Eigenschaften des Graph-Knotens (Dictionary)
  # Ergebnis der Konstruktion: Erzeugter Knoten (Node)
  def create_node(self, node_type, node_id, properties=None):
    if properties is None:
        properties = {}

    node = Node(self.__NODE_TYPES[node_type.value],
                node_id=node_id)

    for k, v in properties.items():
      node[k] = v
      # if isinstance(v, (list, dict)):
      #    node[k] = str(v)
      # else:
      #    node[k] = str(v)

    self.__nodes[node_id] = node

    return node

  # Abfrage der Existenz eines Graph-Knotens
  # node_id: Eindeutige ID des Graph-Knotens
  # Ergebnis der Abfrage: True/False
  def exists_node(self, node_id):
    return node_id in self.__nodes.keys()

  # Abfrage von Graph-Knoten
  # nodes: (a) nichts 
  #        oder
  #        (b) Liste mit IDs der Graph-Knoten (node_id)
  #        oder
  #        (c) ID des Graph-Knotens (node_id)
  # Ergebnis der Abfrage: (a) Alle Graph-Knoten (Dictionary)
  #                       oder
  #                       (b) Teil aller Graph-Knoten (Dictionary)
  #                       oder
  #                       (c) Graph-Knoten 
  def get_nodes(self, nodes=None):
    if nodes is None:
      return self.__nodes
    
    if not isinstance(nodes, list):
      return self.__nodes.get(nodes)
    
    return {k:v for k, v in self.__nodes.items() if k in nodes}

  # Loeschen von Graph-Knoten
  # nodes: (a) Liste mit IDs der Graph-Knoten (node_id)
  #        oder
  #        (b) ID des Graph-Knotens (node_id)
  def delete_nodes(self, nodes):
    if not isinstance(nodes, list):
      self.__nodes.pop(nodes)
    else:
      self.__nodes = {k:v for k, v in self.__nodes.items() if k not in nodes}

  # Konstruktion einer gerichteten Graph-Kante
  # node1: Graph-Knoten 1 (Node)
  # node2: Graph-Knoten 2 (Node)
  # edge_type: Typ der Graph-Kante (siehe EdgeTypes)
  # properties: Eigenschaften der Graph-Kante (Dictionary)
  # Ergebnis der Konstruktion: Erzeugten Kante (Relationship)    
  def create_unidirectional_edge(self, node1, node2, edge_type, properties=None):
    if node1['node_id'] + '-' + node2['node_id'] in self.__edges.keys():
      return None
    
    if properties is None:
        properties = {}

    edge_id = node1['node_id'] + '-' + node2['node_id']
    edge = Relationship(node1,
                        self.__EDGE_TYPES[edge_type.value],
                        node2, edge_id=edge_id)

    for k, v in properties.items():
      edge[k] = v
      # if isinstance(v, (list, dict)):
      #    edge[k] = str(v)
      # else:
      #    edge[k] = str(v)

    self.__edges[edge_id] = edge

    return edge

  # Konstruktion einer ungerichteten Graph-Kante (2x gerichtete Kante)
  # node1: Graph-Knoten 1 (Node)
  # node2: Graph-Knoten 2 (Node)
  # edge_type: Typ der Graph-Kante (siehe EdgeTypes)
  # properties: Eigenschaften der Graph-Kante (Dictionary)
  # Ergebnis der Konstruktion: Tupel mit erzeugten Kanten (Relationship,Relationship)
  def create_bidirectional_edge(self, node1, node2, edge_type, properties=None):
    if node1['node_id'] + '-' + node2['node_id'] in self.__edges.keys():
      return None
    
    if properties is None:
        properties = {}

    return (self.create_unidirectional_edge(node1, node2, edge_type, properties),
            self.create_unidirectional_edge(node2, node1, edge_type, properties))

  # Abfrage der Existenz einer Graph-Kante
  # edge_id: Eindeutige ID der Graph-Kante
  # Ergebnis der Abfrage: True/False
  def exists_edge(self, edge_id):
    return edge_id in self.__edges.keys()

  # Abfrage von Graph-Kanten
  # edges: (a) nichts 
  #        oder
  #        (b) Liste mit IDs der Graph-Kanten (edge_id)
  #        oder
  #        (c) ID der Graph-Kante (edge_id)
  # Ergebnis der Abfrage: (a) Alle Graph-Kanten (Dictionary)
  #                       oder
  #                       (b) Teil aller Graph-Kanten (Dictionary)
  #                       oder
  #                       (c) Graph-Kante
  def get_edges(self, edges=None):
    if edges is None:
      return self.__edges
    
    if not isinstance(edges, list):
      return self.__edges.get(edges)
    
    return {k:v for k, v in self.__edges.items() if k in edges}

  # Loeschen von Graph-Kanten
  # edges: (a) Liste mit IDs der Graph-Kanten (edge_id)
  #        oder
  #        (b) ID der Graph-Kante (edge_id)  
  def delete_edges(self, edges):
    if not isinstance(edges, list):
      self.__edges.pop(edges)
    else:
      self.__edges = {k:v for k, v in self.__edges.items() if k not in edges}

  # Abfrage der Graph-Struktur (Knoten und Kanten)
  # Ergebnis der Abfrage: Tupel mit Graph-Knoten und Kanten
  def get_graph(self):
    return (self.__nodes, self.__edges)

  def match_node_type_to_string(self, node_type):
    return self.__NODE_TYPES[node_type.value]

  def match_edge_type_to_string(self, edge_type):
    return self.__EDGE_TYPES[edge_type.value]