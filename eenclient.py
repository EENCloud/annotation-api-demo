import requests
import json

HOST = 'login.eagleeyenetworks.com'

class EENClient(object):
    
    def __init__(self,api_key):
        self.api_key = api_key
        
        #disable all the warnings about HTTPS/SSL
        requests.packages.urllib3.disable_warnings()
        
        #setup the session
        session = requests.Session()
        session.headers.update({'Authentication':api_key})
        self.session = session

    def authenticate(self, username, password):
        login_url = 'https://{}/g/aaa/authenticate'.format(HOST)
        headers = {'Content-Type':'application/json'}
        credentials = {'username':username,'password':password}
        r = self.session.post(login_url, headers=headers,json=credentials,verify=False)
        if r.status_code == 200:
            return json.loads(r.content)['token']
        else:
            return None
            
    def authorize(self,token):
        url = 'https://{}/g/aaa/authorize'.format(HOST)
        headers = {'Content-Type':'application/json'}
        body = {'token':token}
        r = self.session.post(url, headers=headers,json=body)
        #print r.headers
        # Set-cookies attribute in the resonse header contains the auth_key.  Session
        # object will manage this for us.
        if r.status_code == 200:
            return json.loads(r.content)
        else:
            return None
            
    def getDevice(self, esn):
        url = 'https://{}/g/device'.format(HOST)
        payload = {'id':esn}
        r = self.session.get(url,params=payload)
        if r.status_code == 200:
            return json.loads(r.content)
        else:
            return None

    def getAnnotations(self,esn,uuids):
        url = 'https://{}/annt/annt/get'.format(HOST)
        anntids = ",".join(uuids)
        payload = {'id':esn,'uuid':anntids}
        r = self.session.get(url,params=payload)
        if r.status_code == 200:
            return json.loads(r.content)
        else:
            return None
    
    def getAnnotationsList(self,esn,start,end,count=None,uuid=None,namespace=None):
        url = 'https://{}/annt/annt/list'.format(HOST)
        payload = {'id':esn,'start_timestamp':start,'end_timestamp':end}
        print payload
        if count is not None:
            payload['count'] = count
        if uuid is not None:
            payload['uuid'] = uuid
        if namespace is not None:
            payload['namespace'] = namespace
        r = self.session.get(url,params=payload)
        # print r.status_code
        # print r.content
        if r.status_code == 200:
            return json.loads(r.content)
        else:
            return None        

    def createAnnotation(self,esn,ts,payload,ns):
        url = 'https://{}/annt/set?c={}&ts={}&ns={}'.format(HOST,esn,ts,ns)
        headers = {'Content-Type':'application/json'}
        # print payload, url
        r = self.session.put(url, headers=headers,json=payload)
        # print r.content
        # print r.status_code  
        if r.status_code == 200:
            return json.loads(r.content)
        else:
            return None

    def updateAnnotation(self,uuid,esn,ts,payload,ns=None,update_type='mod'):
        url = 'https://{}/annt/set?u={}&c={}&ts={}&ns={}&type={}'.format(HOST,uuid,esn,ts,ns,update_type)
        headers = {'Content-Type':'application/json'}
        r = self.session.post(url, headers=headers,json=payload)
        # print url
        # print r.content
        # print r.status_code
        if r.status_code == 200:
            return json.loads(r.content)
        else:
            return None

    def __str__(self):
        return "EENClient with API-KEY: {}".format(self.api_key)
        