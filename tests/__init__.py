if __name__ == '__main__':
    from racketinterpreter import interpret

    code = \
        '''
            (define x "Hello World!")
            x 
        '''

    print(interpret(code))
