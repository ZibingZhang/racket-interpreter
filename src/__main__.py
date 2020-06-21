from src import constants
from src.constants import C
from src.errors import BuiltinProcedureError, InterpreterError, LexerError, ParserError, SemanticError, PreLexerError
from src.util import Util


def main():
    constants.init(should_log_scope=False, should_log_stack=False)

    try:
        text = \
            """
            ; Code written for an assignment at Northeastern. It has been slightly modified as some of the original
            ; code made use of Lists which are not yet implemented in the interpreter. Another change is the removal
            ; of check-expect statements, which are replaced with either an = or boolean=?, depending on the output
            ; of the procedure being tested.
            
            (define-struct plist [frst rst])
            ; A PseudoLON is one of :
            ; - "empty"
            ; - (make-plist Number PseudoLON)
            ; and represents a list of numbers
            
            ; examples of PseudoLONs
            (define PLON1 "empty")
            (define PLON2 (make-plist 13 "empty"))
            (define PLON3 (make-plist 8/2 PLON2))
            (define PLON4 (make-plist 5.5 PLON3))
            (define PLON5 (make-plist -3 PLON4))
            (define PLON6 (make-plist 0 PLON5))
            (define PLON7 (make-plist 4 PLON6))
            
            ; add-up-all : PseudoLON -> Number
            ; Adds up all the numbers
            (define (add-up-all plon)
              (cond [(string? plon)
                     0]
                    [(plist? plon)
                     (+ (plist-frst plon)
                        (add-up-all (plist-rst plon)))]))
            (= (add-up-all PLON1) 0)
            (= (add-up-all PLON2) 13)
            (= (add-up-all PLON3) 17)
            (= (add-up-all PLON4) 22.5)
            (= (add-up-all PLON5) 19.5)
            (= (add-up-all PLON6) 19.5)
            
            ; in? : Number PseudoLON -> Bool
            ; Is the number in the list?
            (define (in? n l)
              (cond
                [(string? l)
                 #f]
                [(plist? l)
                 (if (= n (plist-frst l))
                     #t
                     (in? n (plist-rst l)))]))
            (boolean=? (in? 5.5 PLON1) #f)
            (boolean=? (in? 5.5 PLON2) #f)
            (boolean=? (in? 5.5 PLON3) #f)
            (boolean=? (in? 5.5 PLON4) #t)
            (boolean=? (in? 5.5 PLON5) #t)
            (boolean=? (in? 5.5 PLON6) #t)
            
            ; all-in? : List List -> Bool
            ; Are all the elements of the first list in the second?
            (define (all-in? s1 s2)
              (cond
                [(string? s1)
                 #t]
                [(plist? s1)
                 (if (in? (plist-frst s1) s2)
                     (all-in? (plist-rst s1) s2)
                     #f)]))
            (boolean=? (all-in? PLON1 PLON1) #t)
            (boolean=? (all-in? PLON2 PLON1) #f)
            (boolean=? (all-in? PLON1 PLON2) #t)
            (boolean=? (all-in? PLON7 PLON6) #t)
            (boolean=? (all-in? PLON6 PLON7) #t)
            
            ; examples of sets
            (define S0 "empty")
            (define S1 (make-plist 1 (make-plist 2 (make-plist 3 "empty"))))
            (define S2 (make-plist 1 (make-plist 1 (make-plist 1 (make-plist 1 (make-plist 2 (make-plist 2 (make-plist 2 (make-plist 3 (make-plist 3 "empty"))))))))))
            (define S3 (make-plist 1 (make-plist 3 (make-plist 2 "empty"))))
            (define S4 (make-plist 1 (make-plist 2 (make-plist 4 "empty"))))   

            ; set=? : List List -> Bool
            ; Are the two sets equal?
            (define (set=? s1 s2)
              (and (all-in? s1 s2)
                   (all-in? s2 s1)))
            (boolean=? (set=? S0 S1) #f)
            (boolean=? (set=? S1 S0) #f)
            (boolean=? (set=? S1 S2) #t)
            (boolean=? (set=? S2 S1) #t)
            (boolean=? (set=? S1 S3) #t)
            (boolean=? (set=? S1 S4) #f)
            """

        result = Util.text_to_result(text)

        if C.SHOULD_LOG_SCOPE or C.SHOULD_LOG_STACK:
            print('')
        print('Output:')
        for output in result:
            print(f'     {output}')

    except (PreLexerError, LexerError, ParserError, SemanticError, InterpreterError, BuiltinProcedureError) as e:
        print(e.message)
        return


if __name__ == '__main__':
    main()
