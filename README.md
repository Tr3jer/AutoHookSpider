# AutoHookSpider

    将自动爬虫的结果判断是否属于hooks，属于则入库，并不断抓取url爬啊爬。

![](http://7xiw31.com1.z0.glb.clouddn.com/4rfedsxz.png)

```
AutoHookSpider
├── LICENSE
├── README.md
├── hooks.txt   #hooks字典，随机放了200个，可以自己收集。
├── lib
│   ├── __init__.py
│   ├── common.py   #琐碎功能
│   └── record.sql  #先在Mysql创建这个表
├── main.py #主程序
└── requirements.txt
```

1. sudo pip install -r requirements.txt
2. lib/record.sql into mysql
3. usage: python main.py {Options} [ google.com,twitter.com,facebook.com | -t 20 ]
4. 或者直接`python main.py`会直接在hooks.txt抽取(thread_cnt)个入口域名。

![](http://7xiw31.com1.z0.glb.clouddn.com/4trefds.png)
