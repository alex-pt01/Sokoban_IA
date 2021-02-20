from consts import Tiles
from strips import Box

# verifica quais sao as coordenadas onde n se pode colocar caixas
def static_wall_deadlocks(coords_available, goals, walls):
    wall_deadlocks = []
    for coord in coords_available:
        if wall_deadlock(coord, walls, goals, coords_available):
            wall_deadlocks.append(coord)
    return wall_deadlocks

# verifica se vai incorrer num deadlock de parede
def wall_deadlock(free_coord, walls, coords_of_goals, coords_available):
    # se a coordenada é um goal entao vamos supor que n é um wall deadlock
    if free_coord in coords_of_goals:
        return False
    x, y = free_coord
    
    # se todas as coordenadas à volta estiverem livres n é deadlock
    if all(c in coords_available for c in [(x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)]):
        return False
    
    # verificar para o topo esquerdo
    if check_wall_conditions((x, y - 1), (x - 1, y), walls,
                                    lambda : sum(1 for c in coords_of_goals if y >= c[1]),
                                    lambda : sum(1 for c in coords_available if y-1 >= c[1]) > 3,
                                    lambda : sum(1 for c in coords_of_goals if x >= c[0]),
                                    lambda : sum(1 for c in coords_available if x-1 >= c[0]) > 3):
        return True
    # para o topo direito
    if check_wall_conditions((x, y - 1), (x + 1, y), walls,
                                    lambda : sum(1 for c in coords_of_goals if y >= c[1]),
                                    lambda : sum(1 for c in coords_available if y-1 >= c[1]) > 3,
                                    lambda : sum(1 for c in coords_of_goals if x <= c[0]),
                                    lambda : sum(1 for c in coords_available if x+1 <= c[0]) > 3):
        return True
    # para o canto inferior esquerdo
    if check_wall_conditions((x, y + 1), (x - 1, y), walls,
                                    lambda : sum(1 for c in coords_of_goals if y <= c[1]),
                                    lambda : sum(1 for c in coords_available if y+1 <= c[1]) > 3,
                                    lambda : sum(1 for c in coords_of_goals if x >= c[0]),
                                    lambda : sum(1 for c in coords_available if x-1 >= c[0]) > 3):
        return True
    # para o canto inferior direito
    if check_wall_conditions((x, y + 1), (x + 1, y), walls,
                                    lambda : sum(1 for c in coords_of_goals if y <= c[1]),
                                    lambda : sum(1 for c in coords_available if y+1 <= c[1]) > 3,
                                    lambda : sum(1 for c in coords_of_goals if x <= c[0]),
                                    lambda : sum(1 for c in coords_available if x+1 <= c[0]) > 3):
        return True
    
    return False
    
def check_wall_conditions(coord1, coord2, walls, f1, f2, f3, f4):
    if coord1 in walls:
        if coord2 in walls:
            return True
        # quando há objetivos nessa linha ou para tras
        if f1():
            return False
        # se n houver nenhum goal para tras entao poderá haver coordenadas livres (para acontecer alguma têm de ser pelo < 4 coord)
        if f2():
            return False
        return True
    else:
        if coord2 in walls:
            if f3():
                return False
            if f4():
                return False
            return True
    return False    

def oper(coord1, coord2):
    if coord1[0] - coord2[0] == 0 and coord1[1] - coord2[1] == -1:
        return 's'
    if coord1[0] - coord2[0] == 0 and coord1[1] - coord2[1] == 1:
        return 'w'
    if coord1[1] - coord2[1] == 0 and coord1[0] - coord2[0] == -1:
        return 'd'
    if coord1[1] - coord2[1] == 0 and coord1[0] - coord2[0] == 1:
        return 'a'

def map_conditions(map):
    initial = []
    available = []
    goals = []
    walls = []
    y = -1
    x = -1
    for line in map.__getstate__():
        y += 1
        for i in range(len(line)):
            x += 1
            if line[i] == Tiles.FLOOR or line[i] == Tiles.MAN:
                available.append((x, y))
            if line[i] == Tiles.GOAL:
                available.append((x, y))
                goals.append(Box(x, y))
            if line[i] == Tiles.MAN_ON_GOAL:
                available.append((x, y))
                goals.append(Box(x, y))
            if line[i] == Tiles.BOX:
                initial.append(Box(x, y))
                available.append((x, y))
            if line[i] == Tiles.BOX_ON_GOAL:
                initial.append(Box(x, y))
                available.append((x, y))
                goals.append(Box(x, y))
            if line[i] == Tiles.WALL:
                walls.append((x, y))
        x = -1
           
    return initial, goals, walls, available

#our goals -> apenas para n chamar a funcao acima que é enorme
def goals(mapa):
    goals = []
    y = -1
    x = -1
    for line in map.__getstate__():
        y += 1
        for i in range(len(line)):
            x += 1

            if line[i] == Tiles.GOAL:
                goals.append(Box(x, y))
        x = -1
    return goals


""" n esta a ser utilizada """
def add2xOry(coord, action):
    if action.__class__.__name__ == 'W':
        return [coord[0], coord[1] - 1]
    elif action.__class__.__name__ == 'S':
        return [coord[0], coord[1] + 1]
    elif action.__class__.__name__ == 'A':
        return [coord[0] - 1, coord[1]]
    elif action.__class__.__name__ == 'D':
        return [coord[0] + 1, coord[1]]

""" n esta a ser utilizada """
def minor_distance2box(state, action):
    """ Minor distance to box ( disregard walls ) """
    keeper_coordinates = None
    boxes = []
    
    for p in state:
        if type(p).__name__ == "Man" or type(p).__name__ == "Man_On_Goal":
            keeper_coordinates = add2xOry(p.args, action)
        if p.__class__.__name__ == "Box":
            boxes.append(p.args)
    #print(keeper_coordinates)
    return min([distance2box(keeper_coordinates, b) for b in boxes])

""" n esta a ser utilizada """
def oppositedirection(moved, last_op, op):
    """ Check if keeper will repeat move in the opposite direction (and had not pushed anything)"""
    opposites = [('W', 'S'), ('A', 'D')]
    if moved:
        return False
    for t in opposites:
        if (last_op == t[0] and op == t[1]) or (last_op == t[1] and op == t[0]):
            #print(last_op, op)
            return True
        
    return False
