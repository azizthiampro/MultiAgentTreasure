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
                    lock_text = font.render("*", True, BLACK)
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
        pygame.draw.circle(screen, BLACK, center, CELL_SIZE // 3 + 2)
        pygame.draw.circle(screen, color, center, CELL_SIZE // 3)
        
        # Draw "A" for the agent
        agent_text = font.render("A", True, BLACK)
        text_rect = agent_text.get_rect(center=center)
        screen.blit(agent_text, text_rect)

    pygame.display.flip()

# Helper function: Execute a single agent's task
def execute_agent_task(agent, target_treasure, screen, env, agents):
    current_x, current_y = agent.getPos()
    target_x, target_y = target_treasure

    while (current_x, current_y) != (target_x, target_y):
        if current_x < target_x:
            next_x = current_x + 1
        elif current_x > target_x:
            next_x = current_x - 1
        else:
            next_x = current_x

        if current_y < target_y:
            next_y = current_y + 1
        elif current_y > target_y:
            next_y = current_y - 1
        else:
            next_y = current_y

        agent.move(current_x, current_y, next_x, next_y)
        draw_environment(screen, env, agents)
        pygame.time.wait(500)

        current_x, current_y = next_x, next_y

    agent.open()
    draw_environment(screen, env, agents)
    pygame.time.wait(1000)

def trash():
    pygame.init()
    env, agents = loadFileConfig("env1.txt")
    display_agents_info(agents)

    screen = pygame.display.set_mode((env.tailleY * CELL_SIZE, env.tailleX * CELL_SIZE))
    pygame.display.set_caption("Multi-Agent Treasure Hunt")
    clock = pygame.time.Clock()

    draw_environment(screen, env, agents)
    pygame.time.wait(2000)

    locked_treasures = [
        (x, y) for x in range(env.tailleX) for y in range(env.tailleY)
        if env.grilleTres[x][y] is not None and not env.grilleTres[x][y].isOpen()
    ]

    assigned_treasures = set()

    def find_nearest_treasure(agent, treasures):
        agent_pos = agent.getPos()
        nearest_treasure = None
        min_distance = float('inf')
        for treasure in treasures:
            if treasure not in assigned_treasures:
                distance = abs(agent_pos[0] - treasure[0]) + abs(agent_pos[1] - treasure[1])
                if distance < min_distance:
                    nearest_treasure = treasure
                    min_distance = distance
        return nearest_treasure

    def agent_protocol(agent, other_agent):
        target_treasure = find_nearest_treasure(agent, locked_treasures)
        if target_treasure is not None:
            assigned_treasures.add(target_treasure)
            agent.send(other_agent.getId(), f"Target:{target_treasure}")
            print(f"{agent.getId()} sent to {other_agent.getId()}: Target:{target_treasure}")
            return target_treasure
        return None

    try:
        agent0 = agents.get("agent0")
        agent1 = agents.get("agent1")

        for _ in range(len(locked_treasures)):
            target0 = agent_protocol(agent0, agent1)
            if target0:
                execute_agent_task(agent0, target0, screen, env, agents)

            target1 = agent_protocol(agent1, agent0)
            if target1:
                execute_agent_task(agent1, target1, screen, env, agents)

    except Exception as e:
        print(f"Error during execution: {e}")

    print("\nSimulation complete. Closing...")
    pygame.quit()

if __name__ == "__main__":
    trash()