ps -ef | grep 'start_spider_monitor.py' | grep -v grep | cut -c 9-16| xargs kill -9
cd /data/sql_monitor && python3 start_spider_monitor.py >> ./logs/$(date "+%Y-%m-%d").log 2>&1 &
str=$"\n"
sstr=$(echo -e $str)
echo $sstr
echo "脚本执行成功"
