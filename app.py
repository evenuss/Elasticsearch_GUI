from flask import Flask, jsonify, render_template, request, redirect, session, url_for, make_response
from elasticsearch import Elasticsearch
from datetime import datetime
import requests
import json
from os import environ


app = Flask(__name__)

app.secret_key = 'zsjdfnegee#sd43afsfmni4n3432dsfnnh30djdh3h8hjej9k*'


es_ = None

@app.route('/', methods=['GET','POST'])
def connect():
    if request.method == 'POST':
        data = request.form
        # name = data['name']
        host = data['host']
        port = data['port']
        es = Elasticsearch([{'host':host,'port':port}])
        try:
            if es:
                global es_
                es_ = es
                return redirect(url_for('index'))
        except Exception as e:
            # return "Error Can't connect to elastic server with host {} and port {}".format(host, port)
            return str(e)
    elif request.method == "GET":
        return render_template('/connect.html' )
    else:
        return "Method not allowed"

@app.route('/home', methods=['GET','POST'])
def index():
    global es_
    indexes = es_.indices.get_alias().keys()
    indexess = sorted(indexes)
    # print(indexes)
    cluster_name = es_.cluster.state(metric=["cluster_name"])['cluster_name']
    # print(cluster_name)
    return render_template('/home.html', context=indexess)


@app.route('/cariindex', methods=['POST','GET'])
def search_index():
    global es_
    indexes = es_.indices.get_alias().keys()
    indexess = sorted(indexes)
    # print(indexes)
    cluster_name = es_.cluster.state(metric=["cluster_name"])['cluster_name']
    # print(cluster_name)
    layer1 = []
    layer_dict = []
    layer_lists = []
    if request.method == 'POST':
        search = request.form
        search_index = search['index']
        select_index = es_.indices.get_mapping(index=search_index)
        # print(select_index)
        data = es_.search(index=search_index, body={"query": {"match_all": {}}})
        for doclay1 in data['hits']['hits']:
            # print(doclay1)
            layer1.append(doclay1['_index'])
            dict = {}
            for layer_list in doclay1['_source'].keys():
                if layer_list not in layer_lists:
                    layer_lists.append(layer_list)
                dict[layer_list] = doclay1["_source"][layer_list]
                dict["_index"] = doclay1["_index"]
            layer_dict.append(dict)
        # print(layer_dict)
    else:
        pass
    return render_template('/home.html',context=indexess, doc1=layer1, layer_list=layer_lists, layer_dict=layer_dict)

@app.route('/delete/<string:id>/<string:index>', methods=['GET','POST'])
def delete(id,index):
    global es_
    a = es_.delete(index=index, id=id)
    if a:
        print('Success!')
        indexes = es_.indices.get_alias().keys()
        indexess = sorted(indexes)
        cluster_name = es_.cluster.state(metric=["cluster_name"])['cluster_name']
        layer1 = []
        layer_dict = []
        layer_lists = []
        data = es_.search(index=index, body={"query": {"match_all": {}}})
        for doclay1 in data['hits']['hits']:
            layer1.append(doclay1['_index'])
            dict = {}
            for layer_list in doclay1['_source'].keys():
                if layer_list not in layer_lists:
                    layer_lists.append(layer_list)
                dict[layer_list] = doclay1["_source"][layer_list]
                dict["_index"] = doclay1["_index"]
            layer_dict.append(dict)
        return render_template('/home.html',context=indexess, doc1=layer1, layer_list=layer_lists, layer_dict=layer_dict)
    else:
        return render_template('/home.html',context=indexess, doc1=layer1, layer_list=layer_lists, layer_dict=layer_dict)



@app.route('/edit/<string:id>/<string:indes>', methods=['POST','GET'])
def edit(indes,id):
    global es_, doclay1
    layer1=[]
    layer_lists=[]
    layer_dict=[]
    rec= request.form.to_dict()
    res = es_.search(index=indes, body={"query": {"match": {"id":id}}})
    if res:
        for doclay1 in res['hits']['hits']:
            layer1.append(doclay1['_index'])
            dict = {}
            for layer_list in doclay1['_source'].keys():
                if layer_list not in layer_lists:
                    layer_lists.append(layer_list)
                dict[layer_list] = doclay1["_source"][layer_list]
                dict["_index"] = doclay1["_index"]
            layer_dict.append(dict)
    else:
        pass

    if 'update' and request.method == 'POST':
        # print(json.dumps(dict['_index']))
        # print(json.dumps(str(dict['id'])))
        print(rec)
        es_.update(index=indes,id=id,body={"doc":rec})
        return render_template('/edit.html', isi=layer_dict, layer_lists=layer_lists)



    return render_template('/edit.html', isi=layer_dict, layer_lists=layer_lists)

















if __name__ == '__main__':
    app.run(port=5000, debug=True)
