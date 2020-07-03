from racketinterpreter.predefined.controlflow import If
from racketinterpreter.predefined.boolean import (
    And, BooleanHuh, BooleanSymbolEqualHuh, BooleanToString, FalseHuh, Or, Not
)
from racketinterpreter.predefined.numeric import (
    SymbolPlus, SymbolMinus, SymbolMultiply, SymbolDivide, SymbolEqual, SymbolLessThan, SymbolGreaterThan,
    SymbolLessEqualThan, SymbolGreaterEqualThan, Abs, Add1, Ceiling, CurrentSeconds, EvenHuh, ExactToInexact, ExactHuh,
    Exp, Floor, Gcd, IntegerHuh, Lcm, Log, Max, Min, Modulo, NegativeHuh, NumberToString, NumberHuh, OddHuh,
    PositiveHuh, RationalHuh, RealHuh, Round, Sgn, Sqr, Sqrt, Sub1, ZeroHuh
)
from racketinterpreter.predefined.string import (
    StringHuh
)


BUILT_IN_PROCS = {
    # control flow
    'if': If(),
    # numeric
    '+': SymbolPlus(),
    '-': SymbolMinus(),
    '*': SymbolMultiply(),
    '/': SymbolDivide(),
    '=': SymbolEqual(),
    '<': SymbolLessThan(),
    '>': SymbolGreaterThan(),
    '<=': SymbolLessEqualThan(),
    '>=': SymbolGreaterEqualThan(),
    'abs': Abs(),
    'add1': Add1(),
    'ceiling': Ceiling(),
    'current-seconds': CurrentSeconds(),
    'even?': EvenHuh(),
    'exact->inexact': ExactToInexact(),
    'exact?': ExactHuh(),
    'exp': Exp(),
    'floor': Floor(),
    'gcd': Gcd(),
    'integer?': IntegerHuh(),
    'lcm': Lcm(),
    'log': Log(),
    'max': Max(),
    'min': Min(),
    'modulo': Modulo(),
    'negative?': NegativeHuh(),
    'number->string': NumberToString(),
    'number?': NumberHuh(),
    'odd?': OddHuh(),
    'positive?': PositiveHuh(),
    'rational?': RationalHuh(),
    'real?': RealHuh(),
    'round': Round(),
    'sgn': Sgn(),
    'sqr': Sqr(),
    'sqrt': Sqrt(),  # cannot handle negative numbers for now
    'sub1': Sub1(),
    'zero?': ZeroHuh(),
    # boolean
    'and': And(),
    'boolean->string': BooleanToString(),
    'boolean=?': BooleanSymbolEqualHuh(),
    'boolean?': BooleanHuh(),
    'false?': FalseHuh(),
    'not': Not(),
    'or': Or(),
    # string
    # 'string-alphabetic?': StringAlphabeticHuh(),
    # 'string-append': StringAppend(),
    # 'string-contains?': StringContainsHuh(0,
    # 'string-downcase': StringDowncase(),
    # 'string-ith': StringIth(),
    # 'string-length': StringLength(),
    # 'string-lower-case?': StringLowerCaseHuh(),
    # 'string-numeric?': StringNumericHuh(),
    # 'string-upcase': StringUpcase(),
    # 'string-upper-case?': StringUpperCaseHuh(),
    # 'string-whitespace': StringWhitespace(),
    # 'string<=?': StringSymbolLessEqualHuh(),
    # 'string<?': StringSymbolLessHuh(),
    # 'string=?': StringSymbolEqualHuh(),
    # 'string>=?': StringSymbolGreaterEqualHuh(),
    # 'string>?': StringSymbolGreaterHuh(),
    'string?': StringHuh(),
    # 'substring': Substring()
}
