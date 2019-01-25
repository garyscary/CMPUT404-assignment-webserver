#  coding: utf-8 
import socketserver
import os
import mimetypes

# Copyright 2013 Abram Hindle, Eddie Antonio Santos
# Copyright 2019 Gary Dhillon
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
#
# Furthermore it is derived from the Python documentation examples thus
# some of the code is Copyright © 2001-2013 Python Software
# Foundation; All Rights Reserved
#
# http://docs.python.org/2/library/socketserver.html
#
# run: python freetests.py

# try: curl -v -X GET http://127.0.0.1:8080/


class MyWebServer(socketserver.BaseRequestHandler):
    
    def handle(self):
        self.data = self.request.recv(1024).strip()
        print ("Got a request of: %s\n" % self.data)
        response = self.parse(self.data)
        self.request.sendall(bytearray(response,'utf-8'))

    def parse(self, data):
        data = data.decode()
        splitData = data.split("\r\n")
        
        request = splitData[0]
        splitRequest = request.split(" ")
        requestType = splitRequest[0]
        path = splitRequest[1]

        headerTemplate = self.requestHandler(requestType, path)
        
        return headerTemplate

    def requestHandler(self, requestType, path):
        if requestType == "GET":
            return self.contentHandler(path)
        else:
            errorCode = 405
            return self.errorHandler(errorCode)

    def errorHandler(self, errorCode):
        if errorCode == 405:
            statusCode = "405 Method not Allowed"
        if errorCode == 404:
            statusCode = "404 Not found"
        errorTemplate = "HTTP/1.1 {fStatusCode}\r\n".format(fStatusCode=statusCode)
        return errorTemplate

    def contentHandler(self, path):
        basePath = os.getcwd() + "/www"
        serverPath = basePath + path
        normalizedServerPath = os.path.realpath(serverPath)

        if os.path.commonprefix([basePath, normalizedServerPath]) == basePath:
            if os.path.exists(normalizedServerPath):
                statusCode = "200 OK"
                isDir = os.path.isdir(normalizedServerPath)

                if isDir:
                    dirServerPath = normalizedServerPath + "/index.html"
                    contentType = mimetypes.guess_type(dirServerPath)
                    contentFile = open(dirServerPath, "r")
                else:
                    contentType = mimetypes.guess_type(normalizedServerPath)
                    contentFile = open(normalizedServerPath, "r")
                
                contentType = "Content-Type: " + contentType[0]
                content = contentFile.read()
                contentTemplate = "HTTP/1.1 {fStatusCode}\r\n{fContentType}\r\n\r\n\{fContent}".format(fStatusCode=statusCode, fContentType=contentType, fContent=content)                
                contentFile.close()
                return contentTemplate
            else:
                errorCode = 404
                return self.errorHandler(errorCode)
        else:
            errorCode = 404
            return self.errorHandler(errorCode)
    
    def redirectHandler(self):
        pass

if __name__ == "__main__":
    HOST, PORT = "localhost", 8080

    socketserver.TCPServer.allow_reuse_address = True
    # Create the server, binding to localhost on port 8080
    server = socketserver.TCPServer((HOST, PORT), MyWebServer)

    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    server.serve_forever()
