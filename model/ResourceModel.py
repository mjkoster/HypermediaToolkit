
""" ResourceModel class is a list of resource nodes that can be used to 
    construct a resource set at a server location or to inspect resources
    at a server location. The model can be populated by loading a 
    constructor in the collection+senml+json content format, and an 
    existing model can likewise be serialized to the same content format.
    
    TODO. For this and content handlers in the resource layer, we could
    separate the model handling from the serialization and for example 
    an alternate collection+senml+xml format could be easily supported.
"""
from HypermediaHttpRequest import HypermediaHttpRequest
from SenmlCollectionHandler import SenmlCollection
from Links import Links
from Items import SenmlItems
import json
import terms as v

class ResourceModel():
    def __init__(self, model=None, serverAddress=None):
        self._resourceNodeArray = []
        if model:
            self.load(model)   
        if serverAddress:
            self._server = Server(serverAddress)
        
    def serialize(self):
        self._result = []
        for node in self._resourceNodeArray :
            self._result.append(node.getModel())
        return json.dumps(self._result)
    
    def load(self, jsonString):
        self._loadObject = json.loads(jsonString)
        if isinstance(self._loadObject, list):
            for nodeMap in self._loadObject:
                self.addNodes(ResourceNode(nodeMap))
        elif isinstance(self._loadObject, dict):
            self.addNodes(ResourceNode(nodeMap))
            
    def createOnServer(self):
        for node in self._resourceNodeArray:
            self._server.createResourceNode(node)
    
    def loadFromServer(self):
        self._server.getResources("/", self._resourceNodeArray)
    
    def addNodes(self, nodes):
        if isinstance(nodes,list) :
            self._resourceNodeArray.extend(nodes)
        else:
            self._resourceNodeArray.append(nodes)
    
    def removeNode(self, path, selectMap):
        """ remove the selected node and all subresource nodes """
        pass
    
class ResourceNode():
    def __init__(self, nodeMap):
        
        self._links = Links(nodeMap[v._l])
        self._items = SenmlItems(nodeMap[v._e])
        self._baseName = nodeMap[v._bn]
        self._resource = SenmlCollection(self._links.get(), self._items._items, self._baseName)

    def serialize(self):
        return self._resource.serialize()
    
    def load(self, jsonString):
        self._resource.load(jsonString)
        
    def getModel(self):
        return self._resource._senml

class Server():
    def __init__(self, server):
        self._server = server
        
    def createResourceNode(self, node):
        # this is a bit inelegant because it's not using a hypermedia form
        self._url = self._server + node.getModel()[v._bn]
        print "createResourceNode: ", node._resource.serialize()
        self._request = HypermediaHttpRequest(self._url, \
                {v.method: v.post, v.contentFormat: v.senmlCollectionType, v.payload: node._resource.serialize() })
        self._request.send()
        self._request.getResponse()
        print "Status: ", self._request._requestMap[v.response][v.status]
        if v.location in self._request._requestMap[v.options] :
            print "Location: ", self._request._requestMap[v.options][v.location]
        
    def getResources(self, uriPath, resourceArray):
        self._getResourceRecursive(uriPath, resourceArray)
    
    def _getResourceRecursive(self, uriPath, resourceArray):
        resourceNode = self._getResource(uriPath)
        resourceArray.append(resourceNode)
        for link in resourceNode._links.get({v._rel:v._sub}) :
            self._getResourceRecursive(resourceNode._baseName + link[v._href], resourceArray)

    def _getResource(self, uriPath="/"):
        self._url = self._server + uriPath
        self._request = HypermediaHttpRequest(self._url, \
                {v.method:v.get, v.contentFormat:v.senmlCollectionType })
        self._request.send()
        self._request.getResponse()
        print "payload: ", self._request._requestMap[v.response][v.payload]
        return ResourceNode( json.loads(self._request._requestMap[v.response][v.payload] ) )


def selfTest():
    jsonString = \
        """[ {"bn": "/", "e": [{"n":"test","sv":"testValue"}], "l": [{"href": "", "rel": ["self"]}, {"href": "test", "rel": "sub"}]} ]"""
    serverAddress = \
        "http://localhost:8000"
    model = ResourceModel(jsonString, serverAddress)
    model.createOnServer()
    print "created on server"
    model.__init__()
    model.loadFromServer()
    print "model from server: ", model.serialize()
    
if __name__ == "__main__" :
    selfTest()
    
    