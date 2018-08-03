# -*- coding: utf-8 -*-
"""
Created on Mon Mar 12 14:54:03 2018

@author: VK
"""

from __future__ import absolute_import
from __future__ import print_function
import xml.etree.ElementTree as ET
from xml.dom import minidom
import sys
import os

nodes = []
connections = []

class Road_Schemes():
    def __init__(self):
        self.count_junc = 0
        self.coord_x = 0
        self.coord_y = 0
        self.last_junction = 0
        self.last_edge = []
        self.last_scheme = ''
        self.len_step = []
        self.lst_shape = []
        self.last_ybias = []
        
    def expansion_narrows_road(self, name, lst, attr, edg_coll, arg):
        length_one_edge = float(lst[-1]) / (max(int(lst[1]), int(lst[0])) - min(int(lst[1]), int(lst[0])) + 1)
        if self.last_junction==0:
            nodes.append(['gneJ' + str(self.last_junction), self.coord_x, self.coord_y, 'zipper'])
        k, d = int(lst[0]), int(lst[1])
        s = max(k,d)-min(k,d) + 1
        if k > d: scheme = 'narrows'
        else: scheme = 'expansion'
        for i in range(s):
            attr['id'] = name + str(i)
            attr['from'] = 'gneJ' + str(self.last_junction)
            attr['to'] = 'gneJ' + str(self.last_junction+1)
            attr['numLanes'] = str(k)
            ET.SubElement(edg_coll, 'edge', attrib=attr)
            self.coord_x +=length_one_edge
            self.last_junction +=1
            nodes.append(['gneJ' + str(self.last_junction), self.coord_x, self.coord_y, 'zipper'])
            if i>0:
                if scheme == 'expansion':
                    connections.append([name + str(i-1), name + str(i), '', ''])
                if scheme == 'narrows':
                    for j in range(k+1):
                        if j == 0:
                            connections.append([name + str(i-1), name + str(i), '0', '0'])
                        else:
                            connections.append([name + str(i-1), name + str(i), str(j), str(j-1)])
            if arg==0: k +=1
            else: k -=1
            self.last_edge.append(name + str(i))
            self.last_scheme = scheme
            
    def straight_road(self, name, lst, attr, edg_coll):
        if self.last_junction==0:
            nodes.append(['gneJ' + str(self.last_junction), self.coord_x, self.coord_y, 'zipper'])
            self.last_edge.append(name)
        attr['id'] = name
        attr['from'] = 'gneJ' + str(self.last_junction)
        attr['to'] = 'gneJ' + str(self.last_junction+1)
        attr['numLanes'] = lst[0]
        ET.SubElement(edg_coll, 'edge', attrib=attr)
        self.coord_x +=float(lst[1])
        self.last_junction +=1
        nodes.append(['gneJ' + str(self.last_junction), self.coord_x, self.coord_y, 'zipper'])
        connections.append([self.last_edge[-1], name, '', ''])      
        self.last_edge.append(name)
        self.last_scheme = 'straight'
    
    def one_to_one(self, name, lst, attr, edg_coll, paying=0, scheme_pay='', disallow_track=''):  
        if self.last_scheme not in ['one-to-one', 'one-to-one_pay', 'one-to-many']:
            print('Error! Use the scheme "One-to-One" after "One-to-Many" or "One-to-One"!')
            sys.exit()
        else:
            e = float(lst[0])
            ybias = 4 #!!! было 4
            k = 0
            shape_y = 0
            if self.last_scheme == 'one-to-many':
                total_offset = (self.count_junc-2)*ybias            
                self.last_ybias = list(range(-total_offset, ybias*2, ybias))
                for i in range(self.count_junc):   
                    if i == 0:
                        shape_y -= total_offset-0.82 #координата для первого shape
                    else:
                        shape_y += 3.35
                    self.lst_shape.append(shape_y)
            length_before = len(self.last_edge) - self.count_junc
            attr['numLanes'] = '1'
            scheme_pay = list(scheme_pay)
            disallow_track = list(disallow_track)
            #scheme_pay.reverse()
            #disallow_track.reverse()
            last_coord_shape = round(self.coord_x+e,2)
            
            for i in range(self.count_junc):
                string_of_shape = '%.2f,%.2f %.2f,%.2f %.2f,%.2f' % (nodes[self.last_junction - self.count_junc][1],
                                                                     self.coord_y,
                                                                     nodes[self.last_junction - self.count_junc][1],
                                                                     self.lst_shape[i],
                                                                     last_coord_shape,
                                                                     self.last_ybias[i])
                attr['from'] = 'gneJ' + str(self.last_junction - self.count_junc)
                if i == 0:
                    if self.last_scheme == 'one-to-many':
                        attr['shape'] = string_of_shape
                        k = self.last_junction + self.count_junc - 1
                    elif self.last_scheme == 'one-to-one' or self.last_scheme == 'one-to-one_pay':
                        k = self.last_junction
                        attr['shape'] = ''
                    attr['to'] = 'gneJ' + str(k)
                if i > 0:
                    if self.last_scheme == 'one-to-many':
                        attr['shape'] = string_of_shape
                        attr['to'] = 'gneJ' + str(k-i)
                    elif self.last_scheme == 'one-to-one' or self.last_scheme == 'one-to-one_pay':
                        attr['to'] = 'gneJ' + str(k+i)
                        attr['shape'] = ''
                    if i == self.count_junc-2 or i ==self.count_junc - 1:
                        attr['shape'] = ''
                
                if paying==1:
                    try:
                        if int(scheme_pay[i])==0:
                            if int(disallow_track[i])==1:
                                attr['disallow'] = 'truck trailer'
                            else:
                                attr['disallow'] = ''
                            attr['id'] = name + 'cash_%02d.0' % i
                            self.last_edge.append(name + 'cash_%02d.0' % i)
                        else:
                            if int(disallow_track[i])==1:
                                attr['disallow'] = 'truck trailer'
                            else:
                                attr['disallow'] = ''
                            attr['id'] = name + 'trans_%02d.0' % i
                            self.last_edge.append(name + 'trans_%02d.0' % i)
                    except IndexError:
                        attr['disallow'] = ''
                        attr['id'] = name + 'cash_%02d.0' % i
                        self.last_edge.append(name + 'cash_%02d.0' % i)
                else:
                    if self.last_scheme == 'one-to-one_pay':
                        if 'tr' in self.last_edge[length_before+i]:
                            attr['id'] = '_q_pay_%02d_%s_trans_' % (i, name)
                        else:
                            attr['id'] = '_q_pay_%02d_%s' % (i, name)
                    else:
                        attr['id'] = name + str(i)
                    self.last_edge.append(name + str(i))
                if self.last_scheme == 'one-to-many':
                    connections.append([self.last_edge[length_before+i], attr['id'], '0', '0'])
                elif self.last_scheme == 'one-to-one' or self.last_scheme == 'one-to-one_pay':
                    connections.append([self.last_edge[length_before+i], attr['id'], '', ''])                    
                ET.SubElement(edg_coll, 'edge', attr)
                nodes.append(['gneJ' + str(self.last_junction), self.coord_x+e, ybias, 'priority'])
                ybias -= 4 #!!! ставим 4, если хотим оптимальное расстояние между шлюзами
                self.last_junction +=1
            self.coord_x += e
            self.count_junc = i + 1
            if paying==1:
                self.last_scheme = 'one-to-one_pay'
            else:
                self.last_scheme = 'one-to-one'

    def one_to_many(self, name, lst, attr, edg_coll):
        self.count_junc = 0
        if self.last_scheme not in ['expansion', 'straight']:
            print('Error! Use the scheme "One-to-Many" after "Expansion" or "Straight"!')
            sys.exit()
        else:
            self.count_junc = 0
            d = int(lst[0])
            self.len_step = float(lst[1])/d
            for i in range(d):
                if i == 0:
                    self.len_step = [float(lst[1])*0.20]
                else:
                    r_len_step = float(lst[1]) - sum(self.len_step)
                    self.len_step.append(r_len_step / (d-1))
            for i in range(d):
                self.coord_x +=self.len_step[i]
                self.last_junction +=1
                attr['id'] = name + str(i)
                attr['from'] = 'gneJ' + str(self.last_junction-1)
                attr['to'] = 'gneJ' + str(self.last_junction)
                attr['numLanes'] = str(d-i)
                for j in range(d+1-i):
                    if j > 0 and i > 0:
                        connections.append([self.last_edge[-1], name+str(i), str(j), str(j-1)])
                    elif j == 0 and i == 0:
                        connections.append([self.last_edge[-1], name+str(i), '', ''])
                if i < (d-1):
                    nodes.append(['gneJ' + str(self.last_junction), self.coord_x, 0, 'unregulated']) #!!! было 1
                elif i == (d-1):
                    nodes.append(['gneJ' + str(self.last_junction), self.coord_x, 3, 'unregulated']) #!!! было 3
                self.last_edge.append(name + str(i))
                self.count_junc +=1
                ET.SubElement(edg_coll, 'edge', attrib=attr)
            self.last_junction +=1
            self.last_scheme = 'one-to-many'

    def many_to_one(self, name, lst, attr, edg_coll):
        if self.last_scheme not in ['one-to-one', 'one-to-one_pay']:
            print('Error! Use schema "Many-to-One" after "One-to-One"!')
            sys.exit()
        else:
            self.last_ybias.reverse()
            self.lst_shape.reverse()
            first_bias = float(lst[0])
            for i in range(self.count_junc):
                if i == 0:
                    self.coord_x +=first_bias
                else:
                    self.coord_x +=self.len_step[-i]
                string_of_shape = '%.2f,%.2f %.2f,%.2f %.2f,%.2f' % (nodes[self.last_junction - self.count_junc][1],
                                                                     self.last_ybias[i],
                                                                     self.coord_x,
                                                                     self.lst_shape[i],
                                                                     self.coord_x,
                                                                     self.coord_y)
                
                attr['id'] = name + str(i)
                attr['from'] = 'gneJ' +str(self.last_junction-self.count_junc)
                attr['to'] = 'gneJ' + str(self.last_junction)
                attr['numLanes'] = '1'
                if i > 1:
                    attr['shape'] = string_of_shape
                    pass
                if i == 0:
                    nodes.append(['gneJ' + str(self.last_junction), self.coord_x, 3, 'unregulated']) #!!! было 3
                else:
                    nodes.append(['gneJ' + str(self.last_junction), self.coord_x, 0, 'unregulated']) #!!! было 0
                self.last_edge.append(attr['id'])
                ET.SubElement(edg_coll, 'edge', attrib=attr)
                attr['shape'] = ''
                attr['id'] = name + '.' + str(i)
                attr['from'] = 'gneJ' + str(self.last_junction)
                attr['to'] = 'gneJ' + str(self.last_junction+1)
                attr['numLanes'] = str(i+1)
                connections.append([self.last_edge[-1], attr['id'], '0', '0'])
                self.last_edge.append(attr['id'])
                #!!!эту часть переписать
                for j in range(i):
                    connections.append([name + '.' + str(i-1), name + '.' + str(i), str(j), str(j+1)])
                self.last_junction +=1
                ET.SubElement(edg_coll, 'edge', attrib=attr)
            self.coord_x +=self.len_step[0]
            nodes.append(['gneJ'+str(self.last_junction), self.coord_x, 0, 'zipper'])
            self.last_scheme = 'many-to-one'

