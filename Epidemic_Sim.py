import pygame
import time
import random

import numpy as np
import matplotlib.pyplot as plt

pygame.init()

black = (0,0,0)
white = (255, 255, 255)
green = (0, 255, 0)
red = (255, 0, 0)
blue = (0, 0, 255)
purple = (255, 0, 255)
yellow = (255, 255, 0)
gray = (100, 100, 100)

screen_x, screen_y = 700, 700
screen = pygame.display.set_mode((screen_x, screen_y), 0, 32)

healthy = (0, 255, 0)
sick_without_syntoms = (255, 0, 255)
sick_with_syntoms = (255, 0, 0)
immune = (255, 255, 0)
dead = (0,0,0)

class disease:
    def __init__(self, spread, affected, mortality, days_with_syntoms, days_without_syntoms):#add more if needed
        self.spread = spread#0-1
        self.affected = affected#0-1
        self.mortality = mortality#0-1
        self.days_with_syntoms = days_with_syntoms
        self.days_without_syntoms = days_without_syntoms

class precautions:
    def __init__(self, social_dist, quarantine, trav_rad, ppl_met):
        self.social_dist = social_dist#0-1
        self.quarantine = quarantine#0-1
        self.trav_rad = trav_rad#x>=1
        self.ppl_met = ppl_met#it is the amount of ppl each person encounters daily

