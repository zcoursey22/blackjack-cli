import os
import sys
import random
import time
import shelve
from getch import getch
from colorama import Fore, Back, Style
import math

# Dealer will stand on all 17s
# 2:1 payout for blackjack

# TODO
# Add time delay to drawing
# Animate card flip
# Improve selction/input with library
# Rework UX of exiting
# Split
# Surrender
# Insurance
# Settings menu for changing rules, etc.

CARD_BACK_COLOR = Back.GREEN
TYPEWRITE_EFFECT = True
TYPEWRITE_MIN_SPEED = 0.01
TYPEWRITE_SPEED = 15


def typewrite(s, end='\n'):
    if TYPEWRITE_EFFECT:
        n = len(s)
        for c in s:
            time.sleep(min(TYPEWRITE_MIN_SPEED,
                           math.log(n) / n / TYPEWRITE_SPEED))
            print(c, end='', flush=True)
        print(end, end='')
    else:
        print(s, end=end)


class Suit:
    def __init__(self, name, color, symbol):
        self.name = name
        self.color = color
        self.symbol = symbol


class Card:
    def __init__(self, rank, suit):
        self.rank = rank
        self.suit = suit
        try:
            self.value = int(rank)
        except:
            self.value = self.get_value()

    def get_value(self):
        if self.rank == 'A':
            return 11
        return 10


class Deck:
    def __init__(self):
        suits = [
            Suit('Heart', Fore.RED, '♥'),
            Suit('Diamond', Fore.RED, '♦'),
            Suit('Club', Fore.BLACK, '♣'),
            Suit('Spade', Fore.BLACK, '♠')
        ]
        self.suits = suits
        self.cards = [Card(rank, suit)
                      for rank in ['A', 2, 3, 4, 5, 6, 7, 8, 9, 10, 'J', 'Q', 'K'] for suit in suits]
        self.used_cards = []
        self.shuffle()

    def shuffle(self):
        self.cards += self.used_cards
        random.shuffle(self.cards)
        self.used_cards = []

    def draw_card(self):
        card = self.cards.pop()
        return card


class Dealer:
    hand = []

    def draw(self, deck, init=False):
        if not init:
            self.hand.append(deck.draw_card())
        else:
            self.hand = []
            for __ in range(2):
                self.hand.append(deck.draw_card())
        if self.get_hand_sum() > 21:
            for i in range(len(self.hand)):
                if self.hand[i].rank == 'A':
                    self.hand[i].value = 1
                    if self.get_hand_sum() <= 21:
                        return

    def get_hand_sum(self):
        return sum([card.value for card in self.hand])

    def get_soft_sum(self, for_print=False, win=False):
        has_hard_ace = True if len(
            [card for card in self.hand if card.value == 11]) > 0 else False
        hard_sum = self.get_hand_sum()
        if has_hard_ace:
            soft_sum = hard_sum - 10
            if for_print:
                if win:
                    return ''
                return f' (or {soft_sum})'
            return soft_sum
        else:
            if for_print:
                return ''
            return hard_sum

    def show(self, init=False, win=False):
        if not init:
            print(' '.join([f'{card.suit.color}{Back.WHITE}{f"10 " if card.rank == 10 else f"{card.rank}  "}{Style.RESET_ALL}' for card in self.hand]
                           ))
            print(' '.join([f'{card.suit.color}{Back.WHITE} {card.suit.symbol} {Style.RESET_ALL}' for card in self.hand]
                           ) + f' = {self.get_hand_sum()}{self.get_soft_sum(True, win)}')
            print(' '.join([f'{card.suit.color}{Back.WHITE}{f" 10" if card.rank == 10 else f"  {card.rank}"}{Style.RESET_ALL}' for card in self.hand]
                           ))
            return
        card = self.hand[0]
        top_row = f"10 " if card.rank == 10 else f"{card.rank}  "
        bottom_row = f" 10" if card.rank == 10 else f"  {card.rank}"
        print(f'{card.suit.color}{Back.WHITE}{top_row}{Style.RESET_ALL} {Fore.BLACK}{CARD_BACK_COLOR}* *{Style.RESET_ALL}')
        print(f'{card.suit.color}{Back.WHITE} {card.suit.symbol} {Style.RESET_ALL} {Fore.BLACK}{CARD_BACK_COLOR} * {Style.RESET_ALL} = {card.value}')
        print(f'{card.suit.color}{Back.WHITE}{bottom_row}{Style.RESET_ALL} {Fore.BLACK}{CARD_BACK_COLOR}* *{Style.RESET_ALL}')

    def hasBlackjack(self):
        return self.get_hand_sum() == 21


