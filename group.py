from utils import difference_in_time, sum_of_time
from datetime import datetime, timedelta

class Group:
    MINUS = "-"
    PLUS = "+"
    COLON = ":"
    def __init__(self, num:str|int, inline:str)->None:
        self.num = num
        self.inline = inline

        self.off_pairs = []
        self.on_pairs = []
        
        self.off_total = None
        self.on_total = None
    
    def __create_off_pairs(self)->None:
        if self.MINUS in self.inline:
            if self.PLUS in self.inline:
                for off_pair in self.inline.split(self.PLUS):
                    if self.MINUS in off_pair:
                        self.off_pairs.append(off_pair)
            else:
                self.off_pairs.append(self.inline)
        else:
            self.off_pairs.append(None)

    def __create_on_pairs(self)->None:
        if self.PLUS in self.inline:
            if self.MINUS in self.inline:
                for on_pair in self.inline.split(self.MINUS):
                    if self.PLUS in on_pair:
                        self.on_pairs.append(on_pair)
            else:
                self.on_pairs.append(self.inline)
        else:
            self.on_pairs.append(None)

    def get_off_pairs(self)->list:
        if not self.off_pairs:
            self.__create_off_pairs()
        return self.off_pairs

    def get_on_pairs(self)->list:
        if not self.on_pairs:
            self.__create_on_pairs()
        return self.on_pairs

    def __count_off_total(self)->None:
        if not len(self.get_off_pairs()):
            self.__create_off_pairs()

        if len(self.get_off_pairs()) == 1:
            if self.get_off_pairs()[0] is not None:
                h_m_1, h_m_2 = self.get_off_pairs()[0].split(self.MINUS)
                h_1, m_1 = h_m_1.split(self.COLON)
                h_2, m_2 = h_m_2.split(self.COLON)
                self.off_total = (timedelta(hours=int(h_2), minutes=int(m_2)) - timedelta(hours=int(h_1), minutes=int(m_1)))
        else:
            self.off_total = timedelta(hours=0, minutes=0)
            for off_pair in self.get_off_pairs():
                h_m_1, h_m_2 = off_pair.split(self.MINUS)
                h_1, m_1 = h_m_1.split(self.COLON)
                h_2, m_2 = h_m_2.split(self.COLON)
                self.off_total += (timedelta(hours=int(h_2), minutes=int(m_2)) - timedelta(hours=int(h_1), minutes=int(m_1)))

    def __count_on_total(self)->None:
        if not len(self.get_on_pairs()):
            self.__create_on_pairs()

        if len(self.get_on_pairs()) == 1:
            if self.get_on_pairs()[0] is not None:
                h_m_1, h_m_2 = self.get_on_pairs()[0].split(self.PLUS)
                h_1, m_1 = h_m_1.split(self.COLON)
                h_2, m_2 = h_m_2.split(self.COLON)
                self.on_total = (timedelta(hours=int(h_2), minutes=int(m_2)) - timedelta(hours=int(h_1), minutes=int(m_1)))
        else:
            self.on_total = timedelta(hours=0, minutes=0)
            for on_pair in self.get_on_pairs():
                h_m_1, h_m_2 = on_pair.split(self.PLUS)
                h_1, m_1 = h_m_1.split(self.COLON)
                h_2, m_2 = h_m_2.split(self.COLON)
                self.on_total += (timedelta(hours=int(h_2), minutes=int(m_2)) - timedelta(hours=int(h_1), minutes=int(m_1)))

    def get_off_total(self)->timedelta|None:
        if self.off_total is None:
            self.__count_off_total()
        return self.off_total

    def get_on_total(self)->timedelta|None:
        if self.on_total is None:
            self.__count_on_total()
        return self.on_total

    def get_inline(self)->str:
        return self.inline

    def get_num(self)->str:
        return self.num
    
    def __str__(self):
        return f"{self.get_num()} {self.get_inline()}"

    def get_full(self, view:str, total:str)->list:
        result = []
        result.append(self.get_num())
        match view:
            case "OFF_PAIRS":
                result.append(self.get_off_pairs())
            case "ON_PAIRS":
                result.append(self.get_on_pairs())
            case "INLINE":
                result.append([self.get_inline()])
        match total:
            case "NONE":
                result.append(None)
            case "TOTAL_ON":
                on_total = self.get_on_total()
                if on_total is None:
                    result.append((0, 0))
                else:
                    result.append((on_total.days*24 + on_total.seconds//3600, (on_total.seconds//60)%60))
            case "TOTAL_OFF":
                off_total = self.get_off_total()
                if off_total is None:
                    result.append((0, 0))
                else:
                    result.append((off_total.days*24 + off_total.seconds//3600, (off_total.seconds//60)%60))
        return result


if __name__ == "__main__":
    import os
    os.system('cls' if os.name == 'nt' else 'clear')
    inlines = [
                "00:00+24:00",
                "00:00-24:00",
                "00:00-12:00+24:00",
                "00:00+12:00-24:00",
                "00:00-08:00+16:00-24:00",
                "00:00+08:00-16:00+24:00"
                ]
    my_view = "OFF_PAIRS"
    my_total = "TOTAL_OFF"
    
    for inline in inlines:
        group = Group(num="10", inline=inline)
        print(f"INPUT: {inline}")

        n, v, t = group.get_full(
            view=my_view,
            total=my_total
        )
        print(f"VIEW '{my_view}':")
        print(v)
        print(f"TOTAL '{my_total}':")
        print(t)
        print()

