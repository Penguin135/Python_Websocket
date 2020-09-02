import asyncio;
import websockets;
import os;
import sys;
import json;
import shutil
import string

os.chdir('/')
ndir=nfile=0
make_file_name=''

class Node():
    #생성자
    def __init__(self):
        self.__filename='';
        self.__filesize =0;
        self.__data='';
        self.__datasize=0;

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

    def is_completed(self):
        if self.__filesize == self.__datasize:
            print('Transfer is finished')
            return True;
        else:
            return False;
    def save(self, data):
        with open("/tmp/sdob/"+self.__filename, "ab+") as handle:
            handle.write(data);
        self.__datasize += len(data)


# 클라이언트가 '파일 업로드'버튼을 클릭하면 호출
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
    json_dirList = json.dumps({"kinds": "directory", "list": available_drives})

    while True:
        data = await websocket.recv();
        print(data);
        json_data = json.loads(data);
        if json_data['kinds']=='password' and json_data['text']==wsConPwd:
            break;
        else:
            json_transfer=json.dumps({"kinds": "disconnect"})
            await websocket.send("{}".format(json_transfer))
            continue;

    await websocket.send("{}".format(json_dirList))
    global fileName
    global curLink

    while True:
        #클라이언트가 'send'버튼으로 text를 전송할 때까지 대기
        data = await websocket.recv();#받는 데이터는 json형태(kinds, text)

        json_data = json.loads(data)#받은 데이터를 json으로 변환

        #..디렉토리 클릭
        if json_data['kinds']=='chdir' and json_data['text']=='..' and os.getcwd() in available_drives :
            json_dirList = json.dumps({"kinds": "directory", "list": available_drives})
            await websocket.send("{}".format(json_dirList))

        #다른 디렉토리 클릭
        elif json_data['kinds']=='chdir':
            if os.path.isfile(json_data['text']):
                break

            os.chdir(json_data['text']+'/')
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

        #파일 및 디렉토리 제거
        elif json_data['kinds']=='remove':
            dirPath=os.getcwd()
            targetName=json_data['text']
            if os.path.isfile(targetName):
                os.remove(targetName)
            elif os.path.isdir(targetName):
                item=os.path.join(dirPath,targetName)
                shutil.rmtree(item)

            os.chdir('..')
            os.chdir(dirPath)

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

        #이름 변경
        elif json_data['kinds']=='namemodify':
            srcName=json_data['text']
            dstName=json_data['text2']
            os.rename(srcName,dstName)
            
            curLink=os.getcwd()
            os.chdir('..')
            os.chdir(curLink)

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

        elif json_data['kinds']=='modify':
            print('modify started!')
            fileName=json_data['text']
            print('file name:')
            print(fileName)
            f=open(fileName,mode='r+',encoding='utf-8')
            texts=json.dumps({"kinds":"modify","text":f.read()})
            print('texts:')
            print(texts)
            await websocket.send("{}".format(texts));
            f.close()

        elif json_data['kinds']=='modify2':
            fd=open(fileName,mode='w+',encoding='utf-8')
            fd.write(json_data['texts'])
            print('{}'.format(json_data['texts']))
            fd.close()

            curLink=os.getcwd()
            os.chdir('..')
            os.chdir(curLink)

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

        elif json_data['kinds']=='makedir':
            make_dir_name = json_data['text']
            os.mkdir(os.getcwd()+ "/"+make_dir_name+ "/")
            curLink=os.getcwd()
            os.chdir('..')
            os.chdir(curLink)

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

        #파일 생성
        elif json_data['kinds'] == 'makename':
            make_file_name = json_data['text']

        elif json_data['kinds'] == 'maketext':
            make_file_text = json_data['text']
            if make_file_name == '':
                print('file name is null')
            else:
                print('make-name:', make_file_name)
                print('make-text:', make_file_text)
                print(os.getcwd())
                fdd=os.open(make_file_name,os.O_CREAT|os.O_RDWR)
                os.write(fdd,bytes(make_file_text,encoding='utf8'))
                os.close(fdd)
                make_file_name=''
                make_file_text=''

            curLink=os.getcwd()
            os.chdir('..')
            os.chdir(curLink)

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

        #파일 복사
        elif json_data['kinds']=='copy':
            targetName=json_data['text']
            targetLink=os.getcwd()
            print(targetLink)

        #파일 붙여넣기
        elif json_data['kinds']=='paste':
            print(targetLink, targetName)
            shutil.copy(targetLink+"/"+targetName,os.getcwd()+ "/copy_"+targetName)

            curLink=os.getcwd()
            os.chdir('..')
            os.chdir(curLink)

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
            
        elif json_data['kinds']=='cancel':
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

#main start.
#get informations(ip address, port number) from sdob.conff = open("sdob.conf", 'r')
f = open("/opt/sdob/sdob.conf", 'r')
lines = f.read().splitlines()

confValues=[]

for i in range(0, len(lines)):
    if lines[i][0] == '#':
        continue
    else:
        confValues.append(lines[i])

ipAddr=confValues[0]
portNum=int(confValues[1])
wsConPwd=confValues[3]
print(wsConPwd)
f.close()

# 파일 전송용 웹 소켓 서버 생성.호스트는 localhost에 port는 8080으로 생성한다.
start_server = websockets.serve(file_accept, ipAddr, portNum);

# 파일 전송용이 아닌 웹 소켓 서버 성생. 호스트는 localhost에 port는 80801로 생성
start_server_text = websockets.serve(text_accept,  ipAddr, portNum+1);

# 비동기로 서버를 대기한다.
asyncio.get_event_loop().run_until_complete(start_server);
asyncio.get_event_loop().run_until_complete(start_server_text);
asyncio.get_event_loop().run_forever();