class Player:
    hand = []
    bet = 0

    def __init__(self):
        with shelve.open('data') as db:
            try:
                self.money = db['money']
                self.rounds_played = db['rounds_played']
            except:
                self.money = 250
                self.rounds_played = 0
            if self.money == 0:
                self.money = 250

    def get_hand_sum(self):
        return sum([card.value for card in self.hand])

    def get_soft_sum(self, for_print=False, win=False):
        has_hard_ace = True if len(
            [card for card in self.hand if card.value == 11]) > 0 else False
        hard_sum = self.get_hand_sum()
        if has_hard_ace:
            soft_sum = hard_sum - 10
            if for_print:
                if win:
                    return ''
                return f' (or {soft_sum})'
            return soft_sum
        else:
            if for_print:
                return ''
            return hard_sum

    def draw(self, deck, init=False):
        if not init:
            self.hand.append(deck.draw_card())
        else:
            self.hand = []
            for __ in range(2):
                self.hand.append(deck.draw_card())
        if self.get_hand_sum() > 21:
            for i in range(len(self.hand)):
                if self.hand[i].rank == 'A':
                    self.hand[i].value = 1
                    if self.get_hand_sum() <= 21:
                        return

    def show(self, win=False):
        print(' '.join(
            [f'{card.suit.color}{Back.WHITE}{f"10 " if card.rank == 10 else f"{card.rank}  "}{Style.RESET_ALL}' for card in self.hand]))
        print(' '.join(
            [f'{card.suit.color}{Back.WHITE} {card.suit.symbol} {Style.RESET_ALL}' for card in self.hand]) + f' = {self.get_hand_sum()}{self.get_soft_sum(True, win)}')
        print(' '.join(
            [f'{card.suit.color}{Back.WHITE}{f" 10" if card.rank == 10 else f"  {card.rank}"}{Style.RESET_ALL}' for card in self.hand]))

    def hasBlackjack(self):
        return self.get_hand_sum() == 21

    def make_bet(self):
        bet = 0
        while bet < 1 or bet > self.money:
            os.system('clear')
            typewrite(f'Money: ${self.money}')
            typewrite('\nEnter your bet:\n> $', end='')
            bet = input()
            try:
                bet = int(bet)
            except:
                bet = 0
        self.bet = bet
        self.money -= bet
        with shelve.open('data') as db:
            db['money'] = self.money


class Game:
    player = Player()
    dealer = Dealer()
    playing = True
    winner = False

    def start(self):
        while self.playing:
            self.play_game()
        if not self.winner:
            self.display()
        else:
            print()
        typewrite('Thanks for playing!')
        sys.exit()

    def play_game(self):
        self.deck = Deck()
        self.player.make_bet()
        self.dealer.draw(self.deck, True)
        self.player.draw(self.deck, True)
        while not self.winner and self.playing:
            self.play_round()
        if self.playing:
            self.winner = False
            self.play_game()

    def display(self, first=False, win=False, playing=False):
        os.system('clear')
        print()
        self.dealer.show(first, win)
        print()
        self.player.show(win)
        print('\n')
        if not win:
            typewrite(
                f'Money: ${self.player.money + (self.player.bet if playing else 0)}')
            typewrite(f'Current bet: ${self.player.bet}\n')

    def hit(self):
        self.player.draw(self.deck)
        if self.player.hasBlackjack():
            self.winner = self.player
        elif self.player.get_hand_sum() > 21:
            self.winner = self.dealer

    def stand(self):
        while self.dealer.get_hand_sum() < 17:
            self.dealer.draw(self.deck)
            if self.dealer.hasBlackjack():
                self.winner = self.dealer
        if self.dealer.get_hand_sum() > 21:
            self.winner = self.player
        if not self.winner:
            p_sum = self.player.get_hand_sum()
            d_sum = self.dealer.get_hand_sum()
            if p_sum == d_sum:
                self.winner = 'push'
            else:
                self.winner = self.player if p_sum > d_sum else self.dealer

    def double_down(self):
        self.player.money -= self.player.bet
        self.player.bet *= 2
        self.player.draw(self.deck)
        self.stand()

    def split(self):
        pass
        # TODO Implement

    def surrender(self):
        pass
        # TODO Implement

    def quit_game(self):
        self.playing = False

    def play(self):
        user_in = '0'
        while user_in not in ['1', '2', '3']:
            if self.dealer.hasBlackjack():
                self.winner = self.dealer
            if self.player.hasBlackjack():
                self.winner = self.player
            if self.winner:
                break
            self.display(True, playing=True)
            # typewrite(
            #     '1) hit\n2) stand\n3) double down\n4) split (disabled)\n5) surrender (disabled)\n\n> ', end='')
            typewrite(
                '1) hit\n2) stand\n3) double down\n\n> ', end='')
            user_in = getch()
        if user_in == '1':
            self.hit()
        elif user_in == '2':
            self.stand()
        elif user_in == '3':
            self.double_down()

    def play_round(self):
        self.play()
        if self.winner:
            self.display(False, True)
            if self.winner == self.player:
                self.player.money += self.player.bet * 2
                if self.winner.hasBlackjack():
                    self.player.money += self.player.bet
                    typewrite('You got blackjack!')
                elif self.dealer.get_hand_sum() > 21:
                    typewrite('Dealer busted!')
                typewrite('You win!')
            elif self.winner == self.dealer:
                if self.winner.hasBlackjack():
                    typewrite('Dealer has blackjack!')
                elif self.dealer.get_hand_sum() > 21:
                    typewrite('You busted!')
                typewrite('You lose!')
            else:
                self.player.money += self.player.bet
                typewrite('It\'s a push!')
            self.player.rounds_played += 1
            with shelve.open('data') as db:
                db['money'] = self.player.money
                db['rounds_played'] = self.player.rounds_played
            if self.player.money == 0:
                typewrite(f'\nOh no! You ran out of money!')
                self.quit_game()
            else:
                typewrite(f'\nMoney: ${self.player.money}')
                typewrite(
                    '\n\nPress any key to continue (or "q" to quit)\n\n> ', end='')
                user_in = getch()
                if user_in == 'q':
                    typewrite(user_in)
                    self.quit_game()


game = Game()
game.start()
