PORT=$(sed -n '6p' < /opt/sdob/sdob.conf)
/usr/local/bin/python3.7 -m http.server $PORT --directory /opt/sdob/
