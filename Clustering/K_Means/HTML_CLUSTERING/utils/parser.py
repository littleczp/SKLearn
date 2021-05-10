class CommentParser:
    def __init__(self):
        self.start = -1
        self.end = -1

        # init
        self.open_state = 1
        self.close_state = 1
        self.open_count = 0
        self.close_count = 0
        self.inside_comment = False

    def reset(self):
        self.open_state = 1
        self.close_state = 1
        self.open_count = 0
        self.close_count = 0

    def parse(self, c, i):
        if ((self.open_state == 1 and c == "<") or
                (self.open_state == 2 and c == "!") or
                (self.open_state == 3 and c == "-") or
                (self.open_state == 4 and c == "-")):
            self.open_state += 1
        else:
            # Handle <!> comment
            if self.open_state == 3 and c == ">":
                self.inside_comment = False
                self.reset()
                self.start, self.end = i - 2, i
                return True
            self.open_state = 1
        if self.open_state == 5:
            if self.open_count == 0:
                self.start = i - 3
            self.open_state = 1
            self.open_count = 1
            self.inside_comment = True

        if self.close_count < self.open_count:
            if self.close_state == 1:
                if c == "-":
                    self.close_state += 1
            elif self.close_state == 2:
                if c == "-":
                    self.close_state += 1
                else:
                    self.close_state = 1
            elif self.close_state == 3:
                if c == "!":
                    self.close_state = 4
                elif c == ">":
                    self.close_state = 5
                else:
                    self.close_state = 1
            elif self.close_state == 4:
                if c == ">":
                    self.close_state = 5
                else:
                    self.close_state = 1

            if self.close_state == 5:
                self.close_state = 1
                self.close_count += 1
                if self.close_count >= self.open_count:
                    self.end = i
                    self.reset()
                    self.inside_comment = False
                    return True
        return False


class ScriptParser:
    def __init__(self):
        self.start = -1
        self.end = -1
        self.state = 1

    def parse(self, c, i):
        if self.state == 10:
            self.state = 1
        if ((self.state == 1 and c == "<") or
                (self.state == 2 and c == "/") or
                (self.state == 3 and c in "sS") or
                (self.state == 4 and c in "cC") or
                (self.state == 5 and c in "rR") or
                (self.state == 6 and c in "iI") or
                (self.state == 7 and c in "pP") or
                (self.state == 8 and c in "tT") or
                (self.state == 9 and c == ">")):
            self.state += 1
        else:
            self.state = 1

        if self.state == 2:
            self.start = i
        elif self.state == 10:
            self.end = i

        return self.state == 10
