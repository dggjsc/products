#!/bin/bash
echo "Copying IBM Cloud apikey into development environment..."
docker cp ~/.bluemix/apikey.json products:/home/vscode 
docker exec products sudo chown vscode:vscode /home/vscode/apikey.json
echo "Complete"
