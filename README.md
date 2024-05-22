# UCS algorithm wrapper service

# Requirements
1. Python 3.8.x+
2. Flask

# How to use
Please refer to [demo.py](test/demo.py)

# Principles & practice

## 1. Alg
An Alg is the wrapper of a specific algorithm. It has 2 mode:

### [1] Stream mode
The stream mode is used to process data in real-time. The Alg will be initialized once and keep running until the service is stopped. The Alg will process data in real-time and return the result in real-time.

The following streams are supported:
1. MQ subscription
2. TCP connection
3. media streams, e.g. RTSP, RTMP, HLV

Input sources should contain at least one streams, and may contain some meta data, e.g. global file, hyperparameters, etc.
Input sources should be in the following format:
```json
{
  "sources":
  [
    "tcp",
    "rtsp",
    "http"
  ],
  "meta": {
    "meta1": "value1",
    "meta2": "value2"
  }
}
```

Alg in stream mode is suggested to be configured with a MQ output destination or a TSDB

### [2] Batch mode
The batch mode refers to the classical discrete task submission. It takes the input of AlgTask wraps the task information as:

## 2. AlgTask
An AlgTask wraps the algorithm task information in either stream mode or batch mode.
```json
{
  "task_id": "task_id",
  "task_ts": "timestamp in milliseconds",
  "sources": [
  "http://",
  "rtsp://"],
  "meta_data": {
    "meta1": "value1",
    "meta2": "value2"
  }
}
```

## 3. AlgResult  
Results from ```alg.infer_batch()```  or ```alg.infer_stream()```should be in following format:

```json
{
    "task_id": "task_id",
    "alg_task": "wraps of alg_task",
    "result_ts": "timestamp in milliseconds",
    "vals": {"val1":"result values container"},
    "explain": "result explained in plain text"
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