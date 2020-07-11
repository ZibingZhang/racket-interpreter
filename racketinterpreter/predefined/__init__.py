from racketinterpreter.predefined.controlflow import (
    If
)
from racketinterpreter.predefined.boolean import (
    And,
    BooleanHuh,
    BooleanSymEqualHuh,
    BooleanToString,
    FalseHuh,
    Or,
    Not
)
from racketinterpreter.predefined.list import (
    ConsHuh,
    EmptyHuh,
    First,
    List,
    Rest
)
from racketinterpreter.predefined.numeric import (
    SymMultiply,
    SymPlus,
    SymMinus,
    SymDivide,
    SymLessThan,
    SymLessEqualThan,
    SymEqual,
    SymGreaterThan,
    SymGreaterEqualThan,
    Abs,
    Add1,
    Ceiling,
    CurrentSeconds,
    EvenHuh,
    ExactToInexact,
    ExactHuh,
    Exp,
    Floor,
    Gcd,
    IntegerHuh,
    Lcm,
    Log,
    Max,
    Min,
    Modulo,
    NegativeHuh,
    NumberToString,
    NumberHuh,
    OddHuh,
    PositiveHuh,
    RationalNumHuh,
    RealHuh,
    Round,
    Sgn,
    Sqr,
    Sqrt,
    Sub1,
    ZeroHuh
)
from racketinterpreter.predefined.string import (
    StringAlphabeticHuh,
    StringAppend,
    StringContainsHuh,
    StringCopy,
    StringDowncase,
    StringIth,
    StringLength,
    StringLowerCaseHuh,
    StringNumericHuh,
    StringUpcase,
    StringUpperCaseHuh,
    StringWhitespaceHuh,
    StringHuh
)
from racketinterpreter.predefined.symbol import (
    SymbolToString,
    SymbolSymEqualHuh,
    SymbolHuh
)


BUILT_IN_PROCS = {
    # ========== ========== ==========
    #           control flow
    # ========== ========== ==========
    'if': If(),
    # ========== ========== ==========
    #             boolean
    # ========== ========== ==========
    'and': And(),
    'boolean->string': BooleanToString(),
    'boolean=?': BooleanSymEqualHuh(),
    'boolean?': BooleanHuh(),
    'false?': FalseHuh(),
    'not': Not(),
    'or': Or(),
    # ========== ========== ==========
    #               list
    # ========== ========== ==========
    # 'append': Append(),
    'cons?': ConsHuh(),
    # 'eighth': Eighth(),
    'empty?': EmptyHuh(),
    # 'fifth' : Fifth(),
    'first': First(),
    # 'fourth': Fourth(),
    # 'length': Length(),
    'list': List(),
    # 'list*': ListSymStar(),
    # 'list-ref': ListRef(),
    # 'list?': ListHuh(),
    # 'make-list': MakeList(),
    # 'member': Member(),
    # 'member?': MemberHuh(),
    # 'null?': NullHuh(),
    # 'range': Range(),
    'rest': Rest(),
    # 'reverse': Reverse(),
    # 'second': Second(),
    # 'seventh': Seventh(),
    # 'sixth': Sixth(),
    # 'third': Third()
    # ========== ========== ==========
    #             numeric
    # ========== ========== ==========
    '*': SymMultiply(),
    '+': SymPlus(),
    '-': SymMinus(),
    '/': SymDivide(),
    '<': SymLessThan(),
    '<=': SymLessEqualThan(),
    '=': SymEqual(),
    '>': SymGreaterThan(),
    '>=': SymGreaterEqualThan(),
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
    'RationalNum?': RationalNumHuh(),
    'real?': RealHuh(),
    'round': Round(),
    'sgn': Sgn(),
    'sqr': Sqr(),
    'sqrt': Sqrt(),  # cannot handle negative numbers for now
    'sub1': Sub1(),
    'zero?': ZeroHuh(),
    # ========== ========== ==========
    #              string
    # ========== ========== ==========
    'string-alphabetic?': StringAlphabeticHuh(),
    'string-append': StringAppend(),
    # 'string-ci<=?': StringCiSymbolLessEqualHuh(),
    # 'string-ci<?': StringCiSymbolLessHuh(),
    # 'string-ci=?': StringCiSymEqualHuh(),
    # 'string-ci>=?': StringCiSymGreaterEqualHuh(),
    # 'string-ci>?': StringCiSymGreaterHuh(),
    # 'string-contains-ci?': StringContainsCiHuh(),
    'string-contains?': StringContainsHuh(),
    'string-copy': StringCopy(),
    'string-downcase': StringDowncase(),
    'string-ith': StringIth(),
    'string-length': StringLength(),
    'string-lower-case?': StringLowerCaseHuh(),
    'string-numeric?': StringNumericHuh(),
    'string-upcase': StringUpcase(),
    'string-upper-case?': StringUpperCaseHuh(),
    'string-whitespace?': StringWhitespaceHuh(),
    # 'string<=?': StringSymbolLessEqualHuh(),
    # 'string<?': StringSymbolLessHuh(),
    # 'string=?': StringSymEqualHuh(),
    # 'string>=?': StringSymGreaterEqualHuh(),
    # 'string>?': StringSymGreaterHuh(),
    'string?': StringHuh(),
    # 'substring': Substring()
    # ========== ========== ==========
    #              symbol
    # ========== ========== ==========
    'symbol->string': SymbolToString(),
    'symbol=?': SymbolSymEqualHuh(),
    'symbol?': SymbolHuh()
}
