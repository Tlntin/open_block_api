from threading import Thread


class MyThread(Thread):
    """
    自定义多线程
    """

    def __init__(self, func, args):
        super(MyThread, self).__init__()
        self.func = func
        self.args = args
        self.result = "error"  # 默认为错误

    def run(self):
        # 如果能取到数，至少应该是None
        self.result = self.func(*self.args)

    def get_result(self):
        return self.result
