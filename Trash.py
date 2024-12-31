import pygame
from Environment import Environment
from MyAgentGold import MyAgentGold
from MyAgentChest import MyAgentChest
from MyAgentStones import MyAgentStones
from Treasure import Treasure
import random

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
YELLOW = (255, 255, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
GRAY = (200, 200, 200)
ORANGE = (255, 165, 0)


CELL_SIZE = 50
FPS = 10

# Load configuration
def loadFileConfig(nameFile):
    file = open(nameFile)
    lines = file.readlines()
    tailleEnv = lines[1].split()
    tailleX = int(tailleEnv[0])
    tailleY = int(tailleEnv[1])
    zoneDepot = lines[3].split()
    cPosDepot = (int(zoneDepot[0]), int(zoneDepot[1]))
    dictAgent = dict()

    env = Environment(tailleX, tailleY, cPosDepot)
    cpt = 0

    for ligne in lines[4:]:
        ligneSplit = ligne.split(":")
        if ligneSplit[0] == "tres":  # new treasure
            if ligneSplit[1] == "or":
                env.addTreasure(Treasure(1, int(ligneSplit[4])), int(ligneSplit[2]), int(ligneSplit[3]))
            elif ligneSplit[1] == "pierres":
                tres = Treasure(2, int(ligneSplit[4]))
                env.addTreasure(tres, int(ligneSplit[2]), int(ligneSplit[3]))
        elif ligneSplit[0] == "AG":  # new agent
            if ligneSplit[1] == "or":
                id = "agent" + str(cpt)
                agent = MyAgentGold(id, int(ligneSplit[2]), int(ligneSplit[3]), env, int(ligneSplit[4]))
                dictAgent[id] = agent
                env.addAgent(agent)
                cpt += 1

            elif ligneSplit[1] == "pierres":
                id = "agent" + str(cpt)
                agent = MyAgentStones(id, int(ligneSplit[2]), int(ligneSplit[3]), env, int(ligneSplit[4]))
                dictAgent[id] = agent
                env.addAgent(agent)
                cpt += 1

            elif ligneSplit[1] == "ouvr":
                id = "agent" + str(cpt)
                agent = MyAgentChest(id, int(ligneSplit[2]), int(ligneSplit[3]), env)
                dictAgent[id] = agent
                env.addAgent(agent)
                cpt += 1

    file.close()
    env.addAgentSet(dictAgent)

    return env, dictAgent

# Display agents info
def display_agents_info(agents):
    print("\nAgent Information:")
    print("-" * 30)
    for agent_id, agent in agents.items():
        if isinstance(agent, MyAgentGold):
            agent_type = "Gold Picker"
        elif isinstance(agent, MyAgentStones):
            agent_type = "Stones Picker"
        elif isinstance(agent, MyAgentChest):
            agent_type = "Treasure Opener"
        else:
            agent_type = "Unknown"
        position = agent.getPos()  # Get the agent's position
        print(f"Agent ID: {agent_id}, Type: {agent_type}, Position: {position}")
    print("-" * 30)







# Visualization
def draw_environment(screen, env, agents):
    screen.fill(WHITE)
    font = pygame.font.SysFont(None, 24)

    # Draw grid
    for x in range(env.tailleX):
        for y in range(env.tailleY):
            rect = pygame.Rect(y * CELL_SIZE, x * CELL_SIZE, CELL_SIZE, CELL_SIZE)
            pygame.draw.rect(screen, GRAY, rect, 1)

    # Draw depot
    depot_x, depot_y = env.posUnload
    depot_rect = pygame.Rect(depot_y * CELL_SIZE, depot_x * CELL_SIZE, CELL_SIZE, CELL_SIZE)
    pygame.draw.rect(screen, GREEN, depot_rect)

    # Draw treasures
    for x in range(env.tailleX):
        for y in range(env.tailleY):
            if env.grilleTres[x][y] is not None:
                treasure = env.grilleTres[x][y]
                if treasure.getValue() == 0:
                    continue
                color = YELLOW if treasure.getType() == 1 else RED
                treasure_rect = pygame.Rect(y * CELL_SIZE, x * CELL_SIZE, CELL_SIZE, CELL_SIZE)
                pygame.draw.rect(screen, color, treasure_rect)
                value_text = font.render(str(treasure.getValue()), True, BLACK)
                text_rect = value_text.get_rect(center=treasure_rect.center)
                screen.blit(value_text, text_rect)

                # Add lock symbol for treasures that are not open
                if not treasure.isOpen():
                    lock_text = font.render("*", True, BLACK)  # "L" for locked
                    lock_rect = lock_text.get_rect(center=(treasure_rect.centerx, treasure_rect.centery - CELL_SIZE // 6))
                    screen.blit(lock_text, lock_rect)

    # Draw agents
    for agent in agents.values():
        x, y = agent.getPos()
        center = (y * CELL_SIZE + CELL_SIZE // 2, x * CELL_SIZE + CELL_SIZE // 2)
        # Set color based on agent type
        if isinstance(agent, MyAgentGold):
            color = YELLOW
        elif isinstance(agent, MyAgentStones):
            color = RED
        else:
            color = BLUE
        # Draw black outline
        pygame.draw.circle(screen, BLACK, center, CELL_SIZE // 3 + 2)  # Slightly larger circle for outline
        pygame.draw.circle(screen, color, center, CELL_SIZE // 3)  # Agent's colored circle
        
        # Draw "A" for the agent
        agent_text = font.render("A", True, BLACK)
        text_rect = agent_text.get_rect(center=center)
        screen.blit(agent_text, text_rect)

        # Draw backpack value below the agent
        if isinstance(agent, MyAgentChest):
            continue
        backpack_value = agent.backPack  
        backpack_text = font.render(str(backpack_value), True, BLACK)
        backpack_rect = backpack_text.get_rect(center=(center[0], center[1] + CELL_SIZE // 4))
        screen.blit(backpack_text, backpack_rect)

    pygame.display.flip()
def trash():
    pygame.init()
    env, agents = loadFileConfig("env1.txt")
    
    # Display agents info
    display_agents_info(agents)
    
    screen = pygame.display.set_mode((env.tailleY * CELL_SIZE, env.tailleX * CELL_SIZE))
    pygame.display.set_caption("Multi-Agent Treasure Hunt")
    clock = pygame.time.Clock()

    # Draw the initial state
    draw_environment(screen, env, agents)
    pygame.time.wait(2000)  # Pause to observe the initial state

   # treasure_generation_interval = 10  # Every 100 frames (or adjust as needed)
    #frame_count = 0
    horizon = 100  # Total steps in the simulation

    # Perform the sequence of actions
    try:
        # Actions for agent0
        agents.get("agent0").move(7, 4, 7, 3)
        draw_environment(screen, env, agents)
        pygame.time.wait(1000)

        agents.get("agent0").move(7, 3, 6, 3)
        draw_environment(screen, env, agents)
        pygame.time.wait(1000)

        agents.get("agent0").open()
        draw_environment(screen, env, agents)
        pygame.time.wait(1000)

        print(env)  # Debug print to see the environment's state in the console

        agents.get("agent0").move(6, 3, 7, 3)
        draw_environment(screen, env, agents)
        pygame.time.wait(1000)

        print(env)  # Debug print after moving back

        # Actions for agent4
        agents.get("agent4").move(6, 7, 6, 6)
        draw_environment(screen, env, agents)
        pygame.time.wait(1000)

        agents.get("agent4").move(6, 6, 6, 5)
        draw_environment(screen, env, agents)
        pygame.time.wait(1000)

        agents.get("agent4").move(6, 5, 6, 4)
        draw_environment(screen, env, agents)
        pygame.time.wait(1000)

        agents.get("agent4").move(6, 4, 6, 3)
        draw_environment(screen, env, agents)
        pygame.time.wait(1000)

        agents.get("agent4").send("agent0", "Hello, I am sending a message to agent0")
        agents.get("agent0").readMail()

        print(env)  # Debug print before loading

        agents.get("agent4").load(env)  # Load treasure
        draw_environment(screen, env, agents)
        pygame.time.wait(1000)
        

        agents.get("agent4").move(6, 3, 5, 3)
        draw_environment(screen, env, agents)
        pygame.time.wait(1000)
        print(agents.get("agent4"))  # Debug print after loading


    except Exception as e:
        print(f"Error during execution: {e}")

    # Keep the window open to observe
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:  # Exit on window close
                running = False

       # Generate new treasures every 10 steps
        # make the agents execute their plans
        # for t in range(horizon):
        #     if(t%10 == 0):
        #         env.gen_new_treasures(random.randint(0,5), 7)
        #         draw_environment(screen, env, agents)
        
        #draw_environment(screen, env, agents)
        #pygame.time.wait(3000)  # 500 ms delay per step (adjust as needed)




        clock.tick(FPS)

    pygame.quit()


if __name__ == "__main__":
    trash()