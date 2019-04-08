from concurrent import futures

import sys      #pip3 install sys
sys.path.append('./generated')
sys.path.append('./proto')
sys.path.append('./utils')
import grpc
import fileService_pb2_grpc
import fileService_pb2
import heartbeat_pb2_grpc
import heartbeat_pb2
import sys
import time
import yaml
import threading
import os

def getFileData():
    #fileName = 'fileToBeUploaded.img'
    fileName = input("Enter filename:")
    outfile = os.path.join('files', fileName)
    file_data = open(outfile, 'rb').read()
    fileData = fileService_pb2.FileData(fileName=fileName, data=file_data)
    return fileData

def getFileChunks():
     # Maximum chunk size that can be sent
    CHUNK_SIZE=4000000

    # Location of source image
    username = input("Enter Username: ")
    fileName = input("Enter filename: ")

    # This file is for dev purposes. Each line is one piece of the message being sent individually
    outfile = os.path.join('files', fileName)
    
    sTime=time.time()
    with open(outfile, 'rb') as infile:
        while True:
            chunk = infile.read(CHUNK_SIZE)
            if not chunk: break

            # Do what you want with each chunk (in dev, write line to file)
            yield fileService_pb2.FileData(username=username, filename=fileName, data=chunk, seqNo=1)
    print("Time for upload= ", time.time()-sTime)


def downloadTheFile(stub):
    userName = input("Enter Username: ")
    fileName = input("Enter file name: ")
    data = bytes("",'utf-8')
    sTime=time.time()
    responses = stub.DownloadFile(fileService_pb2.FileInfo(username=userName, filename=fileName))
    #print(responses)
    for response in responses:
        fileName = response.filename
        data += response.data
    
    print("Time for Download = ", time.time()-sTime)
    filePath=os.path.join('downloads', fileName)
    saveFile = open(filePath, 'wb')
    saveFile.write(data)
    saveFile.close()
    
    print("File Downloaded - ", fileName)


def uploadTheFileChunks(stub):
    #fileData = getFileData()
    
    response = stub.UploadFile(getFileChunks())
    if(response.success): print("File successfully Uploaded")
    else:
        print("Failed to upload. Message - ", response.message)

def deleteTheFile(stub):
    userName = input("Enter Username: ")
    fileName = input("Enter file name: ")
    response = stub.FileDelete(fileService_pb2.FileInfo(username=userName, filename=fileName))
    print(response.message)

def isFilePresent(stub):
    userName = input("Enter Username: ")
    fileName = input("Enter file name: ")
    response = stub.FileSearch(fileService_pb2.FileInfo(username=userName, filename=fileName))

    if(response.success==True):
        print(response.message)
    else:
        print(response.message)

def handleUserInputs(stub):
    print("===================================")
    print("1. Upload a file")
    print("2. Download a file.")
    print("3. Delete a file")
    print("4. Check if a file present")
    print("===================================")
    option = input("Please choose an option.")

    if(option=='1'):
        uploadTheFileChunks(stub)
    elif(option=='2'):
        downloadTheFile(stub)
    elif(option=='3'):
        deleteTheFile(stub)
    elif(option=='4'):
        isFilePresent(stub)

def run_client(serverAddress):
    with grpc.insecure_channel(serverAddress) as channel:
        try:
            grpc.channel_ready_future(channel).result(timeout=1)
        except grpc.FutureTimeoutError:
            print("Connection timeout. Unable to connect to port ")
            exit()
        else:
            print("Connected")
        stub = fileService_pb2_grpc.FileserviceStub(channel)
        #print("Stub--->", stub)
        handleUserInputs(stub)


if __name__ == '__main__':
    run_client('localhost:9000')
