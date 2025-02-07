
# version 2.1
import heapq
from MyAgent import MyAgent

class MyAgentChest(MyAgent):
    def __init__(self, id, initX, initY, env):
        super().__init__(id, initX, initY, env)
        self.target_chest = None  
        self.received_intentions = {}  
        self.intention_sent = False  
        self.rejected_chests = set()  
        self.failed_deviation_attempts = 0  
        self.myagentScore=0


    def getType(self):
        return 0  

    def open(self, gui):
        """Opens the chest if there is one at the agent's position."""
        if self.env.grilleTres[self.posX][self.posY] is not None:
            self.env.open(self, self.posX, self.posY)
            print(f"{self.getId()} opened a chest at ({self.posX}, {self.posY})")


            self.target_chest = None  # Reset target after opening
            self.intention_sent = False  # Allow new intentions
            self.failed_deviation_attempts = 0  # Reset deviation attempts
            self.myagentScore+=1


    def find_nearest_chest(self, assigned_chests):
        """Find the nearest unopened and unoccupied chest."""
        unopened_chests = [
            (x, y) for x in range(self.env.tailleX) for y in range(self.env.tailleY)
            if self.env.grilleTres[x][y] is not None  # There is a chest
            and not self.env.grilleTres[x][y].isOpen()  # It's not open
            and self.env.grilleAgent[x][y] is None  # ✅ **No agent is standing on it**
        ]
        
        available_chests = [chest for chest in unopened_chests if chest not in assigned_chests]

        if not available_chests:
            return None  # No available chests

        return min(available_chests, key=lambda c: abs(self.posX - c[0]) + abs(self.posY - c[1]))


    def share_intention(self, gui):
        """Shares the agent's intention (nearest chest and distance) with other agents."""
        if self.target_chest and not self.intention_sent:
            distance = abs(self.posX - self.target_chest[0]) + abs(self.posY - self.target_chest[1])
            message = f"INTENTION {self.target_chest[0]} {self.target_chest[1]} {distance}"
            
            for agent in self.env.agentSet.values():
                if isinstance(agent, MyAgentChest) and agent.getId() != self.getId():
                    self.send(agent.getId(), message)
                    print(f"[MESSAGE] {self.getId()} -> {agent.getId()}: {message}")
            
            self.intention_sent = True  

    def read_intentions(self, gui):
        """Reads messages from other agents to track their target chests and resolve conflicts."""
        while self.mailBox:
            sender, content = self.readMail()
            parts = content.split()
            if parts[0] == "INTENTION":
                x, y, distance = int(parts[1]), int(parts[2]), int(parts[3])
                self.received_intentions[sender] = (x, y, distance)
                print(f"[RECEIVED] {self.getId()} <- {sender}: Target Chest ({x}, {y}), Distance {distance}")
                gui.add_chat_message(f"MSG from {sender} -> {self.getId()}: Chest at ({x}, {y}), Distance {distance}")





    def resolve_conflicts(self):
        """Ensures that only the closest agent gets a given chest."""
        if self.target_chest is None:
            return  

        target_x, target_y = self.target_chest
        my_distance = abs(self.posX - target_x) + abs(self.posY - target_y)

        conflicts = [(sender, data[2]) for sender, data in self.received_intentions.items() if data[:2] == (target_x, target_y)]

        if conflicts:
            conflicts.append((self.getId(), my_distance))
            conflicts.sort(key=lambda x: x[1])  

            winner = conflicts[0][0]  

            if winner != self.getId():
                print(f"[CONFLICT] {self.getId()} lost target {self.target_chest} to {winner}. Picking a new target.")
                self.rejected_chests.add(self.target_chest)

                new_target = self.find_nearest_chest(self.rejected_chests)

                if new_target:
                    self.target_chest = new_target
                    self.intention_sent = False  
                else:
                    print(f"[INFO] {self.getId()} has no alternative targets. Waiting...")
                    self.target_chest = None  
    def is_in_depot_zone(self, radius=2):
        """Check if the agent is within the depot zone based on a radius."""
        depot_x, depot_y = self.env.posUnload
        return abs(self.posX - depot_x) <= radius and abs(self.posY - depot_y) <= radius






    def find_nearest_blank_cell(self):
        """Finds the nearest blank cell (without treasure or unlocked chests) for the agent to wait in when idle."""
        neighbors = [
            (-1, 0), (1, 0), (0, -1), (0, 1),  # Up, Down, Left, Right
            (-1, -1), (-1, 1), (1, -1), (1, 1)  # Diagonal moves
        ]

        for dx, dy in neighbors:
            new_x, new_y = self.posX + dx, self.posY + dy
            if 0 <= new_x < self.env.tailleX and 0 <= new_y < self.env.tailleY:
                # ✅ Check if the cell is completely empty (no treasure)
                treasure = self.env.grilleTres[new_x][new_y]
                if treasure is None:
                    return new_x, new_y  # ✅ Completely blank cell
                elif treasure and not treasure.isOpen():
                    continue  # Skip unlocked chests
        return None  # No blank cell found nearby


    def find_nearest_blank_cell_outside_depot(self):
        """Find the nearest blank cell outside the depot zone that does not contain unlocked chests."""
        for x in range(self.env.tailleX):
            for y in range(self.env.tailleY):
                if self.env.grilleTres[x][y] is None and not self.is_in_depot_zone():
                    return x, y
                elif self.env.grilleTres[x][y] and not self.env.grilleTres[x][y].isOpen():
                    continue  # Avoid unlocked chests
        return None


    def move_toward_target(self, gui):
        """Moves the agent towards the assigned chest or out of the depot zone when idle."""
        self.read_intentions(gui)
        self.resolve_conflicts()

        if not self.target_chest:
            print(f"[IDLE] {self.getId()} has no assigned task.")

            # ✅ Check if inside the depot zone
            if self.is_in_depot_zone():
                print(f"[MOVE] {self.getId()} is in the depot zone and will move out.")
                blank_cell = self.find_nearest_blank_cell_outside_depot()
                if blank_cell:
                    self.move(self.posX, self.posY, blank_cell[0], blank_cell[1])
                    gui.add_chat_message(f"{self.getId()} moved out of depot to {blank_cell}.")
                else:
                    print(f"[WAITING] {self.getId()} found no blank cell outside depot. Staying put.")
                return

            # ✅ If outside depot and in a blank cell, wait
            treasure = self.env.grilleTres[self.posX][self.posY]
            if treasure is None:
                print(f"[WAITING] {self.getId()} is idle at a blank cell ({self.posX}, {self.posY}).")
                gui.add_chat_message(f"{self.getId()} is waiting at ({self.posX}, {self.posY}).")
                return
            elif treasure and not treasure.isOpen():
                print(f"[MOVE] {self.getId()} is in an unlocked cell. Moving to a blank cell.")
                blank_cell = self.find_nearest_blank_cell()
                if blank_cell:
                    self.move(self.posX, self.posY, blank_cell[0], blank_cell[1])
                    gui.add_chat_message(f"{self.getId()} moved from unlocked cell to {blank_cell}.")
                else:
                    print(f"[WAITING] {self.getId()} couldn't find a blank cell. Staying put.")
                return

            # ✅ Move to a blank cell if not in one
            blank_cell = self.find_nearest_blank_cell()
            if blank_cell:
                print(f"[MOVE] {self.getId()} moving to idle at blank cell {blank_cell}.")
                self.move(self.posX, self.posY, blank_cell[0], blank_cell[1])
                gui.add_chat_message(f"{self.getId()} moved to idle at {blank_cell}.")
            else:
                print(f"[WAITING] {self.getId()} couldn't find a blank cell. Staying put.")
                gui.add_chat_message(f"{self.getId()} is waiting at ({self.posX}, {self.posY}).")
            return

        # ✅ Continue moving towards the chest if assigned
        target_x, target_y = self.target_chest
        path = self.a_star_find_path((self.posX, self.posY), (target_x, target_y))

        if not path:
            print(f"[ERROR] {self.getId()} could not find a path to ({target_x}, {target_y}). Switching target.")
            self.target_chest = self.find_nearest_chest({})
            self.intention_sent = False
            return

        next_x, next_y = path.pop(0)
        if self.env.grilleAgent[next_x][next_y] is None:
            self.move(self.posX, self.posY, next_x, next_y)

        if (self.posX, self.posY) == (target_x, target_y):
            self.open(gui)


    def a_star_find_path(self, start, goal):
        """Finds the shortest path avoiding obstacles using A*."""
        def heuristic(a, b):
            return abs(a[0] - b[0]) + abs(a[1] - b[1])

        neighbors = [
            (-1, 0), (1, 0), (0, -1), (0, 1),  
            (-1, -1), (-1, 1), (1, -1), (1, 1)  
        ]

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

            for dx, dy in neighbors:
                neighbor = (current[0] + dx, current[1] + dy)

                if neighbor[0] < 0 or neighbor[0] >= self.env.tailleX or neighbor[1] < 0 or neighbor[1] >= self.env.tailleY:
                    continue  # Ignore out-of-bounds positions

                if self.env.grilleAgent[neighbor[0]][neighbor[1]] is not None and neighbor != goal:
                    continue  # Ignore occupied cells unless it's the goal

                # **Fix:** Ensure `g_score[neighbor]` is initialized before using it
                tentative_g_score = g_score[current] + (1.414 if dx != 0 and dy != 0 else 1)

                if neighbor not in g_score or tentative_g_score < g_score.get(neighbor, float('inf')):
                    came_from[neighbor] = current
                    g_score[neighbor] = tentative_g_score
                    f_score[neighbor] = tentative_g_score + heuristic(neighbor, goal)
                    heapq.heappush(open_set, (f_score[neighbor], neighbor))

        return []  # No path found


    def __str__(self):
        return f"Agent Chest {self.id} ({self.posX}, {self.posY})"


### 🔥 **Policy Function for `main.py`**
def chest_policy(opener, gui):  # ✅ Accept gui as a parameter
    opener.move_toward_target(gui)  # ✅ Pass gui when calling move_toward_target
    """Executes the chest opening policy for a single agent."""
    if opener.target_chest is None:  
        opener.target_chest = opener.find_nearest_chest(set())  
    opener.share_intention(gui)  
    opener.read_intentions(gui) 
    opener.resolve_conflicts()  
