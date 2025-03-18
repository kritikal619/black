import pygame
import random
import sys

pygame.init()
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Blackjack Game")
clock = pygame.time.Clock()
FONT = pygame.font.SysFont("Arial", 20)
BIG_FONT = pygame.font.SysFont("Arial", 32)

# 색상 정의
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 128, 0)
GRAY = (200, 200, 200)
RED = (200, 0, 0)
BLUE = (0, 0, 200)

# 카드 관련 함수들
def create_deck():
    deck = []
    suits = ['Hearts', 'Diamonds', 'Clubs', 'Spades']
    ranks = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
    for suit in suits:
        for rank in ranks:
            deck.append((rank, suit))
    return deck

def shuffle_deck(deck):
    random.shuffle(deck)
    return deck

def card_value(card):
    rank, suit = card
    if rank in ['J', 'Q', 'K']:
        return 10
    elif rank == 'A':
        return 11
    else:
        return int(rank)

def calculate_score(hand):
    score = sum(card_value(card) for card in hand)
    aces = sum(1 for card in hand if card[0] == 'A')
    while score > 21 and aces:
        score -= 10
        aces -= 1
    return score

# 버튼 클래스
class Button:
    def __init__(self, rect, text, color=GRAY, text_color=BLACK):
        self.rect = pygame.Rect(rect)
        self.text = text
        self.color = color
        self.text_color = text_color

    def draw(self, surface):
        pygame.draw.rect(surface, self.color, self.rect)
        txt_surf = FONT.render(self.text, True, self.text_color)
        txt_rect = txt_surf.get_rect(center=self.rect.center)
        surface.blit(txt_surf, txt_rect)

    def is_clicked(self, pos):
        return self.rect.collidepoint(pos)

# 카드 그리기 함수 (카드: 사각형과 텍스트)
def draw_card(card, pos):
    rect = pygame.Rect(pos[0], pos[1], 60, 90)
    pygame.draw.rect(screen, WHITE, rect)
    pygame.draw.rect(screen, BLACK, rect, 2)
    card_text = f"{card[0]}{card[1][0]}"
    txt_surf = FONT.render(card_text, True, BLACK)
    txt_rect = txt_surf.get_rect(center=rect.center)
    screen.blit(txt_surf, txt_rect)

def draw_hand(hand, start_pos, hide_first=False):
    x, y = start_pos
    for i, card in enumerate(hand):
        if hide_first and i == 1:
            rect = pygame.Rect(x, y, 60, 90)
            pygame.draw.rect(screen, BLUE, rect)
            pygame.draw.rect(screen, BLACK, rect, 2)
            txt = FONT.render("?", True, WHITE)
            txt_rect = txt.get_rect(center=rect.center)
            screen.blit(txt, txt_rect)
        else:
            draw_card(card, (x, y))
        x += 70  # 카드 사이 간격

# 메인 게임 루프
def main():
    deck = shuffle_deck(create_deck())
    bankroll = 1000
    bet = 100  # 고정 베팅 금액 (필요시 수정 가능)
    player_hand = []
    dealer_hand = []
    game_state = "betting"  # 상태: betting, player_turn, dealer_turn, result
    message = ""
    player_doubled = False
    surrendered = False

    # 버튼 생성
    btn_hit = Button((50, 500, 100, 40), "Hit")
    btn_stand = Button((170, 500, 100, 40), "Stand")
    btn_double = Button((290, 500, 120, 40), "Double Down")
    btn_surrender = Button((430, 500, 120, 40), "Surrender")
    btn_new = Button((600, 500, 150, 40), "New Round")

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
                
            if event.type == pygame.MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()
                if game_state == "betting":
                    # 베팅 후 카드 배분
                    if len(deck) < 15:
                        deck = shuffle_deck(create_deck())
                    player_hand = [deck.pop(), deck.pop()]
                    dealer_hand = [deck.pop(), deck.pop()]
                    game_state = "player_turn"
                    message = "Your turn!"
                elif game_state == "player_turn":
                    if btn_hit.is_clicked(pos):
                        player_hand.append(deck.pop())
                        if calculate_score(player_hand) > 21:
                            message = "Bust! You lose."
                            game_state = "result"
                    elif btn_stand.is_clicked(pos):
                        game_state = "dealer_turn"
                    elif btn_double.is_clicked(pos):
                        if bankroll >= bet:
                            bankroll -= bet
                            bet *= 2
                            player_hand.append(deck.pop())
                            player_doubled = True
                            if calculate_score(player_hand) > 21:
                                message = "Bust after double down!"
                                game_state = "result"
                            else:
                                game_state = "dealer_turn"
                        else:
                            message = "Not enough bankroll to double down."
                    elif btn_surrender.is_clicked(pos):
                        surrendered = True
                        message = "You surrendered. Lose half your bet."
                        game_state = "result"
                elif game_state == "result":
                    if btn_new.is_clicked(pos):
                        deck = shuffle_deck(create_deck())
                        player_hand = []
                        dealer_hand = []
                        game_state = "betting"
                        message = ""
                        bet = 100

        # 딜러 턴 진행
        if game_state == "dealer_turn":
            while calculate_score(dealer_hand) < 17:
                dealer_hand.append(deck.pop())
                pygame.time.delay(500)
            game_state = "result"

        # 결과 판정
        if game_state == "result":
            player_score = calculate_score(player_hand)
            dealer_score = calculate_score(dealer_hand)
            if surrendered:
                result_text = "Surrendered: You lose half your bet."
            elif player_score > 21:
                result_text = "Bust! You lose."
            elif dealer_score > 21:
                result_text = "Dealer busts! You win."
                bankroll += bet * 2
            elif player_score > dealer_score:
                result_text = "You win!"
                bankroll += bet * 2
            elif player_score < dealer_score:
                result_text = "You lose!"
            else:
                result_text = "Push! Bet returned."
                bankroll += bet
            message = result_text

        # 화면 그리기
        screen.fill(GREEN)
        title = BIG_FONT.render("Blackjack", True, WHITE)
        screen.blit(title, (WIDTH//2 - title.get_width()//2, 10))
        bank_text = FONT.render(f"Bankroll: {bankroll}", True, WHITE)
        bet_text = FONT.render(f"Bet: {bet}", True, WHITE)
        screen.blit(bank_text, (50, 50))
        screen.blit(bet_text, (50, 80))
        state_text = FONT.render(message, True, RED)
        screen.blit(state_text, (50, 120))

        # 플레이어와 딜러의 카드 표시
        player_title = FONT.render("Player's Hand:", True, WHITE)
        screen.blit(player_title, (50, 150))
        draw_hand(player_hand, (50, 180))
        dealer_title = FONT.render("Dealer's Hand:", True, WHITE)
        screen.blit(dealer_title, (50, 300))
        if game_state == "player_turn":
            draw_hand(dealer_hand, (50, 330), hide_first=True)
        else:
            draw_hand(dealer_hand, (50, 330))

        # 버튼 표시
        if game_state == "player_turn":
            btn_hit.draw(screen)
            btn_stand.draw(screen)
            btn_double.draw(screen)
            btn_surrender.draw(screen)
        elif game_state == "result":
            btn_new.draw(screen)

        pygame.display.flip()
        clock.tick(30)

if __name__ == "__main__":
    main()
