import grpc
import gobgp_pb2_grpc as gobgp_grpc
import gobgp_pb2 as gobgp

from cgopy import _PATTRS_CAP, Path, Buf, protobuf_obj_attrs, libgobgp 
from ctypes import create_string_buffer, c_int, c_char, cast, pointer, POINTER

from ipaddress import IPv4Address
import subprocess
import json


class BGPHelper(object):

  __GRPC_DEFAULT_PORT = '50051'
  __GRPC_REQUEST_TIMEOUT = 10
  
  __AFI_IP = 1
  __SAFI_UNICAST = 1
  __FAMILY = __AFI_IP << 16 | __SAFI_UNICAST

  __instance = None

  @staticmethod
  def get_instance():
    if BGPHelper.__instance is None:
      BGPHelper()
    return BGPHelper.__instance  

  def __init__(self):

    BGPHelper.__instance = self

  def __establish_channel(self, router_mgmt_ip, port):
    return gobgp_grpc.GobgpApiStub(grpc.insecure_channel(router_mgmt_ip + ':' + port))
  
  # Konfiguration globaler BGP-Parameter (AS und Router-ID) sowie Starten des BGP-Speakers
  # router_mgmt_ip: Management-IP-Adresse des BGP-Routers
  # as_num: AS, in welchem sich der BGP-Router befindet
  # router_id: Router-ID des BGP-Routers
  # peerings: Liste der BGP-Peers:
  #           [{'local_address': <Peering-IP-Adresse des lokalen BGP-Routers>, 
  #             'local_as': <AS des lokalen BGP-Routers>, 
  #             'peer_address': <Peering-IP-Adresse des benachbarten BGP-Routers>,
  #             'peer_as': <AS des benachbarten BGP-Routers>}])  
  def configure_bgp_speaker(self, router_mgmt_ip, as_num, router_id, peerings, port=__GRPC_DEFAULT_PORT):
    subprocess.Popen('/bin/ping -c3 {}'.format(router_mgmt_ip), shell=True,
                     stdout=subprocess.PIPE, stderr=subprocess.PIPE).wait()
    
    node_channel = self.__establish_channel(router_mgmt_ip, port)

    request = gobgp.StartServerRequest()

    setattr(getattr(request, 'global'), 'as', as_num)
    setattr(getattr(request, 'global'), 'router_id', router_id)
    for listen_address in set([peer['local_address'].split('/')[0] for peer in peerings]):
      getattr(request, 'global').listen_addresses.append(listen_address)
    getattr(request, 'global').listen_addresses.append(router_mgmt_ip)      
    setattr(getattr(request, 'global'), 'use_multiple_paths', True)

    node_channel.StartServer(request, self.__GRPC_REQUEST_TIMEOUT)
    
  # Konfiguration von BGP-Peerings
  # router_mgmt_ip: Management-IP-Adresse des BGP-Routers
  # peerings: Liste der BGP-Peers:
  #           [{'local_address': <Peering-IP-Adresse des lokalen BGP-Routers>, 
  #             'local_as': <AS des lokalen BGP-Routers>, 
  #             'peer_address': <Peering-IP-Adresse des benachbarten BGP-Routers>,
  #             'peer_as': <AS des benachbarten BGP-Routers>}])
  def configure_bgp_peers(self, router_mgmt_ip, peerings,
                          port=__GRPC_DEFAULT_PORT):
    subprocess.Popen('/bin/ping -c3 {}'.format(router_mgmt_ip), shell=True,
                     stdout=subprocess.PIPE, stderr=subprocess.PIPE).wait()
    
    node_channel = self.__establish_channel(router_mgmt_ip, port)
    
    for peering in peerings:
      peer = gobgp.Peer()
      peer.conf.neighbor_address = peering['peer_address'].split('/')[0]
      peer.conf.peer_as = peering['peer_as']

      node_channel.AddNeighbor(gobgp.AddNeighborRequest(peer=peer))

  # Loeschen von BGP-Peerings
  # router_mgmt_ip: Management-IP-Adresse des BGP-Routers
  # peer_addresses: Liste von IP-Adressen der BGP-Peers
  def delete_bgp_peers(self, router_mgmt_ip, peer_addresses,
                       port=__GRPC_DEFAULT_PORT):
    subprocess.Popen('/bin/ping -c3 {}'.format(router_mgmt_ip), shell=True,
                     stdout=subprocess.PIPE, stderr=subprocess.PIPE).wait()
    
    node_channel = self.__establish_channel(router_mgmt_ip, port)
    
    for peer_address in peer_addresses:
      node_channel.DeleteNeighbor(gobgp.DeleteNeighborRequest(address=peer_address))
  
  # Abfrage globaler BGP-Parameter (AS und Router-ID)
  # router_mgmt_ip: Management-IP-Adresse des BGP-Routers
  # Ergebnis der Abfrage: {'as': <AS>, 'router_id': Router-ID}
  def get_bgp_speaker_configuration(self, router_mgmt_ip, port=__GRPC_DEFAULT_PORT):
    subprocess.Popen('/bin/ping -c3 {}'.format(router_mgmt_ip), shell=True,
                     stdout=subprocess.PIPE, stderr=subprocess.PIPE).wait()

    node_channel = self.__establish_channel(router_mgmt_ip, port)

    bgp_config = node_channel.GetServer(gobgp.GetServerRequest(), self.__GRPC_REQUEST_TIMEOUT)
    
    return {'as': str(getattr(getattr(bgp_config, 'global'), 'as')),
            'router_id': str(getattr(getattr(bgp_config, 'global'), 'router_id'))}

  # Abfrage der BGP-Peers
  # router_mgmt_ip: Management-IP-Adresse des BGP-Routers
  # Ergebnis der Abfrage: Liste der BGP-Peerings:
  #   [{'local_address': <Peering-IP-Adresse des lokalen BGP-Routers>, 
  #     'local_as': <AS des lokalen BGP-Routers>, 
  #     'peer_address': <Peering-IP-Adresse des benachbarten BGP-Routers>,
  #     'peer_as': <AS des benachbarten BGP-Routers>,
  #     'peering_type': <Typ des BGP-Peerings>,
  #     'state': <Status des BGP-Peerings>}]) 
  def get_bgp_peers(self, router_mgmt_ip, port=__GRPC_DEFAULT_PORT):
    subprocess.Popen('/bin/ping -c3 {}'.format(router_mgmt_ip), shell=True,
                     stdout=subprocess.PIPE, stderr=subprocess.PIPE).wait()
    
    node_channel = self.__establish_channel(router_mgmt_ip, port)
    
    bgp_peers = node_channel.GetNeighbor(gobgp.GetNeighborRequest(), self.__GRPC_REQUEST_TIMEOUT)

    local_as = self.get_bgp_speaker_configuration(router_mgmt_ip, port)['as']
    peers = []    
    
    for peer in bgp_peers.peers:
      
      if int(peer.conf.neighbor_address.split('.')[3]) % 2 == 0:
        local_address = IPv4Address(peer.conf.neighbor_address) - 1
        
      else:
        local_address = IPv4Address(peer.conf.neighbor_address) + 1
      
      # alternatively use IPv4Address objects
      peers.append({'local_address': str(local_address),
                    'local_as': str(local_as),
                    'peer_address': str(peer.conf.neighbor_address),
                    'peer_as': str(peer.conf.peer_as),
                    'peering_type': 'eBGP',  # peer.info.peer_type
                    'state': str(peer.info.bgp_state)})
      
    return peers

  # Abfrage der BGP-Routen
  # router_mgmt_ip: Management-IP-Adresse des BGP-Routers
  # Ergebnis der Abfrage: Liste der BGP-Routen:
  #   {'prefix': {'prefix': <IP-Prefix der BGP-Route>,
  #               'nexthop': <Next-Hop-IP der BGP-Route>, 
  #               'as_path': <AS-Pfad der BGP-Route>}})   
  def get_bgp_routes(self, router_mgmt_ip, port=__GRPC_DEFAULT_PORT):
    subprocess.Popen('/bin/ping -c3 {}'.format(router_mgmt_ip), shell=True,
                     stdout=subprocess.PIPE, stderr=subprocess.PIPE).wait()    
    
    node_channel = self.__establish_channel(router_mgmt_ip, port)
    
    request = gobgp.GetRibRequest(table=gobgp.Table(family=self.__FAMILY, type=gobgp.GLOBAL))
    
    bgp_routes = node_channel.GetRib(request, self.__GRPC_REQUEST_TIMEOUT)
    
    routes = {}
    
    for route in bgp_routes.table.destinations:
      # paths = [path for path in route.paths if path.best]
      routes[str(route.prefix)] = []
      for path in route.paths:
        path_attributes = self.__decode_serialized_path_attributes(path)
        try:
          as_path = path_attributes[2]['as_paths'][0]['asns']
        except:
          as_path = []
        # alternatively use IPv4Network and IPv4Address objects
        routes[str(route.prefix)].append({'prefix': str(route.prefix),
                                          'nexthop': str(path_attributes[3]['nexthop']),
                                          'as_path': as_path})
      min_as_path_length = min([len(r['as_path']) for r in routes[str(route.prefix)]])
      routes[str(route.prefix)] = [r for r in routes[str(route.prefix)] if len(r['as_path']) == min_as_path_length] 
       
    return routes 

  def __decode_serialized_path_attributes(self, serialized_path):
    path = Path()
    path_attributes = []
    for attr in protobuf_obj_attrs(serialized_path):
        if attr == "nlri":  
            path.nlri = Buf()
            nlri_val = getattr(serialized_path, attr)
            nlri_val_buf = create_string_buffer(nlri_val)
            path.nlri.value = cast(nlri_val_buf, POINTER(c_char))
            path.nlri.len = c_int(len(nlri_val))
        elif attr == "pattrs": 
            for pattr in getattr(serialized_path, attr):
                path_attribute = Buf()
                path_attribute_val = pattr
                path_attribute_val_buf = create_string_buffer(path_attribute_val)
                path_attribute.value = cast(path_attribute_val_buf, POINTER(c_char))
                path_attribute.len = c_int(len(path_attribute_val))
                path_attributes.append(pointer(path_attribute))
            path.path_attributes = pointer((POINTER(Buf) * _PATTRS_CAP)(*path_attributes))
    path.path_attributes_len = c_int(len(path_attributes))
    path.path_attributes_cap = c_int(_PATTRS_CAP)
    
    return {attribute['type']: {k: v for k, v in attribute.items() if k != 'type'} for attribute in
            json.loads(libgobgp.decode_path(path).decode('utf8')).get('attrs')} 
