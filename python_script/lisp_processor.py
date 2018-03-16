import math
import operator as op
from functools import reduce
import copy
import time
import sys

#ref: http://samurait.hatenablog.com/entry/lisp_interpreter_implementation_in_python
#ref: http://norvig.com/lispy.html

class LispProcessor:
    def __init__(self):
        self.env = {
            "+" : lambda *x: sum(x),
            "-" : op.sub,
            "*" : lambda *x:reduce(lambda a,b:a*b,x,1),
            "/" : op.truediv, # python3の"/"
            ">" : op.gt,
            "<" : op.lt,
            ">=" : op.ge,
            "<=" : op.le,
            "=" : op.eq,
            "not=" : lambda x,y: x != y,
            "abs" : abs,
            "apply" : lambda proc,args: proc(*args),
            "first" : lambda x: x[0],
            "second" : lambda x: x[1],
            "rest" : lambda x: x[1:],
            "length" : len,
            "list" : lambda *x: list(x),
            "list?" : lambda *x: isinstance(x,list),
            "map" : lambda *x: list(map(*x)),
            "filter" : lambda *x: list(filter(*x)),
            "max" : max,
            "min" : min,
            "not" : op.not_,
            "cons" : lambda x,y: [x] + y,
            "pi" : math.pi,
            "range": lambda *x: list(range(*x)),
            "empty?" : lambda x: len(x) == 0,
            "get-hour" : lambda : time.localtime().tm_hour,
            "get-min" : lambda : time.localtime().tm_min,
            "inc" : lambda n: n + 1,
            "dec" : lambda n: n - 1,
            "mod" : lambda n,m : n % m,
            "empty-list" : [],
        }

    def execute(self,code):
        tokens = self.tokenizer(code)
        
        if len(tokens) == 0:
            return None
        
        expression = self.read_from_tokens(tokens)
        return self.evaluate(expression)

    def find_object(self,var_name):
        if var_name in self.env.keys():
            return self.env[var_name]
        else:
            raise NameError("Unkown variable: %s" % var_name)

    def evaluate(self,x):
        if isinstance(x,str):
            return self.find_object(x)
        elif isinstance(x,bool) or isinstance(x,int) or isinstance(x,float):
            return x
        elif x[0] == "if":
            if len(x) != 4:
                raise TypeError("The number of argument of 'if' must be 3")
            
            _,flag_exp,true_exp,false_exp = x
            
            flag = self.evaluate(flag_exp)
            if flag:
                return self.evaluate(true_exp)
            else:
                return self.evaluate(false_exp)
        elif x[0] == "do":
            # doは最後の式の値を返り値とするので
            if len(x) == 1:
                raise TypeError("The number of argument of 'do' must be over 1")
            
            for exp in x[1:]:
                ret = self.evaluate(exp)
            
            return ret
        elif x[0] == "def":
            if len(x) != 3:
                raise TypeError("The number of argument of 'def' must be 3")
            
            _,var_name,exp = x
            if not isinstance(var_name,str):
                raise TypeError("The variable name must not be number or bool.")
            
            self.env[var_name] = self.evaluate(exp)
        elif x[0] == "fn":
            if len(x) != 3:
                raise TypeError("The number of argument of 'fn' must be 2")
            
            _,params,exp = x
            
            def func(*xs):
                old_env = copy.deepcopy(self.env)
                
                if len(xs) != len(params):
                    raise TypeError("The number of argument of this function must be %d" % len(xs))
                
                for key,val in zip(params,xs):
                    self.env[key] = val
                
                ret = self.evaluate(exp)
                self.env = old_env
                
                return ret
            
            return func
        else:
            func = self.evaluate(x[0])
            if not callable(func):
                raise TypeError("%s is not callable." % x[0])
            
            arguments = [self.evaluate(arg) for arg in x[1:]]
            return func(*arguments)
    
    def read_from_tokens(self,tokens):
        """
        トークンをリストにする．
        ["(","*","3","5",")"] -> ["(","*",3,5,")"]
        """
        
        if len(tokens) == 0:
            raise SyntaxError("Unexpeted EOF. Check the balance of parentheses.")
        
        # 先頭トークンを読む
        token = tokens.pop(0)
        
        if token == "(":
            ret = []
            
            while tokens[0] != ")":
                ret.append(self.read_from_tokens(tokens))
                
                if len(tokens) == 0:
                    raise SyntaxError("Unexpected EOF. Check the balance of parentheses.")
            tokens.pop(0) # pop ")"
            
            return ret
        elif token == ")":
            raise SyntaxError("Unexpected ')'. Check the balance of parentheses.")
        else:
            return self.try_parse(token)
    
    def tokenizer(self,code):
        return code.replace("("," ( ").replace(")"," ) ").split()

    def parse_bool(self,s):
        if s == "True":
            return True
        elif s == "False":
            return False
        else:
            raise ValueError("invalid literal for parse_bool: '%s'" % s)

    def try_parse(self,word):
        ret = None
        
        converters = [self.parse_bool,int,float,str]
        
        for converter in converters:
            try:
                ret = converter(word)
            except:
                pass
            
            if not ret is None:
                break
        
        return ret

def lisp_test():
    lisp = LispProcessor()
    print(lisp.execute("(* 3 2 ) "))
    print(lisp.execute("""
(do
    (def func 
        (fn (n) 
            (if (<= n 1) 
                1 
                (+  (func (- n 1)) 
                    (func (- n 2))))))
    (func 5))
"""))