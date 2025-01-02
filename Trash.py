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
RED = (225, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 175, 0)
GRAY = (200, 200, 200)
YELLOW = (255, 225, 0)

CELL_SIZE = 55
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

def display_score(screen, env):
    """Display the score in a horizontal block at the bottom of the screen."""
    font = pygame.font.SysFont(None, 36)  # Larger font for the score
    score_text = font.render(f"Score: {env.score}", True, BLACK)
    screen_width = screen.get_width()

    # Define the area for the score block
    score_block_height = 50  # Height of the horizontal block
    score_block_rect = pygame.Rect(0, screen.get_height() - score_block_height, screen_width, score_block_height)

    # Fill the score block with a background color
    pygame.draw.rect(screen, GRAY, score_block_rect)

    # Render the score text
    text_rect = score_text.get_rect(center=(screen_width // 2, screen.get_height() - score_block_height // 2))
    screen.blit(score_text, text_rect)

# Visualization
def draw_environment(screen, env, agents):
    screen.fill(WHITE)
    font = pygame.font.SysFont(None, 18)  # Smaller font for capacity display

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
            remaining_capacity = agent.backPack - agent.gold
        elif isinstance(agent, MyAgentStones):
            color = RED
            remaining_capacity = agent.backPack - agent.stone
        else:
            color = BLUE
            remaining_capacity = None  # Chests don't have backpack capacity

        # Draw agent circle with black outline
        pygame.draw.circle(screen, BLACK, center, CELL_SIZE // 2.5 + 2)
        pygame.draw.circle(screen, color, center, CELL_SIZE // 2.5)

        # Draw "A" for the agent
        agent_text = font.render("A", True, BLACK)
        text_rect = agent_text.get_rect(center=center)
        screen.blit(agent_text, text_rect)

        # Draw remaining capacity in the top-right corner inside the circle
        if remaining_capacity is not None:
            remaining_text = font.render(str(remaining_capacity), True, BLACK)
            offset_x = CELL_SIZE // 6  # Adjust to position it in the top-right
            offset_y = -CELL_SIZE // 6
            remaining_rect = remaining_text.get_rect(center=(center[0] + offset_x, center[1] + offset_y))
            screen.blit(remaining_text, remaining_rect)

    # Display the score in the horizontal block
    display_score(screen, env)

    pygame.display.flip()
def backPackFull( agent):
    if isinstance(agent, MyAgentGold) and agent.backPack == agent.gold:
        return True
    elif isinstance(agent, MyAgentStones) and agent.backPack == agent.stone:    
        return True
    
    return False


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

            # Check boundaries
            if neighbor[0] < 0 or neighbor[0] >= env.tailleX or neighbor[1] < 0 or neighbor[1] >= env.tailleY:
                continue

            # Check for temporary obstacles (occupied cells)
            if env.grilleAgent[neighbor[0]][neighbor[1]] is not None and neighbor != goal:
                continue  # Allow the goal cell even if occupied (it will be cleared)

            tentative_g_score = g_score[current] + (1.414 if dx != 0 and dy != 0 else 1)

            if neighbor not in g_score or tentative_g_score < g_score[neighbor]:
                came_from[neighbor] = current
                g_score[neighbor] = tentative_g_score
                f_score[neighbor] = tentative_g_score + heuristic(neighbor, goal)
                heappush(open_set, (f_score[neighbor], neighbor))

    return []  # No path found

def move(self, agent, x1, y1, x2, y2):
    if not (0 <= x2 < self.tailleX and 0 <= y2 < self.tailleY):
        print("Invalid move: Out of bounds")
        return False

    if self.grilleAgent[x2][y2] is not None:
        print("Invalid move: Cell occupied")
        return False

    if self.grilleAgent[x1][y1] == agent:
        self.grilleAgent[x1][y1] = None  # Clear previous position
        self.grilleAgent[x2][y2] = agent  # Move agent
        agent.posX, agent.posY = x2, y2  # Update agent's internal position
        return True

    print("Invalid move: Agent not at the start position")
    return False

def is_cell_free(env, x, y):
        """Check if a cell is free (not occupied by an agent or a treasure)."""
        if not (0 <= x < env.tailleX and 0 <= y < env.tailleY):
            return False  # Out of bounds
        if env.grilleAgent[x][y] is not None:
            return False  # Occupied by an agent
        if env.grilleTres[x][y] is not None:
            return False  # Occupied by a treasure
        return True  # Cell is free
def move_to_depot_and_unload(agent, screen, env, agents):
    """Move the agent to the depot, unload the backpack, and vacate the depot."""
    depot_pos = env.posUnload
    current_pos = agent.getPos()

    # Find path to depot
    path_to_depot = a_star_search(current_pos, depot_pos, env)

    # Move step by step to the depot
    for next_pos in path_to_depot:
        next_x, next_y = next_pos
        if not agent.move(current_pos[0], current_pos[1], next_x, next_y):
            print(f"{agent.getId()} failed to move to depot.")
            return
        draw_environment(screen, env, agents)
        pygame.time.wait(500)
        current_pos = next_pos

    # Unload items at depot
    env.unload(agent)
    print(f"{agent.getId()} unloaded items at the depot. Score updated to {env.score}")

    # Reset the agent's carried treasure to 0
    if isinstance(agent, MyAgentGold):
        agent.gold = 0
    elif isinstance(agent, MyAgentStones):
        agent.stone = 0

    # Find a free cell near the depot to vacate the depot
    neighbors = [(-1, 0), (1, 0), (0, -1), (0, 1)]  # Cardinal directions
    vacated = False
    for dx, dy in neighbors:
        new_x, new_y = depot_pos[0] + dx, depot_pos[1] + dy
        if is_cell_free(env, new_x, new_y):
            if agent.move(depot_pos[0], depot_pos[1], new_x, new_y):
                print(f"{agent.getId()} vacated the depot to ({new_x}, {new_y}).")
                vacated = True
                break

    if not vacated:
        print(f"{agent.getId()} could not vacate the depot due to lack of free cells.")

    # Redraw environment to reflect changes
    draw_environment(screen, env, agents)

# Execute agent task with A*
def execute_agent_task(agent, target_treasure, screen, env, agents):
    """Execute task: move the agent to the treasure cell and load it."""
    if target_treasure is None:
        print(f"No target assigned to {agent.getId()}.")
        return

    current_pos = agent.getPos()
    path = a_star_search(current_pos, target_treasure, env)

    if not path:
        print(f"No path found for {agent.getId()} to {target_treasure}.")
        return  # Skip if no valid path

    # Move agent step by step to the treasure cell
    for next_pos in path:
        next_x, next_y = next_pos

        # Check if the target cell is occupied
        while env.grilleAgent[target_treasure[0]][target_treasure[1]] is not None:
            print(f"{agent.getId()} is waiting for cell {target_treasure} to be free.")
            pygame.time.wait(500)  # Wait for the opener to vacate the cell

        # Move agent step by step
        if not agent.move(current_pos[0], current_pos[1], next_x, next_y):
            print(f"{agent.getId()} failed to move to ({next_x}, {next_y}).")
            return

        draw_environment(screen, env, agents)
        pygame.time.wait(250)
        current_pos = next_pos

    # Attempt to load the treasure if in the correct cell
    if current_pos == target_treasure:
        if isinstance(agent, (MyAgentGold, MyAgentStones)):
            if agent.load(env):  # Mark treasure as collected if load is successful
                print(f"{agent.getId()} successfully collected treasure at {target_treasure}.")
                env.grilleTres[target_treasure[0]][target_treasure[1]] = None  # Mark treasure as collected

            # Check if the agent's backpack is full
            if backPackFull(agent):
                print(f"{agent.getId()}'s backpack is full. Moving to depot to unload.")
                move_to_depot_and_unload(agent, screen, env, agents)

        draw_environment(screen, env, agents)
    else:
        print(f"{agent.getId()} is not in the correct cell to load the treasure.")

# Main simulation
def trash():
    pygame.init()
    env, agents = loadFileConfig("env1.txt")
    display_agents_info(agents)

    # Calculate screen dimensions, reserving space for the score block
    score_block_height = 50  # Height for the score block
    screen_height = env.tailleX * CELL_SIZE + score_block_height
    screen = pygame.display.set_mode((env.tailleY * CELL_SIZE, screen_height))
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
        if not treasures:
            return None  # No treasures to assign
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
            print(f"No valid path for {agent.getId()} to {target}.")
            return False  # No valid path to target

        next_pos = path[0]  # Get the next step in the path
        agent.move(current_pos[0], current_pos[1], next_pos[0], next_pos[1])
        return True
    
    def missionStatus(agent, all_agents, flag):
        """Broadcast their status mission to all other agents."""
        id = agent.getId()

        if flag == 0:
           message = f"Status {id}: Progress"
        elif flag == 1:
            message = f"Status {id}: Completed"

        for other_agent in all_agents.values():
            if other_agent.getId() != agent.getId():
                agent.send(other_agent.getId(), message)
                print(f"{agent.getId()} -> {other_agent.getId()}: {message}")

    def broadcast_intention(agent, target, all_agents):
        if target is None:
            return  # Skip if no target

        # Check for agents with progress status
        progress_agents = check_for_progress_status(agent)

        treasure_type = agent.env.grilleTres[target[0]][target[1]].getType() if agent.env.grilleTres[target[0]][target[1]] else None
        message = f"Intention: Open {target} Type {treasure_type}"
        
        for other_agent in all_agents.values():
            if other_agent.getId() in progress_agents:
                print(f"{agent.getId()} skipped sending intention to {other_agent.getId()} (status=progress).")
                continue
            if other_agent.getId() != agent.getId():
                agent.send(other_agent.getId(), message)
                print(f"{agent.getId()} -> {other_agent.getId()}: {message}")
                
    def notify_treasure_unlocked(opener, target, all_agents):
        """Notify relevant agents and assign the collection task."""
        if target is None:
            return  # Skip if no target

        treasure_type = opener.env.grilleTres[target[0]][target[1]].getType()
        print(f"{opener.getId()} unlocked treasure at {target}.")

        # Resolve conflict and choose the best agent for collection
        chosen_agent = resolve_collection_conflict(treasure_type, target, all_agents, opener.env)

        if chosen_agent:
            print(f"{chosen_agent.getId()} is assigned to collect treasure at {target}.")
            missionStatus(chosen_agent, all_agents, 0)

            # Attempt to vacate the cell for the collector
            neighbors = [(-1, 0), (1, 0), (0, -1), (0, 1)]
            for dx, dy in neighbors:
                new_x, new_y = target[0] + dx, target[1] + dy
                if is_cell_free(opener.env, new_x, new_y):
                    opener.move(target[0], target[1], new_x, new_y)
                    print(f"{opener.getId()} vacated cell {target} for {chosen_agent.getId()}.")
                    break

            execute_agent_task(chosen_agent, target, screen, opener.env, all_agents)
            missionStatus(chosen_agent, all_agents, 1)
        else:
            print(f"No eligible agents to collect treasure at {target}.")
        # Example: Opener agent checking for status messages in the mailbox
    def check_for_progress_status(agent):
        progress_agents = set()
        
        # Check all messages in the mailbox
        while agent.mailBox:
            sender, content = agent.readMail()
            if "Status" in content and "Progress" in content:
                parts = content.split(":")
                if len(parts) > 1:
                    progress_agents.add(parts[0].split()[1])  # Extract the agent ID from the message
        
        return progress_agents
    


    def resolve_collection_conflict(treasure_type, target, all_agents, env):
        """Determine which agent should collect the treasure."""
        relevant_agents = [
            agent for agent in all_agents.values()
            if (isinstance(agent, MyAgentGold) and treasure_type == 1 and agent.backPack - agent.gold > 0) or
               (isinstance(agent, MyAgentStones) and treasure_type == 2 and agent.backPack - agent.stone > 0)
        ]

        if not relevant_agents:
            print(f"No eligible agents to collect treasure at {target}.")
            return None

        # Determine the closest eligible agent
        chosen_agent = None
        min_distance = float('inf')

        for agent in relevant_agents:
            agent_pos = agent.getPos()
            distance = abs(agent_pos[0] - target[0]) + abs(agent_pos[1] - target[1])
            if distance < min_distance:
                chosen_agent = agent
                min_distance = distance
            elif distance == min_distance:  # Tie-breaking
                if chosen_agent and agent.getId() < chosen_agent.getId():
                    chosen_agent = agent

        return chosen_agent

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
            broadcast_intention(agent0, target0, agents)
            broadcast_intention(agent1, target1, agents)

            # Move both opener agents toward their targets
            agent0_moved = move_agent(agent0, target0, env)
            agent1_moved = move_agent(agent1, target1, env)

            # Check if opener agents reach their targets
            if agent0.getPos() == target0:
                agent0.open()  # Perform the opening action
                draw_environment(screen, env, agents)  # Update the display to reflect the opening
                pygame.time.wait(500)  # Pause briefly to show the opener's state
                notify_treasure_unlocked(agent0, target0, agents)
                draw_environment(screen, env, agents)  # Update display after unlocking
                if target0 in locked_treasures:
                    locked_treasures.remove(target0)
                assigned_treasures.discard(target0)
                target0 = assign_target(agent0, locked_treasures)  # Assign a new target

            if agent1.getPos() == target1:
                agent1.open()  # Perform the opening action
                draw_environment(screen, env, agents)  # Update the display to reflect the opening
                pygame.time.wait(500)  # Pause briefly to show the opener's state
                notify_treasure_unlocked(agent1, target1, agents)
                draw_environment(screen, env, agents)  # Update display after unlocking
                if target1 in locked_treasures:
                    locked_treasures.remove(target1)
                assigned_treasures.discard(target1)
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

    print("\nGame closed.")
    pygame.quit()
if __name__ == "__main__":
    trash()