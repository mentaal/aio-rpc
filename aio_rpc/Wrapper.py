from .ObjectWrapper import ObjectWrapper

class Wrapper(ObjectWrapper):
    '''Simple subclass which takes a cls and instantiates it  with the provided
    arguments.

    Args:
        cls (Class): The class or callable to instantiate and serve. If cls is a
        callable, it is expected that calling it returns an instantiation of a
        class which will then be served.

        cls_args (dict): keyword arguments for the callable
        kwargs (dict): cls keyword argumnets
    '''

    def __init__(self, cls, *, cls_args=None, **kwargs):
        if cls_args==None:
            cls_args = {}

        cls_obj = cls(**cls_args)
        super().__init__(obj=cls_obj, **kwargs)

