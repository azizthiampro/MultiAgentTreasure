from Environment import Environment
from MyAgentGold import MyAgentGold, gold_policy
from MyAgentChest import MyAgentChest, chest_policy
from MyAgentStones import MyAgentStones, stone_policy
from Treasure import Treasure
import random
from GameGUI import GameGUI

horizon = 100  # Number of timesteps

def loadFileConfig(nameFile):
    """Loads the initial environment setup from the configuration file."""
    with open(nameFile) as file:
        lines = file.readlines()
    tailleEnv = list(map(int, lines[1].split()))
    zoneDepot = tuple(map(int, lines[3].split()))

    env = Environment(*tailleEnv, zoneDepot)
    dictAgent = {}

    for line in lines[4:]:
        parts = line.strip().split(":")
        if parts[0] == "tres":  # Treasure
            if parts[1] == "or":
                env.addTreasure(Treasure(1, int(parts[4])), int(parts[2]), int(parts[3]))
            elif parts[1] == "pierres":
                env.addTreasure(Treasure(2, int(parts[4])), int(parts[2]), int(parts[3]))
        elif parts[0] == "AG":  # Agent
            id = f"agent{len(dictAgent)}"
            if parts[1] == "or":
                agent = MyAgentGold(id, int(parts[2]), int(parts[3]), env, int(parts[4]))
            elif parts[1] == "pierres":
                agent = MyAgentStones(id, int(parts[2]), int(parts[3]), env, int(parts[4]))
            elif parts[1] == "ouvr":
                agent = MyAgentChest(id, int(parts[2]), int(parts[3]), env)
            dictAgent[id] = agent
            env.addAgent(agent)

    env.addAgentSet(dictAgent)
    return env, dictAgent

def count_treasures(env):
    """Counts the number of gold and stone treasures in the environment."""
    gold_count = 0
    stone_count = 0
    for x in range(env.tailleX):
        for y in range(env.tailleY):
            if env.grilleTres[x][y] is not None:
                if env.grilleTres[x][y].getType() == 1:
                    gold_count += 1
                elif env.grilleTres[x][y].getType() == 2:
                    stone_count += 1
    return gold_count, stone_count

def main():
    def replay_game():
        main()

    # Load environment and agents from configuration file
    env, lAg = loadFileConfig("env1.txt")
    gui = GameGUI(env, replay_callback=replay_game)  # Pass replay function to GUI

    for t in range(horizon):
        openers = [agent for agent in lAg.values() if isinstance(agent, MyAgentChest)]
        gold_agents = [agent for agent in lAg.values() if isinstance(agent, MyAgentGold)]
        stone_agents = [agent for agent in lAg.values() if isinstance(agent, MyAgentStones)]

        # Generate new treasures every 10 steps
        if t % 7 == 0:
            num_new_treasures = random.randint(0, 5)
            env.gen_new_treasures(num_new_treasures, 7)

        # Run agent policies
        for opener in openers:
            chest_policy(opener, gui)
        for gold_agent in gold_agents:
            gold_policy(gold_agent)
        for stone_agent in stone_agents:
            stone_policy(stone_agent)

        gui.update_display()

    # Clear chat log before displaying final results
    gui.chat_log = []

    # Display Final Results in the Terminal
    print("\n******** FINAL RESULTS ********")
    print(f"Total Score: {env.getScore()}")

    print("\nDeposits by Each Picker:")
    for agent in lAg.values():
        if isinstance(agent, (MyAgentGold, MyAgentStones)):
            print(f"{agent.getId()}: {agent.myagentScore} units deposited")

    print("\nChests Opened by Each Opener:")
    for agent in lAg.values():
        if isinstance(agent, MyAgentChest):
            print(f"{agent.getId()}: {agent.myagentScore} chests opened.")

    # Keep GUI open with Replay button
    gui.run_gui()

if __name__ == "__main__":
    main()
