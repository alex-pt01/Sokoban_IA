import asyncio
import getpass
import json
import os

import websockets
from mapa import Map
import pygame
# Next 4 lines are not needed for AI agents, please remove them from your code!

class Client:
    def __init__(self):
        pygame.init()
        program_icon = pygame.image.load("data/icon2.png")
        pygame.display.set_icon(program_icon)
        
        loop = asyncio.get_event_loop()
        SERVER = os.environ.get("SERVER", "localhost")
        PORT = os.environ.get("PORT", "8000")
        NAME = os.environ.get("NAME", getpass.getuser())
        loop.run_until_complete(self.agent_loop(f"{SERVER}:{PORT}", NAME))

        
    
    async def agent_loop(self,server_address="localhost:8000", agent_name="student"):
        async with websockets.connect(f"ws://{server_address}/player") as websocket:

            # Receive information about static game properties
            await websocket.send(json.dumps({"cmd": "join", "name": agent_name}))

            # Next 3 lines are not needed for AI agent
            SCREEN = pygame.display.set_mode((299, 123))
            SPRITES = pygame.image.load("data/pad.png").convert_alpha()
            SCREEN.blit(SPRITES, (0, 0))
            while True:
                try:
                    update = json.loads(
                        await websocket.recv()
                    )  # receive game update, this must be called timely or your game will get out of sync with the server
                    state = None
                    if "map" in update:
                        # we got a new level
                        game_properties = update
                        mapa = Map(update["map"])
                    else:
                        # we got a current map state update
                        #global state
                        state = update
                        print(state)

                    # Next lines are only for the Human Agent, the key values are nonetheless the correct ones!
                    
                    
                    self.pygame(pygame.event.get(),state)
                    

                except websockets.exceptions.ConnectionClosedOK:
                    print("Server has cleanly disconnected us")
                    return

                # Next line is not needed for AI agent
                pygame.display.flip()


       
       
    def pygame(self, getPygameEvent, state):
        key = ""
        for event in getPygameEvent:
            if event.type == pygame.QUIT:
                pygame.quit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    key = "w"
                elif event.key == pygame.K_LEFT:
                    key = "a"
                elif event.key == pygame.K_DOWN:
                    key = "s"
                elif event.key == pygame.K_RIGHT:
                    key = "d"

                elif event.key == pygame.K_d:
                    import pprint

                    pprint.pprint(state)
                    print(Map(f"levels/{state['level']}.xsb"))
                    
                send_web_socket(key)
                break
                
        
    async def send_web_socket(self,key):
        await websocket.send(
                    json.dumps({"cmd": "key", "key": key})
                )  # send key command to server - you must implement this send in the AI agent
             
     
            
if __name__ == "__main__":
    app = Client()
    app.agent_loop()
