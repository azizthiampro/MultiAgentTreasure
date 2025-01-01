import pygame
from Environment import Environment
from MyAgentGold import MyAgentGold
from MyAgentChest import MyAgentChest
from MyAgentStones import MyAgentStones
from Treasure import Treasure
import random
from heapq import heappush, heappop

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

# A* Pathfinding
def a_star_search(start, goal, env):
    def heuristic(a, b):
        dx = abs(a[0] - b[0])
        dy = abs(a[1] - b[1])
        return dx + dy + (1.414 - 2) * min(dx, dy)  # Manhattan + diagonal

    neighbors = [
        (-1, 0), (1, 0), (0, -1), (0, 1),  # Cardinal directions
        (-1, -1), (-1, 1), (1, -1), (1, 1)  # Diagonal directions
    ]

    open_set = []
    heappush(open_set, (0, start))
    came_from = {}
    g_score = {start: 0}
    f_score = {start: heuristic(start, goal)}

    while open_set:
        _, current = heappop(open_set)

        if current == goal:
            path = []
            while current in came_from:
                path.append(current)
                current = came_from[current]
            path.reverse()
            return path

        for dx, dy in neighbors:
            neighbor = (current[0] + dx, current[1] + dy)
            if neighbor[0] < 0 or neighbor[0] >= env.tailleX or neighbor[1] < 0 or neighbor[1] >= env.tailleY:
                continue
            if env.grilleAgent[neighbor[0]][neighbor[1]] is not None:
                continue

            tentative_g_score = g_score[current] + (1.414 if dx != 0 and dy != 0 else 1)

            if neighbor not in g_score or tentative_g_score < g_score[neighbor]:
                came_from[neighbor] = current
                g_score[neighbor] = tentative_g_score
                f_score[neighbor] = tentative_g_score + heuristic(neighbor, goal)
                heappush(open_set, (f_score[neighbor], neighbor))

    return []

# Execute agent task with A*
def execute_agent_task(agent, target_treasure, screen, env, agents):
    current_pos = agent.getPos()
    path = a_star_search(current_pos, target_treasure, env)

    if not path:
        print(f"No path found for {agent.getId()} to {target_treasure}.")
        return

    for next_pos in path:
        next_x, next_y = next_pos
        agent.move(current_pos[0], current_pos[1], next_x, next_y)
        draw_environment(screen, env, agents)
        pygame.time.wait(500)
        current_pos = next_pos

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
        """Find the nearest unclaimed treasure for the agent."""
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

    def assign_target(agent, treasures):
        """Assign the nearest unclaimed treasure to an agent."""
        target_treasure = find_nearest_treasure(agent, treasures)
        if target_treasure is not None:
            assigned_treasures.add(target_treasure)
            return target_treasure
        return None

    def move_agent(agent, target, env):
        """Move the agent one step closer to the target."""
        if target is None:
            return False  # No target, no movement

        current_pos = agent.getPos()
        path = a_star_search(current_pos, target, env)

        if not path:
            return False  # No valid path to target

        next_pos = path[0]  # Get the next step in the path
        agent.move(current_pos[0], current_pos[1], next_pos[0], next_pos[1])
        return True

    def broadcast_intention(agent, target, other_agent):
        """Broadcast the agent's intention to the other agent."""
        message = f"Intention: {target}"
        agent.send(other_agent.getId(), message)
        print(f"{agent.getId()} -> {other_agent.getId()}: {message}")

    def resolve_conflict(agent, target):
        """Check if the agent's target conflicts with another agent's intention."""
        if target in assigned_treasures:
            print(f"{agent.getId()}: Conflict detected for {target}. Recalculating target...")
            assigned_treasures.remove(target)  # Release the target for reassignment
            return assign_target(agent, locked_treasures)
        return target

    # Assign initial targets to agents
    agent0 = agents.get("agent0")
    agent1 = agents.get("agent1")
    target0 = assign_target(agent0, locked_treasures)
    target1 = assign_target(agent1, locked_treasures)

    print(f"Initial targets: Agent0 -> {target0}, Agent1 -> {target1}")

    # Main simulation loop
    running = True
    simulation_complete = False  # Flag to track if the simulation has ended

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        if not simulation_complete:
            # Agents broadcast their intentions
            broadcast_intention(agent0, target0, agent1)
            broadcast_intention(agent1, target1, agent0)

            # Resolve potential conflicts
            target0 = resolve_conflict(agent0, target0)
            target1 = resolve_conflict(agent1, target1)

            # Move both agents toward their targets
            agent0_moved = move_agent(agent0, target0, env)
            agent1_moved = move_agent(agent1, target1, env)

            # Check if agents reach their targets
            if agent0.getPos() == target0:
                agent0.open()
                draw_environment(screen, env, agents)
                locked_treasures.remove(target0)
                assigned_treasures.remove(target0)
                target0 = assign_target(agent0, locked_treasures)  # Assign a new target

            if agent1.getPos() == target1:
                agent1.open()
                draw_environment(screen, env, agents)
                locked_treasures.remove(target1)
                assigned_treasures.remove(target1)
                target1 = assign_target(agent1, locked_treasures)  # Assign a new target

            # Redraw the environment after each step
            pygame.time.wait(250)

            draw_environment(screen, env, agents)
            clock.tick(FPS)

            # Check if there are no more treasures
            if not locked_treasures:
                simulation_complete = True
                print("\nSimulation complete. Waiting for user to close the game...")

        else:
            # Keep the screen open until the user quits
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False 
if __name__ == "__main__":
    trash()