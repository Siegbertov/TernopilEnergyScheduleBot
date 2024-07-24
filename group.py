from utils import difference_in_time, sum_of_time

class Group:
    MINUS = "-"
    PLUS = "+"
    def __init__(self, num:str, inline:str)->None:
        self.num = num
        self.inline = inline

        self.off_pairs = []
        self.on_pairs = []

        self.total_off = None
        self.total_on = None
    
    def __create_off_pairs(self)->None:
        if self.PLUS in self.inline:
            if self.inline.count(self.PLUS) > 1:
                for elem in self.inline.split(self.PLUS):
                    if self.MINUS in elem:
                        self.off_pairs.append(elem)
            else:
                self.off_pairs = self.inline

    def __create_on_pairs(self)->None:
        if self.MINUS in self.inline:
            if self.inline.count(self.MINUS) > 1:
                for elem in self.inline.split(self.MINUS):
                    if self.PLUS in elem:
                        self.on_pairs.append(elem)
            else:
                self.on_pairs = self.inline

    def get_total_off(self)->str:
        if not self.off_pairs:
            self.__create_off_pairs()
        result = None
        for pair in self.off_pairs:
            t1, t2 = pair.split("-")
            diff = difference_in_time(t1.split(":"), t2.split(":"))
            if result is None:
                result = diff
            else:
                result = sum_of_time(result, diff)
        return ":".join(result)

    def get_total_on(self)->str:
        if not self.on_pairs:
            self.__create_on_pairs()
        result = None
        for pair in self.on_pairs:
            t1, t2 = pair.split("+")
            diff = difference_in_time(t1.split(":"), t2.split(":"))
            if result is None:
                result = diff
            else:
                result = sum_of_time(result, diff)
        return ":".join(result)

    def __get_off_pairs(self)->list:
        return self.off_pairs
    
    def __get_on_pairs(self)->list:
        return self.on_pairs

    def get_num(self)->str:
        return self.num
    
    def get_inline_str(self, off_emoji:str, on_emoji:str)->str:
        return self.inline.replace(self.MINUS, off_emoji).replace(self.PLUS, on_emoji)

    def get_off_pairs_str(self, off_emoji:str, on_emoji:str)->str:
        self.__create_off_pairs()
        result = "\n".join(self.__get_off_pairs())
        return result.replace(self.MINUS, off_emoji).replace(self.PLUS, on_emoji)
    
    def get_on_pairs_str(self, off_emoji:str, on_emoji:str)->str:
        self.__create_on_pairs()
        result = "\n".join(self.__get_on_pairs())
        return result.replace(self.MINUS, off_emoji).replace(self.PLUS, on_emoji)



if __name__ == "__main__":
    GROUP = Group(num='5', inline="00:00-5:00+10:00-12:00+17:00-24:00")
    OFF_emoji = "🔴"
    ON_emoji = "🟢"
    print(GROUP.get_num())
    print()
    print(GROUP.get_inline_str(OFF_emoji, ON_emoji))
    print()
    print(GROUP.get_off_pairs_str(OFF_emoji, ON_emoji))
    print(GROUP.get_total_off())
    print()
    print(GROUP.get_on_pairs_str(OFF_emoji, ON_emoji))
    print(GROUP.get_total_on())
    print()