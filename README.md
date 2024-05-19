# UCS algorithm wrapper service

# Requirements
1. Python 3.8.x+
2. Flask
 
# How to use
Please refer to [demo.py](demo.py)

# Output format
Results from ```alg.infer()``` should be in following format:

```json
{
    "tid": "task_id",
    "sources": ["(optional) input sources"],
    "ts_task": "timestamp in milliseconds",
    "ts_result": "timestamp in milliseconds",
    "vals": ["result values container"],
    "explain": ["result explained in text"]
}
```
# License
Copyright 2024 [East China Jiaotong University](http://www.ecjtu.edu.cn)

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.