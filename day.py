from group import Group

class Day:
    def __init__(self, name:str, groups:dict)->None:
        self.name = name
        self.groups = []
        for g_name, g_inline in groups.values():
            self.groups.append(Group(num=g_name, inline=g_inline))

    def get_name(self)->str:
        return self.name
    
    def get_group(self, g_num:str)->Group:
        return self.groups[g_num]
    
    

