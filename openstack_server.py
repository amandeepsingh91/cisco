from flask import Flask
from flask_restful import Resource, Api
from sqlalchemy import create_engine
import SimpleHTTPServer, SocketServer, logging, cgi, httplib, simplejson
import sys

app = Flask(__name__)
api = Api(app)

vm_info = {}

#virtual machine running
openstack_server="192.168.56.106"

if len(sys.argv) > 2:
    PORT = int(sys.argv[2])
    I = sys.argv[1]
elif len(sys.argv) > 1:
    PORT = int(sys.argv[1])
    I = ""
else:
    PORT = 9999
    I = ""


class ServerHandler(SimpleHTTPServer.SimpleHTTPRequestHandler):

    def do_OPTIONS(self):
        self.send_response(200, "ok")
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header("Access-Control-Allow-Headers", "X-Requested-With, Content-type")

    def do_GET(self):
        logging.warning("======= GET STARTED =======")
        logging.warning(self.headers)
        SimpleHTTPServer.SimpleHTTPRequestHandler.do_GET(self)

    def do_POST(self):
        logging.warning("======= POST STARTED =======")
        postvars = {}
        length = int(self.headers.getheader('content-length'))
        postvars = cgi.parse_qs(self.rfile.read(length), keep_blank_values=1)
        logging.warning(postvars)


        '''Get Token '''
        params = '{"auth":{"tenantName":"admin","passwordCredentials":{"username":"admin","password":"password"}}}'
        headers = {"Content-type": "application/json"}
        conn = httplib.HTTPConnection("%s:5000" %(openstack_server))
        conn.request("POST", "/v2.0/tokens", params, headers)
        response = conn.getresponse()
        data = simplejson.loads(response.read())
        token = data["access"]["token"]["id"]
        logging.info(token)
        conn.close()

        postvars = eval(postvars.keys()[0])
        requestDict = postvars
        params = postvars["params"]
        if params == 'None':
            params = None

        headers = postvars["headers"]
        headers["X-Auth-Token"] = token
        url = requestDict["url"]

        method = requestDict["type"]

        urls = url.split('/')
        logging.warning(urls[0])
        logging.warning(method)
        logging.warning(url.strip(urls[0]))
        logging.warning(params)
        logging.warning(headers)


        if (url.strip(urls[0]) == '/v2/query/samples'):

            logging.warning("####################### USAGE")
            logging.warning(urls[0])
            resource_array = []
            resource_str = ""
            #para1 = {"filter": "{\"and\":[{\"or\":[{\"=\":{\"resource\":\"b72eff1c-2c09-4b5d-8c9f-5ec9bb77a393\"}}]},{\"or\":[{\"=\":{\"counter_name\":\"memory.resident\"}},{\"=\":{\"counter_name\":\"cpu_util\"}}]}]}", "orderby": "[{\"timestamp\":\"asc\"}]"}
            #para1 = {"filter": "{\"and\":[{\"or\":[{\"=\":{\"resource\":\"063719e1-91cb-4238-9693-976e79ba6048\"}}]},{\"or\":[{\"=\":{\"counter_name\":\"memory.resident\"}}]}]}"}
            resource_array.append("{\"=\":{\"resource\":\"%s\"}}" %(params))
            resource_array.append("{\"=\":{\"resource\":\"%s\"}}" %(""))
            resource_str = ",".join(resource_array)
            para1 = {}
            para1["filter"]= "{\"and\":[{\"or\":[%s]},{\"or\":[{\"=\":{\"counter_name\":\"memory.resident\"}},{\"=\":{\"counter_name\":\"cpu_util\"}},{\"=\":{\"counter_name\":\"disk.usage\"}}]}]}" %(resource_str)
            para1["orderby"]= "[{\"timestamp\":\"asc\"}]"
            para1["limit"] = 5

            logging.warning("Before sending !!!!")
            ip = urls[0].split(":")
            ip[0] = openstack_server
	    logging.warning("vvvvvvvvvvvvvvvvvvvvvvvv")
            logging.warning(ip)
            conn = httplib.HTTPConnection(':'.join(ip))

            x = simplejson.dumps(para1)
            logging.warning(x)
            logging.warning(headers)
            logging.warning(method)
            logging.warning(url)
            logging.warning(urls[0])
            conn.request(method, url.strip(urls[0]), simplejson.dumps(para1), headers)

            logging.warning("After sending sending!!!!")
            response = conn.getresponse()
            #logging.warning(response)
            logging.warning("After sending 1")
            #logging.warning(response)
            resourceData = {}
            result = simplejson.loads(response.read())
            logging.warning(str(result))
            for meter in result:
                if meter["meter"] not in resourceData:
                    if (meter["meter"] == "memory.resident"):
                        resourceData[meter["meter"]] = int((int(meter["volume"])*100) / int(meter["metadata"]['flavor.ram']))
                    elif (meter["meter"] == "disk.usage"):
                        resourceData[meter["meter"]] = int((int(meter["volume"])*100) / (int(meter["metadata"]['disk_gb'])*1024*1024*1024))
                    else:
                        resourceData[meter["meter"]] = int(meter["volume"])
                    logging.warning(str(int(meter["volume"])*100))
                    logging.warning(str(int(meter["metadata"]['flavor.ram'])))
                    logging.warning(str(int(meter["metadata"]['disk_gb'])*1024*1024*1024))
            resourceData["memory"] = resourceData["memory.resident"]
            del resourceData["memory.resident"]
            resourceData["disk"] = resourceData["disk.usage"]
            del resourceData["disk.usage"]
            logging.warning("After sending 2")
            #resourceData = simplejson.dumps(resourceData)
            #logging.warning(resourceData)

	    for resources in result:
		if (("status" in resources["metadata"]) and (resources["metadata"]["status"] == "active") and ("flavor.id" in resources["metadata"])):
		    vm_info[resources["resource_id"]] = {"flavor.id":resources["metadata"]["flavor.id"],"host":resources["metadata"]["host"],"project_id":resources["project_id"]}

	    logging.warning(str(vm_info))
            conn.close()


	elif (url.strip(urls[0]) == '/vertical_scale'):
		    params = '{"resize":{"flavorRef":"%s"}}' %(flavor)
		    headers = {"Content-type": "application/json","Accept": "application/json", "X-Auth-Token": token}
		    conn = httplib.HTTPConnection("127.0.0.1:8774")
		    conn.request("POST", "/v2/%s/servers/%s/action" %(projectId,serverId), params, headers)
		    response = conn.getresponse()
		    conn.close()
		    if(str(response.status) == '202'):
			time.sleep(5)
			params = '{"confirmResize": null}'
			headers = {"Content-type": "application/json", "X-Auth-Token": token}
			conn = httplib.HTTPConnection("127.0.0.1:8774")
			conn.request("POST", "/v2/%s/servers/%s/action" %(projectId,serverId), params, headers)
			response = conn.getresponse()
			conn.close()
			if (str(response.status) == '204'):
			   print "*************************Vertical scaling done"
			   return True
			else:
			   return False
		    else:
			return False
	else:
            logging.warning("Before sending !!!!")
            logging.warning("vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv01")
	    ip = urls[0].split(":")
            ip[0] = openstack_server
            logging.warning(ip)
            conn = httplib.HTTPConnection(':'.join(ip))
            logging.warning(params)
            logging.warning(headers)
            logging.warning(method)
            logging.warning("vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv02")
            logging.warning(url.strip(urls[0]))
            logging.warning(':'.join(ip))
            logging.warning(url.strip(urls[0]))
            conn.request(method, url.strip(urls[0]), params, headers)
           ## conn.request(method, url.strip(urls[0]), simplejson.dumps(params), headers)
            logging.warning("After sending sending!!!!")
            response = conn.getresponse()
            logging.warning(response)
            logging.warning("After sending 1")
            logging.warning(response)
            resourceData = response.read()
            resourceData = resourceData.replace(".","_")
            logging.warning("After sending 2")
            logging.warning(str(resourceData))
            conn.close()

            ##logging.warning(str(resourceData))

        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(resourceData)
        self.wfile.close()
        ##SimpleHTTPServer.SimpleHTTPRequestHandler.do_POST(self)

Handler = ServerHandler

httpd = SocketServer.TCPServer(("", PORT), Handler)

httpd.serve_forever()
Server.py
Displaying Server.py



if __name__ == '__main__':
    app.run()
