class Constants:

    # can be modified at runtime
    SHOULD_LOG_SCOPE = True
    SHOULD_LOG_STACK = True


C = Constants()


def init(should_log_scope: bool = C.SHOULD_LOG_SCOPE,
         should_log_stack: bool = C.SHOULD_LOG_STACK) -> None:
    global C
    C.SHOULD_LOG_SCOPE = should_log_scope
    C.SHOULD_LOG_STACK = should_log_stack
