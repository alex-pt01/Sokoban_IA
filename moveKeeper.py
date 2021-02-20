from tree_search import SearchDomain
# from aux_func import oper
from hashlib import md5
import queue
from collections import deque

# aux functions
def dist_manhattan(keeper, box):
    return abs(keeper[0] - box[0]) + abs(keeper[1] - box[1])

def oper(coord1, coord2):
    if coord1[0] - coord2[0] == 0 and coord1[1] - coord2[1] == -1:
        return 's'
    if coord1[0] - coord2[0] == 0 and coord1[1] - coord2[1] == 1:
        return 'w'
    if coord1[1] - coord2[1] == 0 and coord1[0] - coord2[0] == -1:
        return 'd'
    if coord1[1] - coord2[1] == 0 and coord1[0] - coord2[0] == 1:
        return 'a'

def evolution2keys(evo):
    ret = ''
    last = evo[0]
    for c in evo[1:]:
            ret += oper(last, c)
            last = c
    return ret

class MoveKeeper(SearchDomain):
    def __init__(self, coordinates):
        self.coordinates = coordinates
        
    def actions(self, current_coord):
        x, y = current_coord
        lateral_coords = [(x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)]
        return [c for c in lateral_coords if c in self.coordinates]
    
    def result(self, current_coord, next_coord):
        # nao é preciso fazer nenhuma verificacao pq já há esse cuidado aquando da criacao da acao
        return next_coord
    
    def cost(self, current_coord, next_coord):
        return 1
    
    def heuristic(self, coord, goal):
        # distancia de manhattan
        return abs(coord[0] - goal[0]) + abs(coord[1] - goal[1])
    
    def satisfies(self, coord, goal):
        return coord == goal
    
class KeeperNode:
    def __init__(self, state, parent, cost, heuristic, counter): 
        self.state = state
        self.parent = parent
        self.cost = cost
        self.heuristic = heuristic
        self.counter = counter
                                        
    def __str__(self):
        return "no(" + str(self.state) + "," + str(self.parent) + ")"
    
    def __repr__(self):
        return str(self)
    
    def __lt__(self, node):
        return self.counter > node.counter

class SearchTreeMoveKeeper:
    
    def __init__(self, problem):
        self.problem = problem
        root = KeeperNode(problem.initial, None, 0, problem.domain.heuristic(problem.initial, problem.goal), 0)
        self.already_opened = set()
        self.at_queue = {problem.initial}
        self.open_nodes = queue.PriorityQueue()
        self.open_nodes.put((0, root))
        self.counter = 0
        
    def get_path(self, node):
        path = [node.state]
        node = node.parent
        while node:
            path[:0] = [node.state]
            node = node.parent
        
        return path            
    
    @property
    def get_keys_to_goal(self):
        return evolution2keys(self.get_path(self.solution))
        
    def searchPath(self, limit=None):        
        while not self.open_nodes.empty():
            priority, node = self.open_nodes.get()
                        
            if self.problem.goal_test(node.state):
                self.solution = node
                return True
            
            self.already_opened.add(node.state)
            self.at_queue.remove(node.state)
            
            for a in self.problem.domain.actions(node.state):

                if a in self.already_opened or a in self.at_queue:
                    continue
                                
                self.at_queue.add(a)
                
                custo = node.cost + 1
                heuristica = self.problem.domain.heuristic(a, self.problem.goal)
                
                newnode = KeeperNode(a, node, custo,
                                     heuristica, self.counter)
                
                self.open_nodes.put((custo + heuristica, newnode))
                self.counter += 1
        return None


from tree_search import SearchProblem
import timeit

def main() :
    mapa = [(0,0), (1,0), (2,0), (3,0), (4,0),
            (0,1), (1,1), (2,1), (3,1), (4,1),
            (0,2), (1,2), (2,2), (4,2),
            (0,3), (1,3), (2,3), (3,3), (4,3),
            (0,4), (1,4), (2,4), (3,4), (4,4)]

    problema = SearchProblem(MoveKeeper(mapa), (1, 1), (3, 4))

    t = SearchTreeMoveKeeper(problema)
    evo = t.searchPath()
    # print(evo)
    # print(evolution2keys(evo))

if __name__ == '__main__':
    # print(timeit.timeit(lambda : main(), number=1000))
    main()
