# inspirado no código das aulas práticas
from tree_search import SearchDomain, SearchProblem
from moveKeeper import SearchTreeMoveKeeper, MoveKeeper
from math import hypot

# verificar qual a distancia duma caixa a um objetivo
def dist_manhattan(box, goal):
    return abs(box[0] - goal[0]) + abs(box[1] - goal[1])

def dist_pythagorean(box, goal):
    return hypot(box[0] - goal[0], box[1] - goal[1])

# associar uma caixa a um objetivo
def greedy_ap(p_queue):
    heuristic = 0
    matched_boxes = set()
    matched_goals = set()
    matching = []
    while p_queue:
        _, box, goal = p_queue.pop(0)
        
        if not box in matched_boxes and not goal in matched_goals:
            matching.append((box, goal))
            matched_boxes.add(box)
            matched_goals.add(goal)
    return matching, matched_boxes, matched_goals

def oper(coord1, coord2):
    if coord1[0] - coord2[0] == 0 and coord1[1] - coord2[1] == -1:
        return 's'
    if coord1[0] - coord2[0] == 0 and coord1[1] - coord2[1] == 1:
        return 'w'
    if coord1[1] - coord2[1] == 0 and coord1[0] - coord2[0] == -1:
        return 'd'
    if coord1[1] - coord2[1] == 0 and coord1[0] - coord2[0] == 1:
        return 'a'
    
def evo_of_box(action):
    if isinstance(action, W):
        return (action.args[0], action.args[1] - 1)
    elif isinstance(action, S):
        return (action.args[0], action.args[1] + 1)
    elif isinstance(action, A):
        return (action.args[0] - 1, action.args[1])
    elif isinstance(action, D):
        return (action.args[0] + 1, action.args[1])
        
# Strips predicates
class Predicate:
    def __str__(self):
        return type(self).__name__ + str(self.args)
    
    def __repr__(self):
        return str(self)
    
    def __eq__(self,predicate):   # allows for comparisons with "==", etc.
        return str(self)==str(predicate)
    
    def __hash__(self):
        return hash(str(self))
    
    def __lt__(self, predicate):
        return str(self) < str(predicate)
    
    def substitute(self,assign): # Substitute the arguments in a predicate
        return type(self)(self.args[0] + assign[0], self.args[1] + assign[1])

# Sokoban predicates

class Box(Predicate):
    def __init__(self,c1,c2):
        self.args = (c1,c2)

# STRIPS operators
class Operator:

    def __init__(self, args, result):
        self.args = args
        self.result = result
                                
    def __str__(self):
        return type(self).__name__ + '([' + str(self.args) + "]," +  \
               str(self.result) + ')'
               
    def __repr__(self):
        return type(self).__name__ + "(" + str(self.args) + ")"

    @classmethod
    def instanciate(cls, coord, state):        
        result = cls.result(coord, state)
        return cls((coord[0], coord[1]), result)

# Sokoban operators
class W(Operator):
    def result(coord, state):
        x, y = coord
        newState = [p for p in state if p != Box(x, y)]
        newState.append(Box(x, y - 1))
        return newState

class A(Operator):
    def result(coord, state):
        x, y = coord
        newState = [p for p in state if p != Box(x, y)]
        newState.append(Box(x - 1, y))
        return newState

class S(Operator):
    def result(coord, state):
        x, y = coord
        newState = [p for p in state if p != Box(x, y)]
        newState.append(Box(x, y + 1))
        return newState
    
class D(Operator):
    def result(coord, state):
        x, y = coord
        newState = [p for p in state if p != Box(x, y)]
        newState.append(Box(x + 1, y))
        return newState

def freeze_deadlock(coord_box, coord_boxes, walls, coords_goals, current_coord_box):
    coord_boxes.remove(current_coord_box)
    coord_boxes.append(coord_box)
    ret = False
    box2check = []
    while True:
        if coord_box in coords_goals:
            break
        
        vertical = vertical_check(coord_box, coord_boxes, walls, coords_goals)
        
        if vertical is None:     # no caso de n haver deadlock na vertical
            break
        
        horizontal = horizontal_check(coord_box, coord_boxes, walls, coords_goals)
        
        if horizontal is None: # no caso de haver deadlock na vertical mas na horizontal n
            break
        
        if vertical == coord_box and horizontal == coord_box: # se há uma wall na vertical e tmb na horizontal
            ret = True
            break
        
        if vertical != coord_box:
            box2check.append(vertical)
        
        if horizontal != coord_box:
            box2check.append(horizontal)
            
        walls.add(coord_box)
        if len(box2check) == 0:
            break
        
        coord_box = box2check.pop(0)        
        
    return ret

def vertical_check(coord_box, coord_boxes, walls, coords_goals):
    x, y = coord_box
    up = (x, y - 1)
    down = (x, y + 1)
    if up in walls or down in walls:
        return coord_box # retornar a própria coordenada se estiver bloqueado por caixas
    
    if up in coord_boxes:
        return up
    if down in coord_boxes:
        return down
    
    return None

