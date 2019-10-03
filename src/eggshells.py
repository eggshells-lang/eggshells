import re

from math import sqrt


class Interpreter:
    def __init__(self):
        self.debug = False
        self.stack = []
        self.std_out = ""
        self.env = dict()

        self.functions = {
            "+": self.plus,
            "-": self.minus,
            "*": self.times,
            "/": self.divide,
            "print": self.prnt,
            "println": self.prntln,
            "string": self.strng,
            "sqrt": self.square_root,
            "for": self.for_loop,
            "var": self.var,
        }

        self.function_parameter_counts = {
            "+": 2,
            "-": 2,
            "/": 2,
            "*": 2,
            "print": 1,
            "println": 1,
            "string": 0,
            "sqrt": 1,
            "for": 3,
            "var": 2,
        }

        self.regex = re.compile(
            r"""'.*?'|".*?"|\(|\)|\d+\.\d*|\d+|\[.*\]|[^\(\)\s]+""", re.VERBOSE
        )
        # self.regex = re.compile(
        #    r''''.*?'|".*?"|\(|\)|\d+\.\d*|\d+|[^\(\)\s]+''', re.VERBOSE)
        # r'''
        # '.*?' | # single quoted substring
        # ".*?" | # double quoted substring
        # \) | \( | # parentheses
        # # \D\w* |
        # \d+\.?\d* | # digits
        # \S+ # all the rest
        # ''', re.VERBOSE)

    def _get_params(self, types):
        vals = []
        while self.stack:
            if self.debug:
                print("strng stck:", [str(v) for v in self.stack])
            if ")" != self.stack[-1] and isinstance(self.stack[-1], types):
                vals.append(self.stack.pop().val)
            elif ")" == self.stack[-1]:
                self.stack.pop()
                break
            else:
                break
        return vals

    def plus(self, x, y):
        return type(x)(x.val + type(x.val)(y.val))

    def minus(self, x, y):
        return number(x.val - y.val)

    def times(self, x, y):
        return type(x)(x.val * y.val)

    def divide(self, x, y):
        return number(x.val / y.val)

    def square_root(self, x):
        return number(sqrt(x.val))

    def to_int(self, x):
        return number(int(x.val))

    def prntln(self, s=""):
        self.prnt(s, end="\n")

    def prnt(self, s="", end=""):
        if self.debug:
            print(str(s) + end)
        self.std_out += str(s.val) + end

    def for_loop(self, iters, fn, params):
        if iters.val > 10:
            iters.val = 10
        if self.debug:
            print(f"fn: {fn}\niters: {iters.val}\nparams: {params}\n")
        for i in range(iters.val):
            fn(*params)

    def var(self, name, val):
        if re.match(r"^\d", name):
            raise Exception("Variable names must start with a-z, A-Z, or _")

        if isinstance(val, (string, number, vector)):
            self.env[name] = val
        elif val in self.env:
            self.env[name] = self.env[val]
        else:
            raise Exception("Some problem with your variable")

    def strng(self):
        return string("".join([str(s) for s in self._get_params((string, number))]))

    def interpret(self, script):
        try:
            script = self.preprocess_script(script)
            for line in script:
                for i in range(1, len(line))[::-1]:
                    if self.debug:
                        print("stack:", [str(v) for v in self.stack])
                        print("\n")
                    tok = line[i]
                    preceding_tok = line[i - 1]
                    if self.debug:
                        print(i, ":", tok)
                    if tok in ["(", ""]:
                        continue
                    if ")" == tok:
                        self.stack.append(")")
                        continue
                    if "(" != preceding_tok:
                        if re.match(r"\d|\.", tok[0]):
                            if "." not in tok:
                                self.stack.append(number(int(tok)))
                            else:
                                self.stack.append(number(float(tok)))
                            continue
                        elif tok[0] not in ["'", '"', "[", "]"]:
                            if tok in self.functions:
                                params = []
                                for _ in range(self.function_parameter_counts[tok]):
                                    if ")" != self.stack[-1]:
                                        params.append(self.stack.pop())
                                self.stack.append(params)
                                self.stack.append(self.functions[tok])
                                continue
                            elif "var" == preceding_tok:
                                self.stack.append(tok)
                            else:
                                if self.debug:
                                    print(self.env)
                                if tok in self.env:
                                    self.stack.append(self.env[tok])
                                else:
                                    raise Exception(
                                        f"{tok} is not a valid token/function"
                                    )
                        elif tok[0] == "'":
                            tok = tok[1:]
                            str_tok = ""
                            for i in range(len(tok)):
                                if tok[i] != "'":
                                    str_tok += tok[i]
                            self.stack.append(string(str_tok))
                            continue
                        elif tok[0] == '"':
                            tok = tok[1:]
                            str_tok = ""
                            for i in range(len(tok)):
                                if tok[i] != '"':
                                    str_tok += tok[i]
                            self.stack.append(string(str_tok))
                            continue
                        elif tok[0] == "[" and tok[-1] == "]":
                            self.stack.append(vector(tok))
                            continue
                        else:
                            raise Exception(f"{tok} is not a valid token/function")

                    elif tok in self.functions:
                        params = []
                        for _ in range(self.function_parameter_counts[tok]):
                            if ")" != self.stack[-1]:
                                params.append(self.stack.pop())
                        ret = self.functions[tok](*params)
                        if ret:
                            self.stack.append(ret)
                    else:
                        raise Exception(f"{tok} is not a valid token/function")
                if self.debug:
                    print("\n")
        finally:
            print(self.stack)
            print("######\nOUTPUT\n######:\n\n" + self.std_out)
            self.stack.clear()
            if self.debug:
                self.std_out = ""

    def preprocess_script(self, script):
        level = 0
        preprocessed = []
        line = []
        if self.debug:
            print(script + "\n")
        for c in self.regex.findall(script):
            if self.debug:
                print(c)
            if c == "(":
                level += 1
            elif c == ")":
                level -= 1
                if level < 0:
                    raise Exception("Too many closing parentheses")
            if self.debug:
                print(level)

            line.append(c)

            if level == 0:
                preprocessed.append(line)
                line = []

        if level > 0:
            raise Exception("Not all parentheses have been closed")

        return preprocessed
        # return self._preprocess_script_aux(preprocessed)


