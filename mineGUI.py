import kivy
kivy.require('1.11.1')

from kivy.app import App
from kivy.uix.widget import Widget
from kivy.properties import NumericProperty, ReferenceListProperty
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.gridlayout import GridLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.button import Button
from kivy.uix.togglebutton import ToggleButton
from kivy.uix.popup import Popup
import numpy as np
from functools import partial
import time
import quantum_functions as qf
from kivy.uix.image import Image 
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.lang import Builder
import random as rd

class interface(FloatLayout):
    def __init__(self, **kwargs):
        super(interface, self).__init__(**kwargs)
        
        
        #Initialize quantum state
        self.nQubits = 9
        self.excluded_bits = set(rd.sample(set(list(range(9))), k = 4)) #In entangled mode
        self.percentMines = 0.5
        self.nGates = 0
        self.completed = 0
        self.health = 1000
        self.trialsPerClick = 100
        self.score = 0
        
        self.lastRound = 0
        
        self.modeToggle = 0 #0 = deterministic, 1 = entangled
        self.currentMeasurement = "Sz"  
        
        self.qs = qf.QState(self.nQubits, 1, self.nQubits)
        self.qs = self.newState()
        
        #Create minesweeper board
        self.gameBoard = board(self.nQubits)
        self.gameBoard.size_hint = (.75,0.8)
        self.gameBoard.pos_hint={'x':0, 'y':0.2}
        self.add_widget(self.gameBoard)
        
        #Interface buttons
        enter = Button(text = "Enter", size_hint = (0.33,0.15),  pos_hint={'x':0, 'y':0})
        self.add_widget(enter)
        enter.bind(on_press = self.pressEnter)
        
        newGame = Button(text = "New Game", size_hint = (0.33,0.15), pos_hint={'x':0.66, 'y':0})
        self.add_widget(newGame)
        newGame.bind(on_press = self.startNewGame)
        
        modeButton = ToggleButton(text='Deterministic', size_hint = (0.15,0.15), pos_hint={'x':0.34, 'y':0})
        self.add_widget(modeButton)
        modeButton.bind(on_press = self.updateMode) 
        
        #Interface text displays
        self.infoBox = Label(text = "Select 1 qubit to measure in Sz, or multiple to measure parity",size_hint = (0.25,0.4), pos_hint={'x':.75, 'y':0.4})
        self.infoBox.text_size = self.infoBox.size
        self.add_widget(self.infoBox)
        
        self.scoreBox = Label(text = 'Score: 0', size_hint = (0.25, 0.1), pos_hint = {'x':0.75, 'y':0.9})
        self.add_widget(self.scoreBox)
        
        self.healthBox = Label(text = 'Trials: {}\nTrials per click: {}'.format(self.health, self.trialsPerClick),size_hint = (0.25, 0.1), pos_hint={'x':.75, 'y':.8})
        self.add_widget(self.healthBox)
        
        self.resultBox = Label(text = "Measurement result: ",size_hint = (0.25,0.15), pos_hint={'x':.75, 'y':0.25})
        self.resultBox.text_size = self.resultBox.size
        self.add_widget(self.resultBox)
        
        self.gameplayBox = Label(size_hint = (0.33,0.15), pos_hint={'x':0.66, 'y':0})
        
    def updateMode(instance, button):
        instance.modeToggle = (instance.modeToggle + 1)%2
        if instance.modeToggle == 0:
            button.text = "Deterministic"
        else:
            button.text = "Entangled"
        instance.startNewGame(button)
        
        
    def pressEnter(instance, button):
        status = instance.gameBoard.clickStatus
        instance.gameBoard.reset()
        
        selected_bits = [i for (i,x) in enumerate(status) if x==1]
        totalClicked = sum(status)
        
        instance.infoBox.text = "Select 1 qubit to measure in Sz, or multiple to measure parity"
        if totalClicked == 0:
            instance.resultBox.text = "Please select at least one qubit!"
        else:
            if instance.lastRound == 1:
                instance.runLastRound(totalClicked, selected_bits)
                return
            instance.health = instance.health - instance.trialsPerClick
            if instance.health < 0:
                instance.health = 0
            instance.updateTextBoxes()
            
            if instance.health == 0:
                instance.lastRound = 1
                instance.finalMeas = np.random.randint(2) #0 for Sz and 1 for parity
                if instance.finalMeas == 0:
                    instance.infoBox.text = "Last attempt! You must make at least one Sz measurement!"
                if instance.finalMeas == 1:
                    instance.infoBox.text = "Last attempt! You must make a parity measurement."
                
            t1 = time.time()
            if totalClicked == 1:
                result = instance.qs.measureZ(selected_bits, instance.trialsPerClick)
                t2 = time.time()
            else:
                result = instance.qs.measureParity(selected_bits, instance.trialsPerClick)
                t2 = time.time()
            print("Measurement time:{}".format(t2 - t1))
            instance.resultBox.text = "Result: \n" + str(result)
                    
            #Reset        
            instance.qs.makeRandomState(0)
            
    def runLastRound(instance,totalClicked, selected_bits):

        if instance.finalMeas == 0:
            result = instance.qs.measureZ(selected_bits, 1)
            for res in result:
                instance.resultBox.text = "Result: \n" + str(res)
                
                mineFlag = res == '0'*totalClicked
                if mineFlag == 1:
                    instance.infoBox.text = "Congratulations. You move on to the next round!"
                    instance.completed = instance.completed + 1
                    instance.score = instance.score + totalClicked
                elif mineFlag == 0:
                    instance.infoBox.text = "BOOM! You lose!"
                    instance.completed = 0
                    instance.reportScore(0)
                    instance.score = 0
                    
        if instance.finalMeas == 1:
            result = instance.qs.measureParity(selected_bits, 1)
            
            for res in result:
                instance.resultBox.text = "Result: \n" + str(res)
                
                mineFlag = res == '0'
                if mineFlag == 1:
                    instance.infoBox.text = "Well done! You move on to the next round!"
                    instance.completed = instance.completed + 1
                    instance.score = instance.score + totalClicked - 1
                elif mineFlag == 0:
                    instance.infoBox.text = "BOOM! You lose!"
                    instance.completed = 0
                    instance.reportScore(0)
                    instance.score = 0

        instance.qs = instance.newState()
        instance.health = 1000 - 200 * instance.completed
        instance.trialsPerClick = max(100 - 20 * instance.completed,10)
        instance.updateTextBoxes()
        instance.lastRound = 0
        if instance.health == 0:
            instance.reportScore(1)
        return
          
    def startNewGame(instance, button):
        instance.infoBox.text = "Select 1 qubit to measure in Sz, or multiple to measure parity"
        instance.completed = 0
        instance.health = 1000
        instance.trialPerClick = 100
        instance.score = 0
        instance.newState()
        instance.updateTextBoxes()
        
    def newState(instance):
        if instance.modeToggle == 0:
            excluded_bits = {0,1,2,3,4,5,6,7,8}
        else:
            excluded_bits = set(rd.sample(set(list(range(9))), k = max(4 - instance.completed * 2, 0)))
        active_bits = 9 - len(excluded_bits)
        nGates = 5 * active_bits
        instance.qs.setAndChooseGates(nGates, excluded_bits, instance.percentMines)
        instance.qs.makeRandomState(1)
        return instance.qs
    
    def updateTextBoxes(instance):
        instance.scoreBox.text = "Score: {}".format(instance.score)
        instance.healthBox.text = 'Trials: {}\nTrials per click: {}'.format(instance.health, instance.trialsPerClick)
    
    def reportScore(instance, bEnd):
        if bEnd:
            popup = Popup(title = 'Game over', content = Label(text = 'Congratulations! Your score is {}'.format(instance.score)), size_hint=(0.3,0.3))
        else:
            popup = Popup(title = 'Game over', content = Label(text = 'Good try. Your score is {}'.format(instance.score)), size_hint=(0.3,0.3))    
        popup.open()
        instance.startNewGame('')

