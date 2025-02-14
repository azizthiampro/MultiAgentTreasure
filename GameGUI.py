import pygame
from Environment import Environment
from MyAgentGold import MyAgentGold
from MyAgentChest import MyAgentChest
from MyAgentStones import MyAgentStones
from Treasure import Treasure

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (225, 38, 0)
GREEN = (0, 130, 0)
GRAY = (200, 200, 220)
YELLOW = (255, 225, 0)
BLUE = (125, 122, 120)

CELL_WIDTH = 55
CELL_HEIGHT = 50
CHAT_HEIGHT = 150  # Increased to accommodate final messages
FPS = 10

class GameGUI:
    def __init__(self, env, replay_callback=None):
        pygame.init()
        self.env = env
        self.replay_callback = replay_callback
        self.cell_width = CELL_WIDTH
        self.cell_height = CELL_HEIGHT
        self.width = env.tailleY * CELL_WIDTH
        self.height = env.tailleX * CELL_HEIGHT + CHAT_HEIGHT
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("Multi-Agent Treasure Hunt")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont(None, 18)
        self.chat_font = pygame.font.SysFont(None, 20)
        self.score_font = pygame.font.SysFont(None, 24, bold=True)
        self.floating_texts = []


        self.chat_log = []
        self.max_chat_lines = 8  # Increased to show more final results

        self.chest_image = pygame.image.load("assets/chest.png")
        self.chest_image = pygame.transform.scale(self.chest_image, (CELL_WIDTH, CELL_HEIGHT))
        self.gold_image = pygame.image.load("assets/gold.png")
        self.gold_image = pygame.transform.scale(self.gold_image, (CELL_WIDTH, CELL_HEIGHT))
        self.stones_image = pygame.image.load("assets/stones.png")
        self.stones_image = pygame.transform.scale(self.stones_image, (CELL_WIDTH, CELL_HEIGHT))

        self.lock_image = pygame.image.load("assets/lock.png")
        self.lock_image = pygame.transform.scale(self.lock_image, (CELL_WIDTH // 4, CELL_HEIGHT // 4))
        self.unlock_image = pygame.image.load("assets/unlock.png")
        self.unlock_image = pygame.transform.scale(self.unlock_image, (CELL_WIDTH // 4, CELL_HEIGHT // 4))

        # ✅ Replay Button
        self.replay_button = pygame.Rect(self.width - 120, self.height - CHAT_HEIGHT + 20, 100, 40)

    def add_chat_message(self, message):
        self.chat_log.append(message)
        if len(self.chat_log) > self.max_chat_lines:
            self.chat_log.pop(0)

    def draw_grid(self):
        for x in range(self.env.tailleX):
            for y in range(self.env.tailleY):
                rect = pygame.Rect(y * CELL_WIDTH, x * CELL_HEIGHT, CELL_WIDTH, CELL_HEIGHT)
                pygame.draw.rect(self.screen, GRAY, rect, 1)

    def draw_objects(self):
        depot_x, depot_y = self.env.posUnload
        depot_rect = pygame.Rect(depot_y * CELL_WIDTH, depot_x * CELL_HEIGHT, CELL_WIDTH, CELL_HEIGHT)
        pygame.draw.rect(self.screen, GREEN, depot_rect)

        score_text = self.score_font.render(f"{self.env.getScore()}", True, WHITE)
        text_rect = score_text.get_rect(center=depot_rect.center)
        self.screen.blit(score_text, text_rect)

        for x in range(self.env.tailleX):
            for y in range(self.env.tailleY):
                treasure = self.env.grilleTres[x][y]
                if treasure and treasure.getValue() > 0:
                    color = YELLOW if treasure.getType() == 1 else RED
                    treasure_rect = pygame.Rect(y * CELL_WIDTH, x * CELL_HEIGHT, CELL_WIDTH, CELL_HEIGHT)
                    pygame.draw.rect(self.screen, color, treasure_rect)
                    value_text = self.font.render(str(treasure.getValue()), True, BLACK)
                    text_rect = value_text.get_rect(center=treasure_rect.center)
                    self.screen.blit(value_text, text_rect)
                    icon_x = (y + 1) * CELL_WIDTH - CELL_WIDTH // 4 - 2
                    icon_y = (x + 1) * CELL_HEIGHT - CELL_HEIGHT // 4 - 2
                    if treasure.isOpen():
                        self.screen.blit(self.unlock_image, (icon_x, icon_y))
                    else:
                        self.screen.blit(self.lock_image, (icon_x, icon_y))

        for agent in self.env.agentSet.values():
            x, y = agent.getPos()
            center = (y * CELL_WIDTH, x * CELL_HEIGHT)
            if isinstance(agent, MyAgentChest):
                self.screen.blit(self.chest_image, center)
            elif isinstance(agent, MyAgentGold):
                self.screen.blit(self.gold_image, center)
            elif isinstance(agent, MyAgentStones):
                self.screen.blit(self.stones_image, center)
            if isinstance(agent, (MyAgentGold, MyAgentStones)):
                collected = agent.getTreasure()
                backpack_capacity = agent.backPack
                backpack_text = self.font.render(f"{collected}/{backpack_capacity}", True, BLACK)
                backpack_rect = backpack_text.get_rect(midbottom=(center[0] + CELL_WIDTH // 2, center[1]))
                self.screen.blit(backpack_text, backpack_rect)

    def draw_chat_window(self):
        chat_rect = pygame.Rect(0, self.height - CHAT_HEIGHT, self.width, CHAT_HEIGHT)
        pygame.draw.rect(self.screen, BLACK, chat_rect)

        title_text = self.chat_font.render("Game Log", True, WHITE)
        self.screen.blit(title_text, (10, self.height - CHAT_HEIGHT + 5))

        start_y = self.height - CHAT_HEIGHT + 30
        for i, message in enumerate(self.chat_log[-self.max_chat_lines:]):
            message_text = self.chat_font.render(message, True, WHITE)
            self.screen.blit(message_text, (10, start_y + i * 18))

       

    def show_game_over_popup(self):
        """Displays a Game Over popup with Replay and Quit buttons."""
        overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))  # Semi-transparent black overlay

        popup_width, popup_height = 350, 200
        popup_x = (self.width - popup_width) // 2
        popup_y = (self.height - popup_height) // 2
        popup_rect = pygame.Rect(popup_x, popup_y, popup_width, popup_height)

        pygame.draw.rect(overlay, WHITE, popup_rect, border_radius=12)
        pygame.draw.rect(overlay, BLUE, popup_rect, 5, border_radius=12)  # Blue border

        # Game Over Text
        game_over_text = self.score_font.render("GAME OVER - Details on Terminal ", True, BLACK)
        text_rect = game_over_text.get_rect(center=(self.width // 2, popup_y + 50))
        overlay.blit(game_over_text, text_rect)

        # Final Score Text
        final_score_text = self.chat_font.render(f"Final Score: {self.env.getScore()}", True, BLACK)
        score_rect = final_score_text.get_rect(center=(self.width // 2, popup_y + 90))
        overlay.blit(final_score_text, score_rect)

        # Replay Button
        self.replay_popup_button = pygame.Rect(popup_x + 30, popup_y + 130, 120, 40)
        pygame.draw.rect(overlay, GREEN, self.replay_popup_button, border_radius=8)
        replay_text = self.chat_font.render("REPLAY", True, WHITE)
        replay_text_rect = replay_text.get_rect(center=self.replay_popup_button.center)
        overlay.blit(replay_text, replay_text_rect)

        # Quit Button
        self.quit_popup_button = pygame.Rect(popup_x + 200, popup_y + 130, 120, 40)
        pygame.draw.rect(overlay, RED, self.quit_popup_button, border_radius=8)
        quit_text = self.chat_font.render("QUIT", True, WHITE)
        quit_text_rect = quit_text.get_rect(center=self.quit_popup_button.center)
        overlay.blit(quit_text, quit_text_rect)

        self.screen.blit(overlay, (0, 0))
        pygame.display.flip()



    def update_display(self):
        self.screen.fill(WHITE)
        self.draw_grid()
        self.draw_objects()
        self.draw_chat_window()

        # Update and draw floating texts
        for text in self.floating_texts[:]:
            text.update()
            text.draw(self.screen, self.font)
            if not text.is_alive():
                self.floating_texts.remove(text)

        pygame.display.flip()
        self.clock.tick(FPS)


    def run_gui(self):
        running = True
        game_over_displayed = False

        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if game_over_displayed:
                        # Handle Replay Button Click
                        if self.replay_popup_button.collidepoint(event.pos):
                            if self.replay_callback:
                                self.replay_callback()
                                return

                        # Handle Quit Button Click
                        if self.quit_popup_button.collidepoint(event.pos):
                            pygame.quit()
                            exit()

                    # Handle the old Replay button (if still needed)
                    elif self.replay_button.collidepoint(event.pos):
                        if self.replay_callback:
                            self.replay_callback()
                            return

            if not game_over_displayed:
                self.show_game_over_popup()
                game_over_displayed = True  # Ensure popup shows only once

    def add_floating_text(self, text, position):
        """Adds a floating text effect near the depot."""
        screen_x = position[1] * CELL_WIDTH
        screen_y = position[0] * CELL_HEIGHT
        self.floating_texts.append(FloatingText(f"+{text}", (screen_x + CELL_WIDTH // 2, screen_y)))

class FloatingText:
    def __init__(self, text, pos, color=BLACK, lifespan=60):
        self.text = text
        self.pos = list(pos)  # [x, y]
        self.color = color
        self.lifespan = lifespan  # Frames until disappearance
        self.age = 0

    def update(self):
        self.pos[1] -= 1  # Move upward
        self.age += 1

    def is_alive(self):
        return self.age < self.lifespan

    def draw(self, surface, font):
        if self.is_alive():
            text_surface = font.render(self.text, True, self.color)
            surface.blit(text_surface, self.pos)
