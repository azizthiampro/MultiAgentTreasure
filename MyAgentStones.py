from MyAgent import MyAgent
import heapq

class MyAgentStones(MyAgent):
    def __init__(self, id, initX, initY, env, capacity):
        MyAgent.__init__(self, id, initX, initY, env)
        self.stone = 0  # Quantity of collected stones
        self.backPack = capacity  # Backpack capacity
        self.target_treasure = None  # Current target stone
        self.myagentScore=0

    # Return quantity of collected stones
    def getTreasure(self):
        return self.stone

    # Unload stones at the depot
    def unload(self, gui=None):
            """Unload stones at the depot if at the unload position."""
            if (self.posX, self.posY) == self.env.posUnload:
                amount_unloaded = self.stone
                self.env.unload(self)
                print(f"[UNLOAD] {self.getId()} unloaded {amount_unloaded} stones at depot.")
                self.myagentScore += amount_unloaded
                self.stone = 0

                # Trigger floating text if GUI is provided
                if gui:
                    gui.add_floating_text(amount_unloaded, (self.posX, self.posY))
            else:
                print(f"[MOVE TO DEPOT] {self.getId()} moving to unload stones.")


    # Return agent type (2 for stones)
    def getType(self):
        return 2

    # Load the stone treasure at the current position (Using Existing `load` Function)
    def load(self, env):
        """Uses the existing `load` function from `Environment.py`."""
        env.load(self)

    # Add stones to the backpack
    def addTreasure(self, t):
        if self.stone + t <= self.backPack:
            self.stone += t
        else:
            self.stone = self.backPack

    # Find the nearest available stone
    def find_nearest_stone(self):
        """Find the closest stone that is available to pick up."""
        stones = [
            (x, y) for x in range(self.env.tailleX) for y in range(self.env.tailleY)
            if self.env.grilleTres[x][y] is not None and self.env.grilleTres[x][y].getType() == 2
        ]
        if not stones:
            return None
        return min(stones, key=lambda s: abs(self.posX - s[0]) + abs(self.posY - s[1]))

    # Move the agent towards the target
    def move_toward_target(self):
        """Move towards the target stone and load it if possible."""
        if not self.target_treasure:
            self.target_treasure = self.find_nearest_stone()
            if not self.target_treasure:
                print(f"[INFO] {self.getId()} found no available stones.")
                return

        target_x, target_y = self.target_treasure
        if (self.posX, self.posY) == (target_x, target_y):  # Already at the stone
            self.load(self.env)  # ✅ Use existing `load` function
            self.target_treasure = None  # Reset target after loading
            return

        # Pathfinding towards the target
        path = self.a_star_pathfinding((self.posX, self.posY), (target_x, target_y))
        if not path:
            print(f"[WARNING] {self.getId()} could not find a path to ({target_x}, {target_y}).")
            self.target_treasure = None
            return

        next_x, next_y = path.pop(0)
        if self.env.grilleAgent[next_x][next_y] is None:
            self.move(self.posX, self.posY, next_x, next_y)

    # Move agent to the depot when full
    def move_to_depot(self):
        """Move the agent towards the depot to unload stones."""
        depot_x, depot_y = self.env.posUnload
        path = self.a_star_pathfinding((self.posX, self.posY), (depot_x, depot_y))
        if not path:
            print(f"[WARNING] {self.getId()} cannot find a path to the depot.")
            return

        next_x, next_y = path.pop(0)
        if self.env.grilleAgent[next_x][next_y] is None:
            self.move(self.posX, self.posY, next_x, next_y)

    def move_outside_depot_zone(self, radius=2):
        """Move the agent to the nearest cell outside the depot zone with no treasure."""
        depot_x, depot_y = self.env.posUnload

        # Find all blank cells outside the depot zone
        candidates = [
            (x, y) for x in range(self.env.tailleX) for y in range(self.env.tailleY)
            if (abs(x - depot_x) > radius or abs(y - depot_y) > radius)
            and self.env.grilleAgent[x][y] is None  # Ensure the cell is unoccupied
            and self.env.grilleTres[x][y] is None   # Ensure the cell has no treasure
        ]

        if not candidates:
            print(f"[INFO] {self.getId()} found no available blank cell outside depot zone.")
            return

        # Select the nearest blank cell
        nearest_blank = min(candidates, key=lambda c: abs(self.posX - c[0]) + abs(self.posY - c[1]))
        print(f"[MOVE] {self.getId()} moving outside depot zone to {nearest_blank}.")

        # Move towards the blank cell, but check for new assignments while moving
        path = self.a_star_pathfinding((self.posX, self.posY), nearest_blank)

        for step in path:
            # Check for new treasure before each move
            if self.find_nearest_stone():
                print(f"[INTERRUPT] {self.getId()} assigned new treasure while moving. Heading to collect.")
                self.target_treasure = self.find_nearest_stone()
                self.move_toward_target()
                return  # Exit the loop and collect the treasure

            # Proceed with moving to the blank cell if no treasure is assigned
            next_x, next_y = step
            if self.env.grilleAgent[next_x][next_y] is None:
                self.move(self.posX, self.posY, next_x, next_y)

    def is_in_depot_zone(self, radius=2):
        """Checks if the agent is within the specified radius of the depot."""
        depot_x, depot_y = self.env.posUnload
        return abs(self.posX - depot_x) <= radius and abs(self.posY - depot_y) <= radius

    # A* pathfinding algorithm
    def a_star_pathfinding(self, start, goal):
        """Finds the shortest path avoiding obstacles using A*."""
        def heuristic(a, b):
            return abs(a[0] - b[0]) + abs(a[1] - b[1])

        open_set = []
        heapq.heappush(open_set, (0, start))
        came_from = {}
        g_score = {start: 0}
        f_score = {start: heuristic(start, goal)}

        while open_set:
            _, current = heapq.heappop(open_set)
            if current == goal:
                path = []
                while current in came_from:
                    path.append(current)
                    current = came_from[current]
                path.reverse()
                return path

            for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                neighbor = (current[0] + dx, current[1] + dy)
                if neighbor[0] < 0 or neighbor[0] >= self.env.tailleX or neighbor[1] < 0 or neighbor[1] >= self.env.tailleY:
                    continue
                if self.env.grilleAgent[neighbor[0]][neighbor[1]] is not None and neighbor != goal:
                    continue

                tentative_g_score = g_score[current] + 1
                if neighbor not in g_score or tentative_g_score < g_score[neighbor]:
                    came_from[neighbor] = current
                    g_score[neighbor] = tentative_g_score
                    heapq.heappush(open_set, (g_score[neighbor], neighbor))

        return []  # No path found

    def __str__(self):
        return f"agent Stone {self.id} ({self.posX}, {self.posY})"
    

