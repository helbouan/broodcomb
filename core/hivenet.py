from infra import Worker, Infrastructure
from topo import Topo
from net import Network
from mapper import Mapper

import re

class Grid5kInfra(Infrastructure):
    def _to_ip(hostname):
        pattern = r"(?P<cluster>[^-]+)-(?P<node>\d+)\.(?P<site>[^\.]+)\.grid5000\.fr"
        match = re.match(pattern, hostname)
        if match:
            cluster = match.group('cluster')
            node = match.group('node')
            site = match.group('site')
        else:
            return hostname

    def __init__(self, hostnames, key):
        super().__init__()
        for hostname in hostnames:
            ip = self._to_ip(hostname)
            self.add_worker(ip, key)

class FranceTopo(Topo):
    def build(self, n, m):
        self.n = n
        self.m = m
        self.blocks = {}
        self.sites = ['lille', 'paris', 'strasbourg', 'rennes', 'nantes', 'lyon', 'grenoble', 'toulouse', 'marseille', 'nice']
        self.hostmap = {site: [[] for _ in range(n)] for site in self.sites}
        self.linkmap = {'edge': {site: [] for site in self.sites}, 'access': {site: [] for site in self.sites}, 'core': []}
        
        cores = []
        j = 1
        k = 1

        for site in self.sites:
            s = self.add_switch('s%i' % j)
            j += 1
            cores.append(s)
            self.blocks[site] = [s]

            for ii in range(n):
                ss = self.add_switch('s%i' % j)
                j += 1
                self.blocks[site].append(ss)
                link = self.add_link(s, ss, delay='1ms', bw='200Mbit')
                self.linkmap['access'][site].append(link)

                for iii in range(m):
                    h = self.add_host('h%i' % k)
                    k += 1
                    self.blocks[site].append(h)
                    self.hostmap[site][ii].append(h)
                    link = self.add_link(ss, h, delay='1ms', bw='20Mbit')
                    self.linkmap['edge'][site].append(link)

        link = self.add_link(cores[0], cores[1], delay='5ms', bw='2000Mbit')
        self.linkmap['core'].append(link)
        link = self.add_link(cores[1], cores[2], delay='5ms', bw='2000Mbit')
        self.linkmap['core'].append(link)
        link = self.add_link(cores[1], cores[3], delay='5ms', bw='2000Mbit')
        self.linkmap['core'].append(link)
        link = self.add_link(cores[1], cores[5], delay='5ms', bw='2000Mbit')
        self.linkmap['core'].append(link)
        link = self.add_link(cores[3], cores[4], delay='5ms', bw='2000Mbit')
        self.linkmap['core'].append(link)
        link = self.add_link(cores[5], cores[6], delay='5ms', bw='2000Mbit')
        self.linkmap['core'].append(link)
        link = self.add_link(cores[5], cores[8], delay='5ms', bw='2000Mbit')
        self.linkmap['core'].append(link)
        link = self.add_link(cores[7], cores[8], delay='5ms', bw='2000Mbit')
        self.linkmap['core'].append(link)
        link = self.add_link(cores[8], cores[9], delay='5ms', bw='2000Mbit')
        self.linkmap['core'].append(link)
    
class FranceMapper(Mapper):
    def place(self):
        for i in range(10):
            for node in self.topo.blocks[self.topo.sites[i]]:
                self.mapping[node] = self.infra.workers[i]