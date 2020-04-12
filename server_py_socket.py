import socket
import threading
import re
import hashlib
import base64
import struct
import subprocess
import sys
import os

def send(client, msg):
    try:
        data = bytearray(msg.encode('utf-8'))
        print('hello5')
        print('\x81')
        if len(data) > 126:
            data = bytearray([129, 126]) + bytearray(struct.pack('>H', len(data))) + data
        else:
            data = bytearray([129, len(data)]) + data
        
        client.send(data)
        return 0
    except Exception as e:
        print("send ERROR : " + str(e))
        return -1
    #client.send(data)


def recv(client):
    
    first_byte = bytearray(client.recv(1))[0]
    FIN = (0xFF & first_byte) >> 7
    opcode = (0x0F & first_byte)
    second_byte = bytearray(client.recv(1))[0]
    mask = (0xFF & second_byte) >> 7
    payload_len = (0x7F & second_byte)
    if opcode < 3:
        if (payload_len == 126):
            payload_len = struct.unpack_from('>H', bytearray(client.recv(2)))[0]
        elif (payload_len == 127):
            payload_len = struct.unpack_from('>Q', bytearray(client.recv(8)))[0]
        if mask == 1:
            masking_key = bytearray(client.recv(4))
            masked_data = bytearray(client.recv(payload_len))
        if mask == 1:
            data = [masked_data[i] ^ masking_key[i%4] for i in range(len(masked_data))]
        else:
            data = masked_data
    else:
        return opcode, bytearray(b'\x00')
    print(bytearray(data).decode('utf-8', 'ignore'))#받은거 콘솔에 출력용
    return opcode, bytearray(data)

def handshake(client):
    request = client.recv(2048)
    p=re.compile('Sec-WebSocket-Key: (.*)\\r')
    m = p.search(request.decode())

    #print(request)
    
    key = m.group(1)+'258EAFA5-E914-47DA-95CA-C5AB0DC85B11'
    #key = 'dGhlIHNhbXBsZSBub25jZQ=='+'258EAFA5-E914-47DA-95CA-C5AB0DC85B11'
    h=hashlib.sha1()
    h.update(key.encode())

    print('\n')
    
    #sh1_key = hashlib.sha1().digest()
    base64_key = base64.b64encode(h.digest())
    #print(base64_key.decode())

    response = "HTTP/1.1 101 Switching Protocols\r\n"+\
           "Upgrade: websocket\r\n"+\
           "Connection: Upgrade\r\n"+\
           "Sec-WebSocket-Accept: %s\r\n"+\
           "\r\n"

    r = response % (base64_key.decode())
    #print(r)
    client.send(r.encode())
    
def handle_client (client, addr):
    print('working\n')
    handshake(client)


    try:
        while 1:
            opcode, data = recv(client)
            if opcode == 0x8:
                print('close frame received')
                break
            elif opcode == 0x1:
                if len(data) == 0:
                    break
                msg = data.decode('utf-8', 'ignore')
                print(msg)
                send(client, msg)
                print('hello4')#여기 실행 안됨. send 안에 문제가 있음.
                
                output = str(subprocess.check_output(msg, stderr=subprocess.STDOUT, shell=True), 'euc-kr')
                os.chdir('/')
                
                print(os.getcwd())
                send(client, output)
            else:
                print('frame not handled : opcode=' + str(opcode) + ' len=' + str(len(data)))
                 
    except Exception as e:
        print(str(e))
        
    print("disconnected")
    client.close()


def run_server(port):
    sock = socket.socket()
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind(('',port))
    sock.listen(5)
    
    

    while True:
        print('Waiting for connection on port' + str(port) + '...')
        client, addr = sock.accept()
        print('Connection from : ' + str(addr))
        threading.Thread(target = handle_client, args = (client, addr)).start()
    #msg = client.recv(1024)
    #print(f'{msg.decode()}')
    
    #print(msg.decode('utf-8'))
    #conn.send(b'{msg}')
    sock.close()

if __name__ == '__main__':
  run_server(9999)
