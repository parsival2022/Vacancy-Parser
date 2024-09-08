import time, random
from typing import Callable, Type, Union, Tuple, Any

def repeat_if_fail(exceptions:Union[Type[Exception], list[Type[Exception]]], wait:Union[int, Tuple[int, int]] = None) -> Any:
    def decorator(func:Callable):
        def wrapper(*args, **kwargs):
                try:
                    return func(*args, **kwargs)
                except exceptions:
                    print("Error occured, trying again.")
                    if wait: 
                        try:
                             t = random.randint(wait)
                        except TypeError:
                             t = wait
                        time.sleep(t)
                    return func(*args, **kwargs)
        return wrapper
    return decorator

def execute_if_fail(exception:Exception, exec:Callable) -> Any:
    def decorator(func:Callable):
        def wrapper(*args, **kwargs):
                try:
                    return func(*args, **kwargs)
                except exception:
                    print("Error occured and corresponding func executed.")
                    return exec()
        return wrapper
    return decorator
