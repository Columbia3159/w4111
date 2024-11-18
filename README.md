
# Development
```
pip install -r requirements.txt
cd webserver
python3 server.py
```
#### Optional
```
python3 -m venv path/to/venv  
source path/to/venv/bin/activate
```
# Production
### [Production url](http://34.139.229.63:8111/)
## Start server
```
nohup python3 server.py > flask.log 2>&1 &
```
## Check log
```
tail -f flask.log
```
## Stop server
```
ps aux | grep server.py
kill <PID>
```
