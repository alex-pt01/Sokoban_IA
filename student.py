import asyncio
import getpass
import json
import os
import time
import sys

import websockets
from mapa import Map
from aux_func import map_conditions, static_wall_deadlocks
from strips import STRIPS
from tree_search import SearchProblem, SearchTree

async def solver(puzzle, solution):
    i=0
    while True:
        start = time.time()

        game_properties = await puzzle.get()
        mapa = Map(game_properties["map"])

        initial, goal, walls, available = map_conditions(mapa)

        coord_box = [b.args for b in initial]
        coord_goal = [g.args for g in goal]
        wall_deadlocks = static_wall_deadlocks([c for c in available if not c in coord_box], coord_goal, walls)
        
        strips = STRIPS(available, walls, wall_deadlocks, coord_goal)

        p = SearchProblem(strips, initial, goal)
        
        t = SearchTree(p, mapa.keeper)
        await t.search()
        
        keys = t.plan
                
        await solution.put(keys)
        i+=1
        print("nv:", i,' time:', time.time() - start)
        print('Nos terminais', t.terminals)
        print('Nos nao terminais', t.non_terminals)


async def agent_loop(puzzle, solution, server_address="localhost:8000", agent_name="student"):
    async with websockets.connect(f"ws://{server_address}/player") as websocket:

        # Receive information about static game properties
        await websocket.send(json.dumps({"cmd": "join", "name": agent_name}))
       
        while True:
            try:
                update = json.loads(
                    await websocket.recv()
                )  # receive game update, this must be called timely or your game will get out of sync with the server

                if "map" in update:
                    # we got a new level
                    mapa = Map(update["map"])
                    keys = ""
                    await puzzle.put(update)
                
                if not solution.empty():
                    keys = await solution.get()
                
                key = ""
                if len(keys):
                    key = keys[0]
                    keys = keys[1:]
	     

                await websocket.send(
                        json.dumps({"cmd": "key", "key": key})
                ) 
            except websockets.exceptions.ConnectionClosedOK:
                print("Server has cleanly disconnected us")
                sys.exit(0)
                return

# DO NOT CHANGE THE LINES BELLOW
# You can change the default values using the command line, example:
# $ NAME='arrumador' python3 client.py
loop = asyncio.get_event_loop()
SERVER = os.environ.get("SERVER", "localhost")
PORT = os.environ.get("PORT", "8000")
NAME = os.environ.get("NAME", getpass.getuser())

puzzle = asyncio.Queue(loop=loop)
solution = asyncio.Queue(loop=loop)

net_task = loop.create_task(agent_loop(puzzle,solution, f"{SERVER}:{PORT}", NAME))
solver_task = loop.create_task(solver(puzzle,solution))


loop.run_until_complete(asyncio.gather(net_task, solver_task))
loop.close()

