from concurrent.futures import ThreadPoolExecutor
from multiprocessing import Process
from functools import wraps


class ProcessRunner(object):
    """
    ProcessRunner class call task in background
        max_workers - max threads for task
        task use queue (multiprocessing.Manager.Queue):
            queue - get args for task
            queue_res - if not None result task store in it queue
    Example:
        q = multiprocessing.Manager.Queue()
        # put args to q
        ...
        q.put(arg)
        q_res = multiprocessing.Manager.Queue()
        pr1 = ProcessRunner(2, queue=q, queue_res=q_res)
        pr1(task)                                       # process run task and store result in queue_res
        pr2 = ProcessRunner(2, queue=q_res)
        pr2(task)                                       # process save result
    """

    def __init__(self, max_workers=5, queue=None, queue_res=None):
        self.max_workers = max_workers
        self.stopper = False
        self.queue = queue
        self.queue_res = queue_res
        self.workers = []
        self.proc = None

    def __call__(self, func, *args, **kwargs):
        """
        Call process with task in threading

        :param func: task function
        :param args and kwargs: other params not from queue or queue_res
        :return: None
        """
        self.proc = Process(target=self.threading, args=(func, *args), kwargs=kwargs, daemon=True)
        self.proc.start()

    def threading(self, func, *args, **kwargs):
        """
        Run workers for task in loop
        :param func: task
        :param args and kwargs: other params not from queue or queue_res
        :return:
        """
        with ThreadPoolExecutor(max_workers=self.max_workers) as worker:
            self.workers.append(worker)
            self._in_loop(func, worker, *args, **kwargs)

    def _in_loop(self, func, worker, *args, **kwargs):
        """
        Run worker in loop
        :param func: task
        :param worker: worker
        :param args and kwargs: other params not from queue or queue_res
        :return:
        """
        while True:
            if self.stopper:
                break
            if self.queue_res:
                func = self._put_result(func)
            worker.submit(func, self.queue.get(), *args, **kwargs)
        worker.shutdown()
        return None

    def _put_result(self, f):
        """
        If put result in queue_res
        :param f: task
        :return: wrapped task
        """
        @wraps(f)
        def wrapp(*args, **kwargs):
            res = f(*args, **kwargs)
            self.queue_res.put(res)
        return wrapp

    def close(self):
        """
        Stop all workers and close process runner
        :return: None
        """
        self.stopper = True
        while self.workers:
            continue
        self.proc.terminate()
