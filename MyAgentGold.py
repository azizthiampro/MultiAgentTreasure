from MyAgent import MyAgent
import heapq

class MyAgentGold(MyAgent):
    def __init__(self, id, initX, initY, env, capacity):
        MyAgent.__init__(self, id, initX, initY, env)
        self.gold = 0  # Quantity of collected golds
        self.backPack = capacity  # Backpack capacity
        self.target_treasure = None  # Current target gold
        self.myagentScore=0

    # Return quantity of collected golds
    def getTreasure(self):
        return self.gold

        # Unload golds at the depot
    def unload(self, gui=None):
        """Unload golds at the depot if at the unload position."""
        if (self.posX, self.posY) == self.env.posUnload:
            amount_unloaded = self.gold
            self.env.unload(self)
            print(f"[UNLOAD] {self.getId()} unloaded {amount_unloaded} golds at depot.")
            self.myagentScore += amount_unloaded
            self.gold = 0

            # Trigger floating text if GUI is provided
            if gui:
                gui.add_floating_text(amount_unloaded, (self.posX, self.posY))
        else:
            print(f"[MOVE TO DEPOT] {self.getId()} moving to unload golds.")


    # Return agent type (2 for golds)
    def getType(self):
        return 1

    # Load the gold treasure at the current position (Using Existing `load` Function)
    def load(self, env):
        """Uses the existing `load` function from `Environment.py`."""
        env.load(self)

    # Add golds to the backpack
    def addTreasure(self, t):
        if self.gold + t <= self.backPack:
            self.gold += t
        else:
            self.gold = self.backPack

    # Find the nearest available gold
    def find_nearest_gold(self):
        """Find the closest gold that is available to pick up."""
        golds = [
            (x, y) for x in range(self.env.tailleX) for y in range(self.env.tailleY)
            if self.env.grilleTres[x][y] is not None and self.env.grilleTres[x][y].getType() == 1
        ]
        if not golds:
            return None
        return min(golds, key=lambda s: abs(self.posX - s[0]) + abs(self.posY - s[1]))

    # Move the agent towards the target
    def move_toward_target(self):
        """Move towards the target gold and load it if possible."""
        if not self.target_treasure:
            self.target_treasure = self.find_nearest_gold()
            if not self.target_treasure:
                print(f"[INFO] {self.getId()} found no available golds.")
                return

        target_x, target_y = self.target_treasure
        if (self.posX, self.posY) == (target_x, target_y):  # Already at the gold
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
        """Move the agent towards the depot to unload golds."""
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
            if self.find_nearest_gold():
                print(f"[INTERRUPT] {self.getId()} assigned new treasure while moving. Heading to collect.")
                self.target_treasure = self.find_nearest_gold()
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
        return f"agent gold {self.id} ({self.posX}, {self.posY})"

def gold_policy(gold_agent,gui):
    """Executes the gold collection policy for a gold agent."""
    print(f"[POLICY] Processing {gold_agent.getId()} at {gold_agent.getPos()}")

    # ✅ **Step 1: If at depot, unload & search for new golds**
    if (gold_agent.posX, gold_agent.posY) == gold_agent.env.posUnload:
        if gold_agent.gold > 0:
            print(f"[UNLOADING] {gold_agent.getId()} unloading at depot...")
            gold_agent.unload(gui)  # ✅ Unloads golds
            print(f"[UNLOADED] {gold_agent.getId()} is now empty and ready to collect more gold.")
        else:
            print(f"[INFO] {gold_agent.getId()} is at depot but backpack is empty.")

        # ✅ Move outside depot zone if no treasure is assigned
        if not gold_agent.find_nearest_gold():
            gold_agent.move_outside_depot_zone(radius=2)
            return  # Exit early if no gold is found

    # ✅ **Step 2: Check if there's gold at the agent's position & load it**
    current_treasure = gold_agent.env.grilleTres[gold_agent.posX][gold_agent.posY]
    if current_treasure and current_treasure.getType() == 1:
        available_space = gold_agent.backPack - gold_agent.gold
        if available_space > 0:
            amount_picked = min(available_space, current_treasure.getValue())
            gold_agent.load(gold_agent.env)
            print(f"[LOAD] {gold_agent.getId()} picked up {amount_picked} gold at ({gold_agent.posX}, {gold_agent.posY})")
            gold_agent.env.grilleTres[gold_agent.posX][gold_agent.posY] = None

    # ✅ **Step 3: Decide next action based on storage and treasure availability**
    if gold_agent.gold >= gold_agent.backPack:
        print(f"[UNLOAD] {gold_agent.getId()} backpack full. Moving to depot.")
        gold_agent.move_to_depot()

    elif gold_agent.gold > 0 and not gold_agent.find_nearest_gold():
        # ✅ **If there is gold in the backpack but no new treasure is available, unload it**
        print(f"[NO TREASURE] {gold_agent.getId()} has gold but no treasure found. Moving to depot to unload.")
        gold_agent.move_to_depot()

    elif not gold_agent.find_nearest_gold():
        # ✅ **Freeze if outside depot and no treasure is available**
        if not gold_agent.is_in_depot_zone(radius=2):
            print(f"[WAITING] {gold_agent.getId()} is outside the depot and no treasure is available. Waiting...")
            return  # Agent stays in place and waits
        else:
            print(f"[INFO] {gold_agent.getId()} is inside depot zone with no treasure. Moving outside.")
            gold_agent.move_outside_depot_zone(radius=2)

    else:
        # ✅ Move to the nearest gold if available
        gold_agent.target_treasure = gold_agent.find_nearest_gold()
        if gold_agent.target_treasure:
            print(f"[MOVE] {gold_agent.getId()} moving towards treasure at {gold_agent.target_treasure}")
            gold_agent.move_toward_target()