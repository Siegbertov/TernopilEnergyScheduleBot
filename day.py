from group import Group

class Day:
    def __init__(self, name:str, groups:dict)->None:
        self.name = name
        self.groups = []
        for g_name, g_inline in groups.items():
            self.groups.append(Group(num=g_name, inline=g_inline))

    def get_name(self)->str:
        return self.name
    
    def get_group(self, g_num:str)->Group:
        return self.groups[g_num]
    
    def get(self, groups_to_show:list, view:str, total:str):
        result = []
        for group in self.groups:
            if group.get_num() in groups_to_show:
                result.append(group.get_full(view=view, total=total))
        return result

if __name__ == "__main__":
    import os
    from pprint import pprint
    os.system('cls' if os.name == 'nt' else 'clear')
    day = Day(
        name='24 липня', 
        groups={
                1: "00:00+24:00",
                2: "00:00-24:00",
                3: "00:00+5:00-10:00+12:00-17:00+24:00",
                4: "00:00+12:00-24:00",
                5: "00:00-5:00+10:00-12:00+17:00-24:00",
                6: "00:00+08:00-16:00+24:00"
                })
    print(day.get_name())
    my_view = "INLINE"
    my_total = "NONE"
    result = day.get(
        groups_to_show=[1, 2, 3, 4, 5, 6],
        view=my_view,
        total=my_total
    )

    pprint(result)



    