def horizontal_check(coord_box, coord_boxes, walls, coords_goals):
    x, y = coord_box
    left = (x - 1, y)
    right = (x + 1, y)
    
    if left in walls or right in walls:
        return coord_box
    
    if left in coord_boxes:
        return left
    if right in coord_boxes:
        return right
        
    return None
    
class STRIPS(SearchDomain):
    
    # constructor
    def __init__(self, coords_available, walls, wall_deadlocks, coords_goal):
        self.coords_available = coords_available
        self.walls = walls
        self.wall_deadlocks = wall_deadlocks
        self.coords_goal = coords_goal
        self.operators = {o.__name__.lower():o for o in Operator.__subclasses__()}
        
    # esta funcao itera simplesmente por todas as caixas do estado de forma a saber para onde o keeper se pode mover
    def get_subP_goals(self, state):
        coord_boxes = [b.args for b in state]
        coords_available = {c for c in self.coords_available if not c in coord_boxes}

        return [self.pos_coords_Box(coords_available, coord_boxes, p.args) for p in state]

    # funcao que retorna todas as coordenadas para onde o keeper se pode mover para empurrar uma caixa
    def pos_coords_Box(self, coords_available, coord_of_boxes, coord):
        
        x, y = coord
        lst_lat = [(x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)]
        lst_other_side = [(x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)]
                
        return [lst_lat[i] for i in range(4)
                    if  lst_lat[i] in coords_available                      # verificar se a coordenada está livre
                        and not lst_other_side[i] in self.wall_deadlocks    # verificar se a caixa vai para deadlock
                        and lst_other_side[i] in coords_available           # verificar se o lado oposto está livre
                        and not freeze_deadlock(lst_other_side[i],         # verificar se vai haver um freeze deadlock
                                                coord_of_boxes.copy(), set(self.walls), self.coords_goal,
                                                coord)], coord 


    # list of applicable actions in a given "state"
    def actions(self, node):
        actions = []
        
        coord_boxes = [b.args for b in node.state]
        coords_available = [c for c in self.coords_available if not c in coord_boxes]
        
        m = MoveKeeper(coords_available)
        for coords, box in self.get_subP_goals(node.state):
            for coord in coords:
                p = SearchProblem(m, node.keeper, coord)
                t = SearchTreeMoveKeeper(p)
                evo = t.searchPath()
                
                if not evo: # quer dizer que há uma caixa (p.e) a bloquear o caminho que n permite que o keeper
                            # chegue a essa coordenada livre
                   continue
                movements = t.get_keys_to_goal
                
                action = self.operators[oper(coord, box)].instanciate(box, node.state)
                
                actions.append((action, movements))
                    
        return actions
    
    def result(self, state, action):
        pass
    
    def cost(self, state, action):
        return 0

    def heuristic(self, state, goal):
        # retorna a soma das distancias de caixas a objetivos em q cada objetivo fica associado a uma unica caixa
        edges = [(dist_pythagorean(s.args, g.args), s.args, g.args) for s in state for g in goal]
        
        matching, matched_boxes, matched_goals = greedy_ap(sorted(edges, key=lambda d : d[0]))
        
        soma = sum(dist_pythagorean(b, g) for b, g in matching)
        
        if not all(b.args in matched_boxes for b in state):
            soma += sum(min(dist_pythagorean(b.args, g.args) for g in goal)for b in state if not b.args in matched_boxes)
        
        return soma

    # Checks if a given "goal" is satisfied in a given "state"
    def satisfies(self, state, goal):
        return all(p in state for p in goal)
    
    
""" para testar apenas um nv """
import time
from mapa import *
from consts import *
from tree_search import SearchTree

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

# verifica quais sao as coordenadas onde n se pode colocar caixas
def static_wall_deadlocks(coords_available, goals, walls):
    return [ coord for coord in coords_available if wall_deadlock(coord, walls, goals, coords_available)]

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

def main():
    start = time.time()

    m = Map('levels/118.xsb')
    print(m)
    initial, goal, walls, available = map_conditions(m)
    # print('initial state:', initial)
    # root = SearchNode(initial, None, 0, 0, 0, None, m.keeper)
    coord_box = [b.args for b in initial]
    coord_goal = [g.args for g in goal]
    wall_deadlocks = static_wall_deadlocks([c for c in available if not c in coord_box], coord_goal, walls)

    strips = STRIPS(available, walls, wall_deadlocks, coord_goal)

    p = SearchProblem(strips, initial, goal)

    t = SearchTree(p, m.keeper)
    try:
        t.searchSync()
        print(t.plan)
        print('Nos terminais {} e os nos nao terminais {}'.format(t.non_terminals, t.terminals))
    except KeyboardInterrupt:
        print('Nós nao terminais: {}\nNos terminais {}'.format(t.non_terminals, t.terminals))
        print('Lista de coordenadas passadas', t.coordenadas)
        print('Lista de posicoes das caixas', t.caixas)
        print('Lista de posicoes do keeper', t.keeper)

    print('time:', time.time() - start)
    
import timeit
if __name__ == '__main__':
    main()
