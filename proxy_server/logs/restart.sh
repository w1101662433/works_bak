ps -ef | grep 'python3 start_proxy_server.py' | grep -v grep | cut -c 9-15| xargs kill -9
cd /data/proxy_server && python3 start_proxy_server.py >> ./logs/$(date "+%Y-%m-%d").log 2>&1 &
str=$"\n"
sstr=$(echo -e $str)
echo $sstr
echo "脚本执行成功"
