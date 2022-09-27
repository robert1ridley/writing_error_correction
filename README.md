# 语法纠错

### 文档说明

#### 运行环境
* Python 3.9.13

#### 设置环境
* 输入 `cd writing_error_correction`
* 生成一个虚拟环境: `python3 -m venv venv`
* 启动虚拟环境：`source venv/bin/activate`
* 下载dependencies：`pip install -r requirements_v2.txt`

#### 额外的依赖性
* Java >= 8

#### 运行说明
* `export FLASK_APP=application_v2.py`
* `flask run`
* 目前 端口设置 为5000

#### DEVELOPMENT URL
* http://127.0.0.1:5000/api/v1/textCheck

### PRODUCTION
* Use Gunicorn as WSGI server in combination with pm2.
* To run gunicorn, `gunicorn --bind 0.0.0.0:5000 application_v2:app`
* To run gunicorn persistently with pm2, `pm2 --name=application_v2 start "gunicorn --bind 0.0.0.0:5000 application_v2:app"`

#### HTTP请求方式
* POST

#### 提交参数
| 参数名		| 必填  	| 类型		| 说明 				  	        |
| ----------|:-----:| ---------:|------------------------------:|
| text   	| Y    	| string 	| 需要纠错的文本，必填，字符串类型  	|

#### 返回参数
| 参数名		            | 说明  	               | 举例 				                                               |
| ----------------------|:--------------------:|------------------------------------------------------------------:|
| data   	            | 错误信息              | 该值为json格式数组                                                  |
| word   	            | 出错词汇              | he     	                                                           |
| type   	            | 警告类型              | spelling /grammar                                                 |
| substitute   	        | 替换词                | him            	                                               |
| description           | 警告说明              | objective male pronoun, used to refer to a male human or animal   |
| existence             | 词汇是否存在           | true (布尔值)                                                      |
| explanation           | 错误解释    	       | that male; objective male pronoun                                 |
| example             	| 警告正确示例           | 该值为json格式三维数组       	                                       |
| example.0.incorrect   | 示例第一条的错误举例    | She likes he.                                                     |
| example.0.correct     | 示例第一条的正确举例    | 该值为一维数组                           	|

#### 返回例子
请求：
```
{
	"text": "They doesn't like chiken."
}
```

返回：
```
{
    "errno": 0,
    "message": "success",
    "data": [
        {
            "word": "doesn't",
            "substitute": "don't",
            "description": "Possible verb agreement error — use the base form here.",
            "from": 5,
            "to": 12,
            "explanation": "Possible verb agreement error — use the base form here.",
            "existence": true,
            "type": "grammar",
            "example": [
                {
                    "correct": [
                        "They don't like chiken."
                    ],
                    "incorrect": "They doesn't like chiken."
                }
            ]
        },
        {
            "word": "chiken",
            "substitute": "chicken",
            "description": "Possible spelling mistake found.",
            "from": 18,
            "to": 24,
            "explanation": "Possible spelling mistake found.",
            "existence": true,
            "type": "spelling",
            "example": [
                {
                    "correct": [
                        "They doesn't like chicken.",
                        "They doesn't like chi ken."
                    ],
                    "incorrect": "They doesn't like chiken."
                }
            ]
        }
    ]
}
```