class string:
    def __init__(self, val):
        self.val = val

    def __str__(self):
        return str(self.val)


class number:
    def __init__(self, val):
        self.val = val

    def __str__(self):
        return str(self.val)


class vector:
    # ['this', 'is', 1, ['vector']]
    def __init__(self, vals):
        self.vals = vals
        self.regex = re.compile(r""""[^\"]*?"|'[^\']*?'|\d+\.\d*|\d+|\[.*?\]""")
        self._build_vec()
        self.val = str(self)

    def __build_vec_aux(self, vec):
        for i in range(len(vec)):
            if "[" == vec[i][0] and "]" == vec[i][-1]:
                vec[i] = self.regex.findall(vec[i][1:-1])
                self.__build_vec_aux(vec[i])
            elif re.match(r'\'.*?\'|".*?"', vec[i]):
                if re.match(r"\d+.\d*|\d+", vec[i][1:-1]):
                    vec[i] = number(vec[i][1:-1])
                else:
                    vec[i] = string(vec[i][1:-1])

    def _build_vec(self):
        vec = self.regex.findall(self.vals[1:-1])
        self.__build_vec_aux(vec)
        self.vec = vec

    def __str_aux(self, vec):
        s = []
        for i in range(len(vec)):
            if isinstance(vec[i], list):
                s.append(self.__str_aux(vec[i]))
            else:
                s.append(str(vec[i]))

        return s

    def __str__(self):
        return str(self.__str_aux(self.vec))


# [['(', '(', 'println', "'hello'", ')', '(', 'println', "'world'", ')', ')']]
# =>
# [
#     [
#         '(', 'println', "'hello'", ')'
#     ],
#     [
#         '(', 'println', "'world'", ')'
#     ]
# ]


def _pp_helper(l, d=0):
    item = []
    t = "\t" * d

    i = 0
    while i < len(l):
        print(f"{t}l[i]: {l[i]}")
        if l[i] == "(" and l[i + 1] == "(" and l[-1] == ")":
            _pp_helper(l[1:-1], d + 1)

            i += len(l[1:-1])
        i += 1

    return item


# if __name__ == '__main__':
#     es = Interpreter()
#     es.debug = True
#     script = """(print 'l(o)))l')()(print 'lol lol')(var a 33)(print a)(print 33)"""
#     es.interpret(script)
#     print(es.std_out)
