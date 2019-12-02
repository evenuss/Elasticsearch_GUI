from flask import Flask, jsonify, render_template, request, redirect, session, url_for
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



@app.route('/dashboard', methods=['GET','POST'])
def index():
    global es_
    key_list = []
    resp2 = []
    data1 = []
    indexes = es_.indices.get_alias().keys()
    cluster_name = es_.cluster.state(metric=["cluster_name"])['cluster_name']
    st_index = sorted(indexes)
    if request.method == 'POST':
        search = request.form
        indexser = search['cari-index']
        select_indx = es_.indices.get_mapping(index=indexser)
        print(select_indx)
        data = es_.search(index=indexser, body={"query": {"match_all": {}}})
        for a in data["hits"]["hits"]:
            data1.append(a)
            dict = {}
            for key in a["_source"].keys():
                if key not in key_list:
                    key_list.append({key})
                dict[key] = a["_source"][key]
                dict["_index"] = a["_index"]
            resp2.append(dict)
        print(resp2)
        print(data1['_id'])
        print(data1)
    else:
        pass

    context = {
        'cluster': cluster_name,
        'data':st_index,
    }
    return render_template('/home.html', context=context, resp2=resp2, key_list=key_list)



























# @app.route('/dashboard', methods=['GET','POST'])
# def index():
#     global es_
#     key_list = []
#     resp2 = []
#     indexes = es_.indices.get_alias().keys()
#     cluster_name = es_.cluster.state(metric=["cluster_name"])['cluster_name']
#     st_index = sorted(indexes)
#     if request.method == 'POST':
#         search = request.form
#         indexser = search['cari-index']
#         select_indx = es_.indices.get_mapping(index=indexser)
#         print(select_indx)
#         data = es_.search(index=indexser, body={"query": {"match_all": {}}})
#         for a in data["hits"]["hits"]:
#             # id_doc = (a['_id'])
#             # print(id_doc)
#             dict = {}
#             for key in a["_source"].keys():
#                 # print(key)
#                 if key not in key_list:
#                     key_list.append(key)
#                 dict[key] = a["_source"][key]
#                 dict["_index"] = a["_index"]
#             resp2.append(dict)

#         print(resp2)
#         # ez = es.count(index=valueindex)
#         # awe = ez

#     else:
#         pass

#     context = {
#         'cluster': cluster_name,
#         'data':st_index,
#     }
#     return render_template('/home.html', context=context, resp2=resp2, key_list=key_list)



# es.indices.get_alias('*')


if __name__ == '__main__':
    app.run(port=5000, debug=True)
