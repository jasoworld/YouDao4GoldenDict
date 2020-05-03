#!/usr/bin/python3
import sys
import time, uuid, hashlib, requests, json

YOUDAO_URL = 'https://openapi.youdao.com/api'
APP_KEY = 这个地方是sr类型
APP_SECRET = 这个地方是str类型

def connect(word: str):
    q = word
    curtime = str(int(time.time()))
    salt = str(uuid.uuid1())
    signStr = APP_KEY + truncate(q) + salt + curtime + APP_SECRET
    sign = encrypt(signStr)

    data = {}
    data['from'] = 'auto'
    data['to'] = 'auto'
    data['signType'] = 'v3'
    data['curtime'] = curtime
    data['appKey'] = APP_KEY
    data['q'] = word
    data['salt'] = salt
    data['sign'] = sign

    response = do_request(data)
    contentType = response.headers['Content-Type']
    if contentType == 'audio/mp3':
        pass
    else:
        print(format(response.content))


def getColoredFont(word: str, color: str) -> str:
    coloredFont = "<font color=" + color + ">" + word + "</font>"
    return str(coloredFont)

# ==================以下为辅助函数=============


def encrypt(sign: str):
    """
    这个函数是为了生成签名
    :param sign:str
    :return:str
    """
    hash_algorithm = hashlib.sha256()
    hash_algorithm.update(sign.encode('utf-8'))
    return hash_algorithm.hexdigest()


def truncate(q:str):
    """
    当查询的单词太长时，截断
    :param q: str
    :return: 若q===None 则返回None，否则返回截断后的str
    """
    if q is None:
        return None
    size = len(q)
    return q if size <= 20 else q[0:10] + str(size) + q[size - 10:size]


def do_request(data:[str, any]):
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    return requests.post(YOUDAO_URL, data=data, headers=headers)


def format(content: bytes) -> str:
    """
    传入的数据为utf-8格式的Json数据，将Json数据格式化为Html
    :param content:
    :return: 格式化后的Html
    """
    jsonData = json.loads(str(content, 'utf-8'))
    # 格式化被查询的单词
    word = '''<p style="color: red; font-weight: bold">%s</p>'''%(sys.argv[1])
    # 格式化音标 当翻译句子时这个段落没有
    phonetic = ''
    try:
        phonetic = '''
                    <table>
                        <tr>
                            <td>英</td>
                            <td style="color: darkorange; font-weight: bold">[%s]</td>
                            <td>&nbsp&nbsp</td>
                            <td>美</td>
                            <td style="color: darkorange; font-weight: bold">[%s]</td>
                        </tr>
                    </table>
                    '''%(jsonData['basic']['uk-phonetic'], jsonData['basic']['us-phonetic'])
    except Exception:
        phonetic = ''
    # 释义列表
    explains = ''
    try:
        explains = '''
        <p style="font-weight: bold">释义</p>
        <ol>
        '''
        for expla in jsonData['basic']['explains']:
            explains += '''<li style="color: blue">%s</li>'''%expla
        explains += '</ol>'
    except Exception:
        explains = ''
        pass
    # 网络释义 这个有可能有，也有可能没有
    web_explains = ''
    try:
        web_explains = '''<p style="font-weight: bold">网络短语</p>'''
        for phrase in jsonData['web']:
            web_explains += '''<li><a>%s：</a>&nbsp''' % phrase['key']
            for value in phrase['value']:
                web_explains += '''&nbsp&nbsp<a style="color: blue">%s</a>'''%value
            web_explains +='</li>'

        web_explains += '</ol>'
    except Exception:
        web_explains = ''
    if((phonetic == '') & (explains == '') & (web_explains == '')):
        word = ''
    return word + phonetic + explains + web_explains

if __name__ == '__main__':
    connect(sys.argv[1])
