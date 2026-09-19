import time

def timeit(method):
    def timed(*args, **kw):
        ts = time.time()
        result = method(*args, **kw)
        te = time.time()
        name = kw.get('timeitLoggerName', method.__name__+ str(args[1:]))      #avoid self in the args
        if 'timeitLogger' in kw:
            kw['timeitLogger'][name] = int((te - ts) * 1000)
        else:
            print('%r %2.2f ms' % (name, (te - ts) * 1000))
        return result
    return timed