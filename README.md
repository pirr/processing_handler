# processing_handler
Process handler for tasks with queues
processing_handler include ProcessRunner class

ProcessRunner class call task in background
        max_workers - max threads for task
        task use queue (multiprocessing.Manager.Queue):
            queue - get args for task
            queue_res - if not None result task store in it queue
    Example:
        
        >>> q = multiprocessing.Manager.Queue()
           # put args to q
           ...
        >>> q.put(arg)
        >>> q_res = multiprocessing.Manager.Queue()
        >>> pr1 = ProcessRunner(2, queue=q, queue_res=q_res)
        >>> pr1(task)                                       # process run task and store result in queue_res
        >>> pr2 = ProcessRunner(2, queue=q_res)
        >>> pr2(task)                                       # process save result
        >>> pr1.close()                                     # stop process pr1
        >>> pr2.close()                                     # stop process pr2
        
        
        
Work example is async_requests.py
        
        >>> python async_requests.py