def save_xml(project_name, filename, xml_code):
    xml_string = ET.tostring(xml_code).decode()
    if os.path.exists('../Output/gen_net_files/'+project_name) == False: #!!!изменение пути
        os.makedirs('../Output/gen_net_files/'+project_name) #!!!изменение пути
    xml_prettyxml = minidom.parseString(xml_string).toprettyxml(encoding='UTF-8')
    with open('../Output/gen_net_files/'+project_name+'/'+filename, 'wb') as xml_file:
        xml_file.write(xml_prettyxml)

def file_generator(project_name, scheme_of_section, scheme_pay, disallow_truck):
    attr = {'id':'', 'from':'', 'to':'', 'priority':'1', 'numLanes':'',
            'speed':'13.89', 'disallow':'', 'shape':''}
    attr_node = {'id':'', 'x':'', 'y':'', 'type':''}
    attr_conn = {'from':'', 'to':'', 'fromLane':'', 'toLane':''}
    edg_coll = ET.Element('edges',
                     attrib={'version':'0.27',
                             'xmlns:xsi':'http://www.w3.org/2001/XMLSchema-instance',
                             'xsi:noNamespaceSchemaLocation':'http://sumo.dlr.de/xsd/edges_file.xsd'})
    obj = Road_Schemes()
    for key in sorted(scheme_of_section.iterkeys()):
        lst = scheme_of_section[key]['param']
        name = scheme_of_section[key]['name']
        if scheme_of_section[key]['schema_type'] == 'Expansion':
            obj.expansion_narrows_road(name, lst, attr, edg_coll, 0)
        elif scheme_of_section[key]['schema_type'] == 'Straight':
            obj.straight_road(name, lst, attr, edg_coll)
        elif scheme_of_section[key]['schema_type'] == 'One-to-Many':
            obj.one_to_many(name, lst, attr, edg_coll)
        elif scheme_of_section[key]['schema_type'] == 'One-to-One':
            if scheme_of_section[key]['param'][-1] == '1':
                obj.one_to_one(name, lst, attr, edg_coll, 1, scheme_pay, disallow_truck)
            else:
                obj.one_to_one(name, lst, attr, edg_coll, 0)
        elif scheme_of_section[key]['schema_type'] == 'Many-to-One':
                obj.many_to_one(name, lst, attr, edg_coll)
        elif scheme_of_section[key]['schema_type'] == 'Narrows':
            obj.expansion_narrows_road(name, lst, attr, edg_coll, 1)
        elif scheme_of_section[key]['schema_type'] == 'Experimental':
            obj.experimental(name, lst, attr, edg_coll)
    save_xml(project_name, project_name + '.edg.xml', edg_coll)
    
    nod_coll = ET.Element('nodes',
                          attrib={'version':'0.27',
                             'xmlns:xsi':'http://www.w3.org/2001/XMLSchema-instance',
                             'xsi:noNamespaceSchemaLocation':'http://sumo.dlr.de/xsd/nodes_file.xsd'})
    ET.SubElement(nod_coll, 'location',
                  attrib={'netOffset':'0.00,0.00',
                          'convBoundary':'0.00,0.00,%.2f,0.00' % (obj.coord_x),
                          'origBoundary':'-10000000000.00,-10000000000.00,10000000000.00,10000000000.00',
                          'projParameter':'!'})

    for i in range(len(nodes)):
        attr_node['id'] = nodes[i][0]
        attr_node['x'] = '%.2f' % nodes[i][1]
        attr_node['y'] = '%.2f' % nodes[i][2]
        if i==0 or i==len(nodes)-1:
            attr_node['type'] = 'dead_end'
        else:
            attr_node['type'] = nodes[i][3]
        ET.SubElement(nod_coll, 'node', attrib=attr_node)
    save_xml(project_name, project_name + '.nod.xml', nod_coll)
    
    conn_coll = ET.Element('connections',
                           attrib={'version':'0.27',
                             'xmlns:xsi':'http://www.w3.org/2001/XMLSchema-instance',
                             'xsi:noNamespaceSchemaLocation':'http://sumo.dlr.de/xsd/connections_file.xsd'})
    
    for i in range(len(connections)):
        attr_conn['from'] = connections[i][0]
        attr_conn['to'] = connections[i][1]
        attr_conn['fromLane'] = connections[i][2]
        attr_conn['toLane'] = connections[i][3]
        if (attr_conn['fromLane'] or attr_conn['toLane']) == '':
            del attr_conn['fromLane']
            del attr_conn['toLane']
        ET.SubElement(conn_coll, 'connection', attrib=attr_conn)
    save_xml(project_name, project_name + '.con.xml', conn_coll)