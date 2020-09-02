import pygame
from player import *
from board import Board
from constants import *
from game_rules import *
import time

pygame.init()

pygame.display.set_caption("Monopoly")
win = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
clock = pygame.time.Clock()


pl_list = [Player(0, 14, COLOURS["RED"], "Player 1")]#,Player(0, 14, COLOURS["DARK BLUE"], "Player 2")] #Player(0, 14, PINK, "Player 3")

board = Board(WINDOW_WIDTH, WINDOW_HEIGHT)#the Board is a class within board.py
#using the board class it then sets up all the properties needing to be made

auction_list = [] # this will be used to control who is allowed to bid during an auction
auction_turn = 0 #this will be used when the player selects auction so it can go through each player in the list
jail_list = []
run = True
turn = 0
#turn is used to go through each player to let them have there turn
triple_checker = 0
#this variable checks whether a player has rolled three doubles in a row
action_taken = 0
#this number will change depending on where the player lands it'll decide which buttons are drawn and what actions the player can take
double = False
#when a player rolls a double they can still purchase or pay rent to property so when it's complete this will validate whether there at the end of their turn

action_time = 0
#this will be used for timers or delays

board.sort_sets()


while run:
    #to quit the file
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False



        win.fill((200, 200, 255))
        board.draw(pl_list, pl_list[turn].pos, action_taken)
        # board.draw is in the board class and goes through all the propertys, player squares and buttons that need to be drawn
        for i in pl_list:
            i.draw(board)
            #this draws the players to the board, circling through them


        #this is to do with the movement of the player
        if event.type == pygame.MOUSEBUTTONDOWN:
            x = board.check_for_button_click(action_taken)
            if x != None:


                if x == "ROLL DICE":
                    x = dice_roll()
                    pl_list[turn].move(x[0]) #when the player clicks roll dice it gets the number and then using the property_action function determines what property has been landed on
                    if x[1] == True:
                        triple_checker+=1
                    action_taken = pl_list[turn].property_action(board)
                    pl_list[turn].pass_go(x[0])


                elif x == "END TURN":
                    turn += 1
                    action_taken = 0 #this will reset it and then let the next player have their turn

                elif x == "MAKE DEAL":
                    print("gvg")

                elif x == "LOOK AT PROPERTYS":
                    action_taken = 4

                elif x == "PURCHASE":
                    pl_list[turn].buy_property(board)
                    action_taken = 1

                elif x == "AUCTION":
                    auction_list = pl_list
                    action_taken = 5

                elif x == "BID 100":
                    pass
                elif x == "BID 10":
                    pass
                elif x == "BID 1":
                    pass






        if action_taken == 6 or action_taken == 7:
            action_time = time.time() if action_time == 0 else action_time
            if time.time() - action_time >= 3:
                if action_taken == 6:
                    pl_list[turn].pay_rent(board)
                elif action_taken == 7:
                    pl_list[turn].pay_tax(board)
                action_taken = 1
                action_time = 0

        #if list(BROWN) == board.properties[pl_list[turn].pos].colour:
         #   print("skrrr skrrr")







            #this will ensure it cycles through all the players in the game if theres 2 players then it'll go 0,1,0,1...

        """if triple_checker == 3:
            jail_list.append(pl_list[turn])"""






            #this goes through every player in the game and draws them

        board.enlarge_property()


        win.blit(board, (0, 0))
        """x,y = pygame.mouse.get_pos()
        print(x,y)"""

        pygame.display.update()
        clock.tick(60)

        turn %= len(pl_list)

pygame.quit()