class grid:
    def __init__(self, disease, precautions, board, x_pos, y_pos, width, height, line_color):
        self.disease = disease
        self.precautions = precautions
        self.board = board
        self.cubes = [[cube(i, j, x_pos, y_pos, height/len(self.board), self.board[i][j]) for j in range(len(self.board[0]))] for i in range(len(self.board))]
        self.x_pos = x_pos
        self.y_pos = y_pos
        self.width = width
        self.height = height
        self.cube_side_len = height/len(self.cubes)
        self.rows = len(self.cubes)
        self.colms = len(self.cubes[0])
        self.line_color = line_color
        self.selected = None
        self.day = 0

        self.days = [0]
        self.healthy = [0]
        self.sick_with_syntoms = [0]
        self.sick_without_syntoms = [0]
        self.immune = [0]
        self.dead = [0]
        for i in range(self.rows):
            for j in range(self.colms):
                if board[i][j] == healthy:
                    self.healthy[0] += 1
                elif board[i][j] == sick_without_syntoms:
                    self.sick_without_syntoms[0] += 1
                elif board[i][j] == sick_with_syntoms:
                    self.sick_with_syntoms[0] += 1
                elif board[i][j] == sick_without_syntoms:
                    self.immune[0] += 1
                else:
                    self.dead[0] += 1
        
    def mod(self, pos_xy):
        #acts as a modifyer that shifts a passed in value of (x, y) on the grid to be in the correct place on the entire pygame display
        return (pos_xy[0] + self.x_pos, pos_xy[1] + self.y_pos)
    def draw(self):
        
        #draw cubes
        for i in range(self.rows):
            for j in range(self.colms):
                self.cubes[i][j].draw()

        #draws hor lines
        for row_num in range(self.rows + 1):
            pos_1 = self.mod((0, int(row_num*self.cube_side_len)))
            pos_2 = self.mod((self.width, int(row_num*self.cube_side_len)))
            pygame.draw.line(screen, self.line_color, pos_1, pos_2)

        #draws vert lines
        for colm_num in range(self.colms + 1):
            pos_1 = self.mod((int(colm_num*self.cube_side_len), 0))
            pos_2 = self.mod((int(colm_num*self.cube_side_len), self.height))
            pygame.draw.line(screen, self.line_color, pos_1, pos_2)

    def select(self, row, colm):
        #reset all selected pieces
        for i in range(self.rows):
            for j in range(self.colms):
                self.cubes[i][j].selected = False

        #selectes piece cursor is over
        self.cubes[row][colm].selected = True
        self.selected = (row, colm)
    def disease_done(self):
        return self.sick_without_syntoms[-1] + self.sick_with_syntoms[-1] == 0

    def click(self, mouse_pos):
        X, Y = mouse_pos
        
        if self.x_pos < X < self.width + self.x_pos and self.y_pos < Y < self.height + self.y_pos:
            row = int((Y - self.y_pos)//self.cube_side_len)
            colm = int((X - self.x_pos)//self.cube_side_len)
            return (int(row), int(colm))
        else:
            return None
    def choose_color_cube(self, val):
        row, colm = self.selected
        self.cubes[row][colm].set_val(val)
    def next_day(self):

        #still have to incorperate:
        #affected variable in disease
        #social dist variable
        #healthcare capacity

        self.day += 1        
        new_board = [[None for a in range(self.colms)] for b in range(self.rows)]

        #main next day loop
        for i in range(self.rows):
            for j in range(self.colms):

                #skips if person is dead or immune
                if self.cubes[i][j].val == dead or self.cubes[i][j].val == immune:
                    new_board[i][j] = self.cubes[i][j].val
                    continue

                # checks for the cubes surrounding it
                surrounding = []
                #makes a list of all valid modifyer vals
                mod_ind = []
                for k in range(-self.precautions.trav_rad, self.precautions.trav_rad + 1):
                    for l in range(-self.precautions.trav_rad, self.precautions.trav_rad + 1):
                        if k == 0 and l == 0:
                            pass
                        else:
                            try:
                                if i+k < 0 or j+l < 0:#this is because -1 is still a valid index
                                    raise IndexError
                                else:
                                    mod_ind.append((k,l))
                            except IndexError:
                                pass
                #chooses modifyers randomly and adds them to the surrounding list
                for _ in range(self.precautions.ppl_met):
                    try:
                        m = random.choice((mod_ind))#may cause error
                        k = m[0]
                        l = m[1]
                        surrounding.append(self.cubes[i+k][j + l].val)
                        del mod_ind[mod_ind.index((k, l))]
                    except IndexError:
                        break
                    
                #check if healthy person should get infected#incorperate all other precautions
                if self.cubes[i][j].val == healthy:
                    n = random.uniform(0, 1)
                    q = True if n < self.precautions.quarantine else False
                    sick_surrounding = surrounding.count(sick_without_syntoms) if q else surrounding.count(sick_without_syntoms) + surrounding.count(sick_with_syntoms)
                    new_board[i][j] = healthy
                    for g in range(sick_surrounding):
                        if new_board[i][j] == sick_without_syntoms or new_board[i][j] == sick_with_syntoms:#avoids retesting if thing turns sick in the middle
                            break
                        else:
                            n = random.uniform(0, 1)
                            if n < self.disease.spread:
                                if self.disease.days_without_syntoms != 0:
                                    new_board[i][j] = sick_without_syntoms
                                else:
                                    new_board[i][j] = sick_with_syntoms
                                    
                #updates days sick for ppl
                elif self.cubes[i][j].val == sick_without_syntoms or self.cubes[i][j].val == sick_with_syntoms:
                    self.cubes[i][j].days_sick += 1
                    if self.cubes[i][j].days_sick > (self.disease.days_with_syntoms + self.disease.days_without_syntoms):
                        n = random.uniform(0, 1)
                        if n < self.disease.mortality:
                            new_board[i][j] = dead
                        else:
                            new_board[i][j] = immune
                    elif self.cubes[i][j].days_sick > self.disease.days_without_syntoms:
                        new_board[i][j] = sick_with_syntoms
                    else:
                        new_board[i][j] = self.cubes[i][j].val

                #raises an error if the new_state is none
                else:
                    print('there is a None value in the grid')
                    raise Exception
                
        #update the board
        for i in range(self.rows):
            for j in range(self.colms):
                if new_board[i][j] == None:
                    print(i, j)
                    raise Exception
                self.cubes[i][j].val = new_board[i][j]
        self.board = new_board

        #updates all data for the graph
        self.days.append(self.days[-1] + 1)
        self.healthy.append(0)
        self.sick_without_syntoms.append(0)
        self.sick_with_syntoms.append(0)
        self.immune.append(0)
        self.dead.append(0)
        for i in range(len(new_board)):
            for j in range(len(new_board[0])):
                if new_board[i][j] == healthy:
                    self.healthy[-1] += 1
                elif new_board[i][j] == sick_without_syntoms:
                    self.sick_without_syntoms[-1] += 1
                elif new_board[i][j] == sick_with_syntoms:
                    self.sick_with_syntoms[-1] += 1
                elif new_board[i][j] == immune:
                    self.immune[-1] += 1
                else:
                    self.dead[-1] += 1
                    
    def graph_data(self):

        #sets up all variables
        a = np.array(self.sick_without_syntoms)
        b = np.array(self.sick_with_syntoms)
        s = a + b
        s = s.tolist()

        a = np.array(self.dead)
        b = np.array(self.immune)
        r = a + b
        r = r.tolist()
        
        #makes legend
        plt.plot([],[],color = 'g',label = 'healthy')
        plt.plot([],[],color = 'k', label = 'removed')
        plt.plot([],[],color = 'r', label = 'infected')

        #makes and shows the graph
        #, colors = [sick_without_syntoms, sick_with_syntoms, healthy, immune, dead]
        c = ['r', 'g', 'k']
        plt.stackplot(self.days, s, self.healthy, r, colors = c)
        plt.legend()
        plt.show()
        
            
class cube:
    def __init__(self, row, colm, board_x, board_y, cube_side_len, val = None):#val will be the cube's color
        self.row = row
        self.colm = colm
        self.board_x = board_x
        self.board_y = board_y
        self.val = val
        self.cube_side_len = cube_side_len
        self.selected = False
        self.days_sick = 0
    def mod(self, pos_xy):
        #acts as a modifyer that shifts a passed in value of (x, y) on the grid to be in the correct place on the entire pygame display
        return (pos_xy[0] + self.x_pos, pos_xy[1] + self.y_pos)
    def draw(self):#val is color
        x = int(self.colm*self.cube_side_len)
        y = int(self.row*self.cube_side_len)
        m_x = int(self.board_x)#may be problem
        m_y = int(self.board_y)
        c = int(self.cube_side_len)

        #draws all cubes w/ color
        if self.val != None:
            pygame.draw.rect(screen, self.val, (x + m_x, y + m_y, c, c))

        #draws if selected
        if self.selected:
            pygame.draw.rect(screen, yellow, (x + m_x, y + m_y, c, c), 3)
    def set_val(self, val):
        self.val = val
        
b = [[ random.choice([healthy]) for a in range(101)] for b in range(101)]
b[50][50] = sick_without_syntoms

coronavirus = disease(0.2, 0.5, 0.03, 5, 1)
NH = precautions(0, 0.9, 1, 8)
g = grid(coronavirus, NH, b, 10, 10, 505, 505, blue)

#spread, affected, mortality, days_with_syntoms, days_without_syntoms
print('spread: ' + '0.2')
print('affected: ' + '0.5')
print('mortality: ' + '0.03')
print('days_with_syntoms: ' + '5')
print('days_without_syntoms: ' + '1') 

run = True
next_day = False
access = False
curDay = 0

while run:

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                curDay += 1
                print('Day:', curDay)
                g.next_day()
            if event.key == pygame.K_RIGHT:
                g.graph_data()
            '''for i in range(50):
                g.next_day()
            g.graph_data()'''
            '''if event.key == pygame.K_SPACE and access == True:
                next_day = True
            elif event.key == pygame.K_RIGHT:
                done = False
                while not done:
                    g.next_day()
                    if g.disease_done():
                        done = True
                g.graph_data()'''
        else:
            access = True
        
    if next_day:
        g.next_day()
        next_day = False
        access = False
        
    screen.fill(white)
    g.draw()
    pygame.display.update()

