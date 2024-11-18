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
