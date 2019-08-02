import sqlite3
import requests
from multiprocessing import Manager, Process
from datetime import datetime
from db import Database
from processing_handler import ProcessRunner


def req_foo(url):
    """
    Get page by url and put response
    :param q_res: queue for results
    :param url: page url
    :return: None
    """
    print(f'{url} - start request')
    st = datetime.now()
    try:
        r = requests.get(url)
        print(f'INFO: {url} - GET status {r.status_code} | time: {datetime.now() - st}')
        return r
    except requests.ConnectionError:
        print(f'ERROR: {url} - Connection error | time: {datetime.now() - st}')
    except Exception:
        print(f'ERROR: {url} - Unknown error | time: {datetime.now() - st}')
    return None


def write_res(res):
    """
    Save page content to database from queue
    :param res: http response
    :return: None
    """
    if res is None:
        return None
    db = Database('requsts_res.sqlite3')
    curs = db.connect()
    try:
        curs.execute('''INSERT INTO content_new (url, binary_content) VALUES (?,?)''', (res.url, res._content,))
        db.conn.commit()
    except sqlite3.ProgrammingError as e:
        print('Database Error')
        print(e)
        raise e


def put_test_urls(q_urls):
    for i in range(100):
        q_urls.put(f'http://example{i}.com')


if __name__ == '__main__':
    db = Database('requsts_res.sqlite3')
    curs = db.connect()
    curs.execute('''CREATE TABLE IF NOT EXISTS content_new (id INTEGER PRIMARY KEY AUTOINCREMENT, url TEXT, binary_content BLOB)''')
    db.conn.commit()
    del db

    m = Manager()
    q_res = m.Queue(maxsize=5)
    q_urls = m.Queue(maxsize=10)

    urls_puter = Process(target=put_test_urls, args=(q_urls,), daemon=True)
    urls_puter.start()
    req_runner = ProcessRunner(queue=q_urls, queue_res=q_res, max_workers=3)
    req_runner(req_foo)
    db_runner = ProcessRunner(queue=q_res, max_workers=1)
    db_runner(write_res)