class board(GridLayout):
    
    def __init__(self,nQubits, **kwargs):
        super(board, self).__init__(**kwargs)
        
        self.cols = int(np.sqrt(nQubits))
        self.rows = int(np.sqrt(nQubits))
        
        self.buttons = [[],[],[],[],[]] #Holds button objects
        
        self.clickStatus = []
        for i in range(self.cols*self.rows):
            self.clickStatus.append(0)
        
        for i in range(self.rows):
            for j in range(self.cols):
                self.buttons[i].append(ToggleButton(text='{}'.format(i*self.rows+j)))
                self.add_widget(self.buttons[i][j])
                self.buttons[i][j].bind(on_press = partial(self.pressUpdate,i,j))     
                
    def pressUpdate(instance, row, col,butt):
        bState = 0
        if butt.state == 'down': bState = 1
        instance.clickStatus[row*instance.rows + col] = bState
        # print(instance.clickStatus)
    
    def reset(instance):
        instance.clickStatus = []
        for i in range(instance.cols*instance.rows):
            instance.clickStatus.append(0)
        for i in range(instance.rows):
            for j in range(instance.cols):
                instance.buttons[i][j].state = "normal"
                       





Builder.load_string("""
<StartPageScreen>:
    FloatLayout:
        Image:
            source: 'logo1.jpg'
            size:self.texture_size
        Button:
            text: 'Go to rules'
            on_press:
                root.manager.transition.direction = 'left'
                root.manager.current = 'rules'
            size_hint:1,0.2
            pos_hint:{'x':0,'y':0.0}

<RulesScreen>:
    FloatLayout:
        Button:
            text: 'Back to StartPage'
            on_press:
                root.manager.transition.direction = 'right'
                root.manager.current = 'startpage'
            size_hint:0.5,0.2
            pos_hint:{'x':0,'y':0.0}
        Button:
            text: 'Start Game!'
            on_press:
                root.manager.transition.direction = 'left'
                root.manager.current = 'game'
            size_hint:0.5,0.2
            pos_hint:{'x':0.5,'y':0.0}
        Label:
            text: "The game board is a 3 x 3 grid, representing a 9 qubit pure, but possibly highly entangled, quantum state.\\n There are 4 qubits that are deterministically set in the first round.\\n Mines are represented by the computational basis state 1, while non mines are represented by state 0. \\n The game is played in several rounds with two stages.\\n At the start of each round, you have a ten tomography measurments you can make to get information on the state.\\n If you select a single qubit you will measure its Sz component. If you select multiple qubits you will measure their total parity.\\n\\n Once you have used all your tomography trials, you need to make a projective measurement!\\nYou will have to measure either parity or spin-z of a collection of qubits (meaning one measurement can affect the next ones!). If you measure a 1, you lose!\\nSpin measurements are done sequentially from the lowest to highest selected bit.\\nParity measurements give you the total parity of all the selected qubits.\\nThe more qubits you include in your measurement, the higher your score if you win the round! \\nNote that in subsequent rounds, the number of measurements in the tomography stage is reduced, and the number of deterministic bits is reduced as well."
            text_size: self.size
            valign: 'top'
            size_hint:0.9,0.8
            pos_hint:{'x':0,'y':0.2}  
""")
       
       
class StartPageScreen(Screen,Image):
    pass

class RulesScreen(Screen):
    pass
    
class gameScreen(Screen):
   
    def __init__(self, **kwargs):
        super(gameScreen, self).__init__(**kwargs)
        self.add_widget(interface())
        
 

class TitleApp(App):
    def build(self):
        # Create the screen manager
        sm = ScreenManager()
        sm.add_widget(StartPageScreen(name='startpage'))
        sm.add_widget(RulesScreen(name='rules'))
        sm.add_widget(gameScreen(name='game')) 
        return sm

class MineApp(App):
    
    def build(self):
        self.gameBoard = interface()
        return self.gameBoard
    
if __name__ == '__main__':
    TitleApp().run()
 #   MineApp().run()

