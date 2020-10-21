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


pl_list = [Player(0, 14, COLOURS["RED"] ,"Player 1"),Player(0, 14, COLOURS["DARK BLUE"], "Player 2"),Player(0, 14, COLOURS["YELLOW"], "Player 3")]

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

other_card = None
board.sort_sets()

deal_player = None
per = 0

for i in board.properties:
    try:
        i.rent["0"] *= 100
    except:
        TypeError

def choose_deal_player(player_buttons, deal_player, current_player):
    for i in range(len(player_buttons)):
        if check_rect(player_buttons[i][0]):
            deal_player = pl_list[player_buttons[i][1]] if pl_list[player_buttons[i][1]] != current_player else deal_player
    return deal_player



while run:
    #to quit the file
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False








        win.fill((200, 200, 255))
        player_buttons = board.draw_background(pl_list, turn)

        # board.draw is in the board class and goes through all the propertys, player squares and buttons that need to be drawn
        for i in pl_list:
            i.draw(board)
            #this draws the players to the board, circling through them

        def reset_values():
            return 0, None, False


        #this is to do with the movement of the player
        if event.type == pygame.MOUSEBUTTONDOWN:
            deal_player = choose_deal_player(player_buttons, deal_player, pl_list[turn])
            x = board.check_for_button_click(action_taken)
            if x != None:


                if x == "ROLL DICE":
                    roll = dice_roll()
                    if roll[1]:
                        triple_checker +=1
                        double = True
                    if pl_list[turn] not in jail_list or double == True:
                        if not check_for_triple(triple_checker):
                            pl_list[turn].move(roll[0]) #when the player clicks roll dice it gets the number and then using the property_action function determines what property has been landed on
                            action_taken = pl_list[turn].property_action(board)
                            pl_list[turn].pass_go(roll[0])
                        else:
                            pl_list[turn].to_jail()
                            jail_list.append(pl_list[turn])
                            double = False
                            action_taken = 1
                    else:
                        action_taken = 1
                        jail_list.remove(pl_list[turn])



                elif x == "END TURN" and have_enough_money == True:
                    if double != True:
                        turn += 1
                        turn %= len(pl_list)
                        triple_checker = 0
                    other_card = None
                    double = False
                    deal_player = None
                    action_taken = 0 #this will reset it and then let the next player have their turn

                elif x == "MAKE DEAL":
                    if deal_player != None:
                        deal = Deal(pl_list[turn], deal_player, board)
                        action_taken = 3
                    else:
                        print("select a player")
                        #board.no_deal_player()

                elif x == "LOOK AT PROPERTYS":
                    action_taken = 11

                elif x == "PURCHASE":
                    if pl_list[turn].buy_property(board):
                        action_taken = 1

                elif x == "AUCTION":
                    auction = Auction(pl_list, board.properties[pl_list[turn].pos], board)
                    action_taken = 6

                elif x == "BID 1":
                    auction.add_amount(1)

                elif x == "BID 10":
                    auction.add_amount(10)

                elif x == "BID 100":
                    auction.add_amount(100)

                elif x == "BACK":
                    if action_taken == 5:
                        action_taken = 11
                    else:
                        action_taken = 1

                elif x == "+ HOUSE":
                    pl_list[turn].add_house(board, other_card)

                elif x == "- HOUSE":
                    pl_list[turn].remove_house(board, other_card)

                elif x == "MORTGAGE":
                    pl_list[turn].mortgage(board, other_card)

                elif x == "UNMORTGAGE":
                    pl_list[turn].unmortgage(board, other_card)

                elif x == "LEAVE":
                    auction.leave()

                elif x == "FINISHED":
                    action_taken = 4

                elif x == "ACCEPT":
                    action_taken = 1
                    deal.accept()
                    deal = None

                elif x == "REJECT":
                    action_taken = 1
                    deal = None

        if pl_list[turn].land_on_go_to_jail(board):
            jail_list.append(pl_list[turn])

        if action_taken == 3 or action_taken == 4:
            deal.draw()
            if action_taken == 3:
                if event.type == pygame.MOUSEBUTTONDOWN:
                    deal.add_propertys()




        elif action_taken == 6:
            auction.draw()
            if auction.check_finished():
                auction.players[0].buy_property(board, pl_list[turn], auction.amount)
                action_taken = 1


        elif action_taken == 7 or action_taken == 8  or action_taken == 9:
            action_time = time.time() if action_time == 0 else action_time
            if time.time() - action_time >= 3:
                if action_taken == 7:
                    have_enough_money, amount_required = pl_list[turn].pay_rent(board)
                elif action_taken == 8:
                    have_enough_money, amount_required = pl_list[turn].pay_tax(board)
                action_taken = 1
                action_time = 0



        elif action_taken == 11:
            if event.type == pygame.MOUSEBUTTONDOWN:
                if pl_list[turn].check_owned_property():
                    other_card = board.enlarge_property()
                    action_taken = 5

        board.utility_station_rent("BLACK")
        board.utility_station_rent("BOARD COLOUR")

        board.draw_onto_board(pl_list[turn].pos, action_taken, other_card)

        #if list(BROWN) == board.properties[pl_list[turn].pos].colour:
         #   print("skrrr skrrr")

        if have_enough_money == False and action_taken == 1:
            action_taken = pl_list[turn].property_action(board)
        if have_enough_money == False:
            print("do not have enough money")







            #this will ensure it cycles through all the players in the game if theres 2 players then it'll go 0,1,0,1...

        """if triple_checker == 3:
            jail_list.append(pl_list[turn])"""



        x,y = pygame.mouse.get_pos()
        render_text(board,font, pl_list[turn].username, COLOURS["BLACK"], (x,y))
        render_text(board, font, str(triple_checker), COLOURS["RED"], (x, y+30))
        render_text(board, font, str(double), COLOURS["RED"], (x-30, y+30))



            #this goes through every player in the game and draws them


        win.blit(board, (0, 0))

        pygame.display.update()
        clock.tick(60)





pygame.quit()