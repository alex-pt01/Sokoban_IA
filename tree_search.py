# código retirado do exemplo das aulas práticas

from abc import ABC, abstractmethod
import time
import asyncio
import queue

class SearchDomain(ABC):
    
    # construtor
    @abstractmethod
    def __init__(self):
        pass

    # lista de accoes possiveis num estado
    @abstractmethod
    def actions(self, state):
        pass

    # resultado de uma accao num estado, ou seja, o estado seguinte
    @abstractmethod
    def result(self, state, action):
        pass

    # custo de uma accao num estado
    @abstractmethod
    def cost(self, state, action):
        pass

    # custo estimado de chegar de um estado a outro
    @abstractmethod
    def heuristic(self, state, goal):
        pass

    # test if the given "goal" is satisfied in "state"
    @abstractmethod
    def satisfies(self, state, goal):
        pass
    
class SearchProblem:
    def __init__(self, domain, initial, goal):
        self.domain = domain
        self.initial = initial
        self.goal = goal
        
    def goal_test(self, state):
        return self.domain.satisfies(state, self.goal)
    
class SearchNode:
    def __init__(self, state, parent , depth, cost, heuristic, action, keeper, movements, counter, hash_): 
        self.state = state
        self.parent = parent
        self.depth = depth
        self.cost = cost
        self.heuristic = heuristic
        self.action = action
        
        self.keeper = keeper
        self.movements = movements
        self.counter = counter
        self.hash_ = hash_
            
    def __str__(self):
        return "no(" + str(self.state) + "," + str(self.parent) + ")"
    
    def __repr__(self):
        return str(self)
    
    def __lt__(self, node):
        return self.counter > node.counter
    
class SearchTree:
    
    # construtor
    def __init__(self,problem, keeper_coord): 
        self.problem = problem
        root = SearchNode(problem.initial, None, 0, 0, problem.domain.heuristic(problem.initial, problem.goal), None, keeper_coord, '', 0, hash(''))
        
        self.open_nodes = queue.PriorityQueue()
        self.open_nodes.put((0, root))
        
        self.terminals = 0
        self.non_terminals = 1
        self.visited = set()
        self.in_queue = {hash('')}
        self.counter = 0
                        
    @property
    def length(self):
        return self.solution.depth
    
    @property
    def cost(self):
        return self.solution.cost
    
    @property
    def avg_branching(self):
        return (self.terminals + self.non_terminals - 1) / self.non_terminals

    # obter o caminho (sequencia de estados) da raiz ate um no
    def get_path(self,node):
        if node.parent == None:
            return [node.state]
        path = self.get_path(node.parent)
        path += [node.state]
        return path
    
    def get_plan(self, node):
        if node.parent == None:
            return ''
        plan = self.get_plan(node.parent)
        plan += node.movements + node.action
        return plan
    
    @property
    def plan(self):
        return self.get_plan(self.solution)
    
    async def search(self):
        while not self.open_nodes.empty():
            await asyncio.sleep(0)
            priority, node = self.open_nodes.get()
                        
            if self.problem.goal_test(node.state):
                self.solution = node
                self.terminals = self.open_nodes.qsize()
                return True
            
            self.visited.add(node.hash_)
            self.in_queue.remove(node.hash_)
            self.non_terminals += 1

            for a, mov in self.problem.domain.actions(node):
                newstate = a.result
                                
                state_hash = hash(str(sorted(newstate)) + str(a.args))
                
                if state_hash in self.visited or state_hash in self.in_queue:
                    continue
                
                self.in_queue.add(state_hash)
                
                heuristica = self.problem.domain.heuristic(newstate, self.problem.goal)
                newnode = SearchNode(newstate, node, node.depth + 1, 1, 
                                     heuristica, a.__class__.__name__.lower(), a.args, mov, self.counter, state_hash)
                self.open_nodes.put((heuristica, newnode))
                
                self.counter += 1
            
        return None
    
    def searchSync(self, limit=None):
        while not self.open_nodes.empty():
            priority, node = self.open_nodes.get()
                                    
            if self.problem.goal_test(node.state):
                self.solution = node
                self.terminals = self.open_nodes.qsize()
                return self.get_path(node)

            self.non_terminals += 1
            
            self.visited.add(node.hash_)
            self.in_queue.remove(node.hash_)
            
            for a, mov in self.problem.domain.actions(node):
                
                newstate = a.result
                
                state_hash = hash(str(sorted(newstate)) + str(a.args))
                
                if state_hash in self.visited or state_hash in self.in_queue:
                    continue
                
                self.in_queue.add(state_hash)
                
                custo = node.cost + self.problem.domain.cost(node.state, a)
                heuristica = self.problem.domain.heuristic(newstate, self.problem.goal)
                newnode = SearchNode(newstate, node, node.depth + 1, custo, 
                                     heuristica, a.__class__.__name__.lower(), a.args, mov, self.counter, state_hash)
                self.open_nodes.put((custo + heuristica, newnode))
                self.counter += 1
        return None
