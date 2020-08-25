import asyncio;
# 웹 소켓 모듈을 선언한다.
import websockets;
import socket;

#아래서부터 파일 관련 패키지
import os;
import sys;
import json;
import shutil
import string
#기본 경로
#os.chdir('D:')
os.chdir('/')
ndir=nfile=0

# 업로드 할 때 데이터 정보에 관한 클래스
class Node():
    #생성자
    def __init__(self):
        self.__filename=''; # 받는 파일의 이름
        self.__filesize =0; # 받는 파일의 크기
        self.__data='';     # 받는 파일의 내용(클라이언트에서 정한 버퍼 사이즈 만큼씩 받는다)
        self.__datasize=0;  # 받은 파일의 사이즈

    # filename getter
    @property
    def filename(self):
        return self.__filename;

    # filename setter
    @filename.setter
    def filename(self, filename):
        self.__filename=filename;

    # filesize getter
    @property
    def filesize(self):
        return self.__filesize;

    # filesize setter
    @filesize.setter
    def filesize(self, filesize):
        self.__filesize=int(filesize);

    # data getter
    @property
    def data(self):
        return self.__data;

    # data setter
    @data.setter
    def data(self, data):
        self.__data = data;

    @property
    def datasize(self):
        return self.__datasize;

    @datasize.setter
    def datasize(self, length):
        self.__datasize += length;

    # add data to self.__data
    def add_data(self, data):
        self.__data += data;

    # 파일전송이 끝났는지 확인하는 함수
    def is_completed(self):
        if self.__filesize == self.__datasize:
            print('transfering finished')
            return True;
        else:
            return False;
    def save(self, data):
        # 파일을 binary형식, 이어붙이는 모드로 연뒤에 파일을 계속 이어쓴다
        with open("C:/Users/rudwn/OneDrive/문서/WS/"+self.__filename, "ab+") as handle:
            handle.write(data);
        # 받은 datasize를 받은 데이터 size를 더해가며 저장한다(전송 종료 조건에 사용)
        self.__datasize += len(data)


# 클라이언트가 '파일 업로드'버튼을 클릭하면 호출된다.
async def file_accept(websocket, path):
    node = Node(); # node에 Node() 클래스 할당
    while True:
        # 클라이언트로부터 메시지를 대기한다.
        message = await websocket.recv();
        if message == 'START': #클라이언트로부터 'START' 메시지가 날라오면
            await websocket.send("FILENAME"); #파일 이름을 요청
        elif message == 'FILENAME': #파일 이름을 받는다
            node.filename = await websocket.recv();
            await websocket.send("FILESIZE")
        elif message == 'FILESIZE': #파일 사이즈를 받는다
            node.filesize = await websocket.recv();
            await websocket.send("DATA");#데이터를 요청한다
        elif message == 'DATA':#데이터가 오면 저장한다
            node.save(await websocket.recv());
            if node.is_completed() == False:#전송이 끝나지 않았으면 계속 전송
                await websocket.send("DATA");
            else:
                await websocket.close();#전송이 끝났으면 웹소켓을 닫고 종료
                break;

async def text_accept(websocket, path):
    available_drives = ['/']
    #print(available_drives)
    #print(os.listdir())
    #allList=os.listdir(os.getcwd())
    #print(allList)
    #dirList=['..']
    #fileList=[]
    #for i in os.listdir():
    #    if os.path.isfile(i):
    #        fileList.append(i)
    #    else:
    #        dirList.append(i)
    json_dirList = json.dumps({"kinds": "directory", "list": available_drives})
    #json_fileList = json.dumps({"kinds": "directory", "list": fileList})

    #드라이블 경로로 가기 위해서는 C: 이 아닌 C:\ 이렇게 필요해서 끝에 \를 붙여줌
    #for i in range(len(available_drives)):
    #    available_drives[i] = available_drives[i] + '\\'
    #    print(available_drives[i])


    #json_fileList = json.dumps({"kinds": "filelist", "list": fileList})
    #await websocket.send("{}".format(dirList))
    await websocket.send("{}".format(json_dirList))
    #await websocket.send("{}".format(json_fileList))
    while True:
        #클라이언트가 'send'버튼으로 text를 전송할 때까지 대기
        data = await websocket.recv();#받는 데이터는 json형태(kinds, text)
        json_data = json.loads(data)#받은 데이터를 json으로 변환

        if json_data['kinds']=='chdir' and json_data['text']=='..' and os.getcwd() in available_drives :
            json_dirList = json.dumps({"kinds": "directory", "list": available_drives})
            await websocket.send("{}".format(json_dirList))
        elif json_data['kinds']=='chdir':
            #print(type(json_data['text']))
            #print(os.getcwd())
            os.chdir(json_data['text'])
            dirList=['..']
            fileList=[]
            for i in os.listdir():
                if os.path.isfile(i):
                    fileList.append(i)
                else:
                    dirList.append(i)

            json_dirList = json.dumps({"kinds": "directory", "list": dirList})
            json_fileList = json.dumps({"kinds": "filelist", "list": fileList})
            await websocket.send("{}".format(json_dirList));
            await websocket.send("{}".format(json_fileList));

        #print("received : " + data);


def network_info():
    host = socket.gethostname()
    ip_addr = socket.gethostbyname(host)
    print('HOST:' + host)
    print("ip Address:" + ip_addr)
    return ip_addr


ip = network_info()

# 파일 전송용 웹 소켓 서버 생성.호스트는 localhost에 port는 8080으로 생성한다.
start_server = websockets.serve(file_accept, '172.30.1.23', 9998);

# 파일 전송용이 아닌 웹 소켓 서버 성생. 호스트는 localhost에 port는 80801로 생성
start_server_text = websockets.serve(text_accept,  '172.30.1.23', 9999);

# 비동기로 서버를 대기한다.
asyncio.get_event_loop().run_until_complete(start_server);
asyncio.get_event_loop().run_until_complete(start_server_text);
asyncio.get_event_loop().run_forever();
