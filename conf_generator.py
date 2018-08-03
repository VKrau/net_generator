# -*- coding: utf-8 -*-
"""
Created on Fri Mar 23 15:02:47 2018

@author: VK
"""
from __future__ import absolute_import
from __future__ import print_function
import os
import sys
import re
import shutil
import itertools
import ConfigParser

def generate_combinations(lst, rep):
    yield itertools.product(lst, repeat=rep)

def eval_string(eval_string, gen_dic, gen_schemes_pay = 0):
    for i, j in sorted(gen_dic.iteritems()):
        eval_string +=''.join(str(j))+', '
    eval_string = eval_string[:-1] + ')'
    return list(eval(eval_string))

def generate_conf_files(conf, conf_file):
    conf_dic = {}
    gen_dic = {}
    gen_list = []
    val_list = []
    gen_schemes_pay = []
    for i in conf.items('Parametrization'):
                conf_dic.setdefault(i[0],i[1])
    for i,j in conf_dic.iteritems():
        if 'generate' in j:
            gen_list.append(re.findall(r'(\w+)', re.sub(r'generate', i, j)))
        if 'values' in j:
            val_list.append(re.findall(r'(\w+)', re.sub(r'values', i, j)))
    name = conf_dic['name']
    try:
        for i in gen_list:
            if i[0] == 'toll_scheme':
                gen = generate_combinations(i[1], int(i[2]))
                for i in gen:
                    gen_schemes_pay = list(i)
                for i, j in enumerate(gen_schemes_pay):
                    gen_schemes_pay[i] = ''.join(j)
            else:
                gen_dic.setdefault(i[0], [j for j in range(int(i[1]), int(i[2])+1, int(i[3]))])
    except (ConfigParser.NoSectionError, IndexError):
        print('Error in generate value in the configuration file!')
        sys.exit()
    try:
        for i in val_list:
            if i[0] == 'toll_scheme':
                gen_schemes_pay = [j for j in i[1:]]
            else:
                gen_dic.setdefault(i[0], [int(j) for j in i[1:]])
    except (ConfigParser.NoSectionError, IndexError):
        print('Error in values in the configuration file!')
    if gen_schemes_pay:
        string = 'itertools.product(gen_schemes_pay,'
        out_list= eval_string(string, gen_dic, gen_schemes_pay)
    elif gen_list:
        string = 'itertools.product('
        out_list = eval_string(string, gen_dic)
    else:
        out_list = []
    if out_list:
        for i,j in enumerate(out_list):
            if i == 0:
                shutil.copy2('../'+conf_file, '../Output/gen_conf_files/%s_%s.conf' % (name, i)) #!!!изменение пути
            if gen_schemes_pay:
                conf.set('Parametrization', 'toll_scheme', j[0])
                k = 1
            else:
                k = 0
            conf.set('Parametrization', 'name', '%s_%s' % (name, i))
            for l, m in enumerate(sorted(gen_dic.iterkeys())):
                conf.set('Parametrization', m, j[l+k])
            with open('../Output/gen_conf_files/%s_%s.conf' % (name, i), 'w') as config: #!!!изменение пути
                conf.write(config)
    else:
        shutil.copy2('../'+conf_file, '../Output/gen_conf_files/%s.conf' % name) #!!!изменение пути

def start_conf_generation(conf_file=None):
    conf = ConfigParser.RawConfigParser()
    conf.read('../'+conf_file)
    if os.path.exists('../Output/gen_conf_files') == False: #!!!изменение пути
        os.makedirs('../Output/gen_conf_files') #!!!изменение пути
    generate_conf_files(conf, conf_file)
    
if __name__ == "__main__":
    start_conf_generation()