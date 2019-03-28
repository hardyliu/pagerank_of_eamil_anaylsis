# -*- coding: utf-8 -*-
"""
Created on Thu Mar 28 15:30:33 2019
用pagerank来分析希拉里邮件中的重要人物关系
@author: hardyliu
"""

import pandas as pd
import networkx as nx
import numpy as np
import matplotlib.pyplot as plt
from collections import defaultdict

#加载数据集
#读取邮件数据
emails = pd.read_csv('./input/Emails.csv')
#读取别名文件
file = pd.read_csv('./input/Aliases.csv')

aliases={}

for index,row in file.iterrows():
    #将别名和ID对应上
    aliases[row['Alias']]=row['PersonId']
#读取人名    
file = pd.read_csv('./input/Persons.csv')
persons={}

for index,row in file.iterrows():
    persons[row['Id']]=row['Name']
    
 
#将人名规范化处理    
def transform_name(name):
    #将姓名统一小写
    name = str(name).lower()
    #去掉，和@之后的内容
    name = name.replace(",","").split("@")[0]
    #转换别名
    if name in aliases.keys():
        return persons[aliases[name]]
    return name

#画人物网络关系图
def show_graph(graph,layout='spring_layout'):
    
    if layout=='circular_layout':
        #在一个圆环上均匀分布节点
        positions=nx.circular_layout(graph)
    else:
        #中心放射状
        positions=nx.spring_layout(graph)
    #由于节点属性pagerank的值太小，将其放大一定倍数显示
    nodesize=[x['pagerank']*20000  for v,x in graph.nodes(data=True)]
   #设置边的长度
    edgesize = [np.sqrt(e[2]['weight']) for e in graph.edges(data=True)]
    #绘制节点
    nx.draw_networkx_nodes(graph,positions,node_size=nodesize,alpha=0.4) 
    #绘制边
    nx.draw_networkx_edges(graph,positions,edge_size=edgesize,alpha=0.2)
    #绘制节点的label
    nx.draw_networkx_labels(graph,positions,font_size=10)
    plt.show()

#将发件人和收件人字段进行规范化处理        
emails.MetadataFrom=emails.MetadataFrom.apply(transform_name) 
emails.MetadataTo = emails.MetadataTo.apply(transform_name)   

edges_weights_temp= defaultdict(list)
#设置边的权重为所发邮件的次数
for row in zip(emails.MetadataFrom,emails.MetadataTo,emails.RawText):
    temp = (row[0],row[1])
    if temp not in edges_weights_temp:
        edges_weights_temp[temp]=1
    else:
        edges_weights_temp[temp]=edges_weights_temp[temp]+1
        
#将(from,to),weight转化为 (from,to,weight)        
edges_weights=[(key[0],key[1],val) for key,val in edges_weights_temp.items()]
#创建一个有向图
graph = nx.DiGraph()

#设置有向图的路径和权重
graph.add_weighted_edges_from(edges_weights)
#计算每个节点的PR值
pagerank = nx.pagerank(graph)
#将pagerank作为节点的属性
nx.set_node_attributes(graph,name='pagerank',values=pagerank)

#显示网络图
show_graph(graph)

#设置PR的阀值，用来筛选大于阀值的核心节点
pagerank_threshold=0.005

#复制一份计算好的网络关系图
small_graph = graph.copy()
#剪掉pr值小于阀值的节点
for n,p_rank in graph.nodes(data=True):
    if p_rank['pagerank']<pagerank_threshold:
        small_graph.remove_node(n)
        
#绘制采用circular_layout布局的网络图        
show_graph(small_graph,'circular_layout')        

        
    