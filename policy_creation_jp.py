import sys
from pprint import pprint
from datetime import datetime
import datetime

from tetpyclient import RestClient
import json
import requests.packages.urllib3

requests.packages.urllib3.disable_warnings()

API_ENDPOINT="https://{Your cluster's IP or FQDN}"

rc = RestClient(API_ENDPOINT,credentials_file='credentials.json', verify=False)

resp = rc.get('/applications')
app = resp.json()

a_list = []
b_list = []
for i in app:
    app_name = i['name']
    id = i['id']
    a_list.append(app_name)
    b_list.append(id)

app_list = list(enumerate(a_list, start=1))
id_list = list(enumerate(b_list, start=1))

print()
print('-' * 10, 'アプリケーションの一覧を表示します', '-' * 10)
print()

a_dict = {}
for a, b in app_list:
    a_dict[a] = b
    print(f'{a:2}', ":", b)

print()

id_dict = {}
for a, b in id_list:
    id_dict[a] = b

while True:
    x = input('ポリシーを追加したいアプリケーションを番号で入力してください： ')
    x = int(x)
    if x in a_dict:
        break
print()
print('-' * 10, 'clusterの一覧を表示します', '-' * 10)
print()

application_id = id_dict[x]

resp = rc.get('/applications/%s/clusters' % application_id)
clusters = resp.json()

c_list = []
d_list = []

for i in clusters:
    cluster_name = i['name']
    cid = i['id']
    c_list.append(cluster_name)
    d_list.append(cid)

cluster_list = list(enumerate(c_list, start=1))
cid_list = list(enumerate(d_list, start=1))

c_dict = {}
for a, b in cluster_list:
    c_dict[a] = b
    print(f'{a:2}', ":", b)

print()

cid_dict = {}
for a, b in cid_list:
    cid_dict[a] = b

while True:
    y = input('送信元のclusterを番号で入力してください： ')
    y = int(y)
    if y in c_dict:
        break

print()

cluster_id =  cid_dict[y]

print('-' * 10, 'Scopeの一覧を表示します', '-' * 10)
print()

resp = rc.get('/app_scopes')
scopes = resp.json()

e_list = []
f_list = []

for i in scopes:
    scope_name = i['name']
    sid = i['id']
    e_list.append(scope_name)
    f_list.append(sid)

scope_list = list(enumerate(e_list, start=1))
sid_list = list(enumerate(f_list, start=1))

s_dict = {}
for a, b in scope_list:
    s_dict[a] = b
    print(f'{a:2}', ":", b)

print()

sid_dict = {}
for a, b in sid_list:
    sid_dict[a] = b

while True:
    z = input('宛先のScopeを番号で入力してください： ')
    z = int(z)
    if z in s_dict:
        break

print()

scope_id =  sid_dict[z]

p_range = list(range(65535))

print('TCPかUDPどちらですか？')
print()
print(' 1 : TCP\n 2 : UDP')
print()

while True:
    proto = input('番号で選択してください： ')
    if proto == '1' or proto == '2':
        break

print()

if int(proto) == 1:
    proto = 6
elif int(proto) == 2:
    proto = 17

proto = int(proto)

while True:
    port = input('宛先のポート番号を入力してください： ')
    port = int(port)
    if port in p_range:
        break

print()

resp = rc.get('/applications/%s/policies' % application_id)
policy = resp.json()
d_pol = policy['default_policies']
ver = d_pol[0]['version']

req_payload = {
  "version": ver,
  "rank" : "DEFAULT",
  "policy_action" : "ALLOW",
  "priority" : 90,
  "consumer_filter_id" : cluster_id,
  "provider_filter_id" : scope_id,
}

rc.post('/applications/%s/policies' % application_id, json_body=json.dumps(req_payload))

resp = rc.get('/applications/%s/policies' % application_id)
policy= resp.json()

d_pol = policy['default_policies']
policy_id = [rx['id'] for rx in d_pol if (rx['consumer_filter_id'] == cluster_id and rx['provider_filter_id'] == scope_id)]
policy_id = policy_id.pop()

req_payload = {
  "version": ver,
  "start_port" : port,
  "end_port" : port,
  "proto" : proto,
}

resp = rc.post('/policies/%s/l4_params' % policy_id, json_body=json.dumps(req_payload))

if resp.status_code == 200:
    print('ポリシーの設定は正常に完了しました')
else:
    print('ポリシーの設定に失敗しました')

print()
