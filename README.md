# Python_Websocket
server : python, client : web (javascript web browser)

### 프로젝트 소개
목적:본 프로젝트는 Linux(centos) PC 또는 가상머신을 대상으로 파일 및 디렉토리 관리를 웹 브라우저에서 제공되는 UI를 통해 손쉽게 관리할 수 있도록 하는 rpm 패키지 개발

### 설치 방법
sdob 패키지 설치 방법.pdf 파일 참고

### 설치 파일 설명
/opt/sdob/ 경로에 필요한 파일들이 설치됨  
directory.png  index.html           sdob-web.service  sdob.target  webserver.sh
file.png       sdob-server.service  sdob.conf         server.py

service 세 가지가 등록됨  
sdob-server.service
sdob-web.service
sdob.target

/tmp/sdob/ 디렉토리가 생성됨  
파일 전송 사용시, 이 디렉토리에 파일이 전송됨
