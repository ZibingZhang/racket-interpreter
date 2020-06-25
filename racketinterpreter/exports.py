def interpret(code: str):
    from racketinterpreter.util import Util
    outputs = list(map(str, Util.text_to_result(code)))
    return outputs,
