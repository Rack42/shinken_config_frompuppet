#!/usr/bin/env python
# -*- coding: utf-8 -*-
#  Copyright (C) 2015 Olivier Hanesse, olivier.hanesse@gmail.com  
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU Affero General Public License as
#  published by the Free Software Foundation, either version 3 of the
#  License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU Affero General Public License for more details.
#
#  You should have received a copy of the GNU Affero General Public License
#  along with this program.  If not, see <http://www.gnu.org/licenses/>.

import sys
import os
import json
from optparse import OptionParser
from mapping_puppet_shinkenpack import sup_template, mapping

try:
    import jinja2
except:
    print "Please install python-jinja2."
    sys.exit(1)


try:
    import requests
except:
    print "Please install python-requests."
    sys.exit(1)

class QueryPackPuppetDB:

    def __init__(self, url, pack):
        self.url = url
        self.pack = pack

    def get_data_from_puppetdb(self,query):
        """ Function for fetching data from PuppetDB """
        headers = {'Accept': 'application/json'}
        # Specify an order for the resources, so we can compare (diff) results from several runs.
        payload = {'query': query, 'order-by': '[{"field": "title"}]'}
        r = requests.get(self.url, params=payload, headers=headers)
        ndata = json.loads(r.text)
        return ndata

    def get_hosts_from_pack(self):
        """Returns a hash of all hosts where given pack has been applied
        """
        query = """["and",
                   ["not", ["=", ["parameter", "ensure"], "absent"]],
                   ["=", "type", "{pack}"],
                   ["=", ["node", "active"], true]]""".format(pack=self.pack)
        hosts = {}
        for host in self.get_data_from_puppetdb(query):
          hosts[host['certname']] = {}
          hosts[host['certname']]['parameters'] = host['parameters']
        return hosts


def write_host_config(hostname,tmpdir,config):
   """Write config to a file in tmpdir/. 
   """
   conf_file = os.path.join(tmpdir, '%s.cfg' % hostname)
   if not os.path.exists(tmpdir):
      os.mkdir(tmpdir)
   with open(conf_file, 'w') as f:
       f.write(config)


def main():
    usage = '''Usage: %prog [options]

Mapping Files
Class Puppet <-> Pack Shinken

'''
    parser = OptionParser(usage)
    parser.add_option("-i", "--hostname", dest="hostname",
        help="Hostname or IP of PuppetDB host.")
    parser.add_option("--base-dir", type="string", dest="base_dir", default="/tmp/shinken/",
                      help="Base configuration directory [default: %default]")
    (opts, args) = parser.parse_args()

    if opts.hostname:
        url = "http://" + opts.hostname + ":8080/v3/resources"
    else:
        print "Please provide a hostname."
        sys.exit(1)

    config_packs = {}

    packs = mapping.keys()
    for pack in packs:
      h = QueryPackPuppetDB(url, pack).get_hosts_from_pack()
      for i in h:
          if i in config_packs and not (config_packs[i] is None):
            config_packs[i]['parameters'][pack] = h[i]['parameters']
          else:
            config_packs[i] = {}
            config_packs[i]['packs'] = []
            config_packs[i]['parameters'] = {}
            config_packs[i]['parameters'][pack] = h[i]['parameters']
          config_packs[i]['packs'].append(pack)

    # Put everything together
    for h in config_packs:
      # we need the default template
      config_packs[h]['template'] = [ config_packs[h]['parameters']['Shinken::Packs::Host']['template'] ]
      for p in config_packs[h]['packs']:
        if mapping[p]:
          config_packs[h]['template'].insert(0,mapping[p])
      config_packs[h]['template'] = ', '.join(config_packs[h]['template'])
    

    #Now we can generate proper shinken config files
    for h in config_packs:
      write_host_config(h,opts.base_dir,jinja2.Template(sup_template['shinken_host']).render(name=h,template=config_packs[h]['template'],macros=config_packs[h]['parameters']))

if __name__ == "__main__":
    main()
