from mininet.node import Node


class BGPRouter(Node):

  __ZEBRAD_EXEC_PATH = '/usr/lib/quagga/zebra'
  __GOBGPD_EXEC_PATH = '/opt/go/bin/gobgpd'  
  
  def config(self, **params):
    super(BGPRouter, self).config(**params)

    # enable ip forwarding
    self.cmd('sysctl net.ipv4.ip_forward=1')
    self.waitOutput()

    # disable reverse path forwarding filter
    self.cmd('sysctl -w net.ipv4.conf.all.rp_filter=0')
    self.waitOutput()
    self.cmd('sysctl -w net.ipv4.conf.default.rp_filter=0')
    self.waitOutput()
    
  def terminate(self):
    # enable reverse path forwarding filter
    self.cmd('sysctl -w net.ipv4.conf.all.rp_filter=1')
    self.waitOutput()
    self.cmd('sysctl -w net.ipv4.conf.default.rp_filter=1')
    self.waitOutput()
    
    # disable ip forwarding
    self.cmd('sysctl net.ipv4.ip_forward=0')
    self.waitOutput()    
    
    super(BGPRouter, self).terminate()

  def start_bgp(self):
    self.cmd(self.__ZEBRAD_EXEC_PATH + ' -d -i /tmp/zebrad_{0}.pid >> /tmp/zebrad_{0}.log 2>&1'.format(self.name))    
    self.waitOutput()
    self.cmd(self.__GOBGPD_EXEC_PATH + ' -t toml -f gobgpd.conf >> /tmp/gobgpd_{}.log 2>&1 &'.format(self.name))
    self.waitOutput()
    
  def terminate_bgp(self):
    self.cmd('pkill -9 zebra')
    self.waitOutput()
    self.cmd('pkill -9 bgpd')
    self.waitOutput()

    
class SpineRouter(BGPRouter):

  def config(self, **params):
      super(SpineRouter, self).config(**params)

  def terminate(self):
      super(SpineRouter, self).terminate()

  
class LeafRouter(BGPRouter):  

  def config(self, **params):
      super(LeafRouter, self).config(**params)

  def terminate(self):
      super(LeafRouter, self).terminate()