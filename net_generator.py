# -*- coding: utf-8 -*-
"""
Created on Mon Mar 12 14:54:03 2018

@author: VK
"""

from __future__ import absolute_import
from __future__ import print_function
import ConfigParser
import sys
import os
from convert import convert2net
import schemes_module

def start_net_generation(args):
    try:
        conf = ConfigParser.RawConfigParser()
        conf.read(args)
        print(args)
        conf_dic = {}
        scheme_of_section = {}
        for i in conf.items('Parametrization'):
            conf_dic.setdefault(i[0],i[1])
        for i in conf.items('Scheme of Section'):
            scheme_of_section.setdefault((i[0]),{'schema_type':str(i[1]).split('__')[0],
                                                 'name':str(i[1]).split('__')[1].split(':')[0],
                                                 'param':[]})
            list_of_param = str(i[1]).split('__')[1].split('__')[0].split(':')[1].split(';')
            for j in list_of_param:
                j = j.strip()
                try:
                    scheme_of_section[i[0]]['param'].append(conf_dic[j])
                except KeyError:
                    pass
        scheme_pay = conf_dic['toll_scheme']
        disallow_truck = conf_dic['truck_scheme']
        project_name = conf_dic['name']
        if os.path.exists('../Output/gen_net_files') == False: #!!!изменение пути
            os.makedirs('../Output/gen_net_files') #!!!изменение пути
        schemes_module.nodes = []
        schemes_module.connections = []
        schemes_module.file_generator(project_name, scheme_of_section, scheme_pay, disallow_truck)
        convert2net(project_name)
    except (ConfigParser.NoSectionError, IndexError):
        print('Error in the contents of the configuration file!')
        sys.exit(0)

if __name__ == "__main__":
    if len(sys.argv) > 1:
        start_net_generation(sys.argv[1])
    else:
        print('Please specify the file to be processed!')