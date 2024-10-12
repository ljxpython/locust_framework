


# 框架编写
文件结构如下：
```bash
├── src/
│   ├── some_file.py
├── locustfiles/
│   ├── locustfile1.py
│   ├── locustfile2.py
│   └── more_files/
│       ├── locustfile3.py
│       ├── _ignoreme.py
│   └── shape_classes/
│       ├── DoubleWaveShape.py
│       ├── StagesShape.py

```

```bash
locust -f locustfiles --class-picker
```
