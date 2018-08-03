# -*- coding: utf-8 -*-
"""
Created on Mon Mar 12 15:12:51 2018

@author: VK
"""
from __future__ import absolute_import
from __future__ import print_function
import os
import sys
import subprocess

def convert2net(n):
    SUMO_HOME = os.path.realpath(os.environ.get(
            'SUMO_HOME', os.path.join(os.path.dirname(__file__), '..', '..', '..', '..')))
    sys.path.append(os.path.join(SUMO_HOME, 'tools'))
    try:
        from sumolib import checkBinary
    except ImportError:
        def checkBinary(name):
            return name
    NETCONVERT = checkBinary('netconvert')
    
    try:
        subprocess.call([NETCONVERT,
                         #'--no-internal-links',
                         '--edge-files', '../Output/gen_net_files/%s/%s.edg.xml' % (n, n), #!!!изменение пути
                         '--node-files', '../Output/gen_net_files/%s/%s.nod.xml' % (n, n), #!!!изменение пути
                         '--connection-files', '../Output/gen_net_files/%s/%s.con.xml' % (n, n), #!!!изменение пути
                         '-o', '../Output/gen_net_files/%s/%s.net.xml' % (n, n)]) #!!!изменение пути
    except WindowsError:
        print('Error: NETCONVERT not found! Check the correctness of the paths!')