def stone_policy(stone_agent,gui):
    """Executes the stone collection policy for a stone agent."""
    print(f"[POLICY] Processing {stone_agent.getId()} at {stone_agent.getPos()}")

    # ✅ **Step 1: If at depot, unload & search for new stones**
    if (stone_agent.posX, stone_agent.posY) == stone_agent.env.posUnload:
        if stone_agent.stone > 0:
            print(f"[UNLOADING] {stone_agent.getId()} unloading at depot...")
            stone_agent.unload(gui)  # ✅ Unloads stones
            print(f"[UNLOADED] {stone_agent.getId()} is now empty and ready to collect more stone.")
        else:
            print(f"[INFO] {stone_agent.getId()} is at depot but backpack is empty.")

        # ✅ Move outside depot zone if no treasure is assigned
        if not stone_agent.find_nearest_stone():
            stone_agent.move_outside_depot_zone(radius=2)
            return  # Exit early if no stone is found

    # ✅ **Step 2: Check if there's stone at the agent's position & load it**
    current_treasure = stone_agent.env.grilleTres[stone_agent.posX][stone_agent.posY]
    if current_treasure and current_treasure.getType() == 2:
        available_space = stone_agent.backPack - stone_agent.stone
        if available_space > 0:
            amount_picked = min(available_space, current_treasure.getValue())
            stone_agent.load(stone_agent.env)
            print(f"[LOAD] {stone_agent.getId()} picked up {amount_picked} stone at ({stone_agent.posX}, {stone_agent.posY})")
            stone_agent.env.grilleTres[stone_agent.posX][stone_agent.posY] = None

    # ✅ **Step 3: Decide next action based on storage and treasure availability**
    if stone_agent.stone >= stone_agent.backPack:
        print(f"[UNLOAD] {stone_agent.getId()} backpack full. Moving to depot.")
        stone_agent.move_to_depot()

    elif stone_agent.stone > 0 and not stone_agent.find_nearest_stone():
        # ✅ **If there is stone in the backpack but no new treasure is available, unload it**
        print(f"[NO TREASURE] {stone_agent.getId()} has stone but no treasure found. Moving to depot to unload.")
        stone_agent.move_to_depot()

    elif not stone_agent.find_nearest_stone():
        # ✅ **Freeze if outside depot and no treasure is available**
        if not stone_agent.is_in_depot_zone(radius=2):
            print(f"[WAITING] {stone_agent.getId()} is outside the depot and no treasure is available. Waiting...")
            return  # Agent stays in place and waits
        else:
            print(f"[INFO] {stone_agent.getId()} is inside depot zone with no treasure. Moving outside.")
            stone_agent.move_outside_depot_zone(radius=2)

    else:
        # ✅ Move to the nearest stone if available
        stone_agent.target_treasure = stone_agent.find_nearest_stone()
        if stone_agent.target_treasure:
            print(f"[MOVE] {stone_agent.getId()} moving towards treasure at {stone_agent.target_treasure}")
            stone_agent.move_toward_target()