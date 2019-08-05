import algo
import img_proc
import serial
import numpy
import lcd
import os
import RPi.GPIO as GPIO
import time
import button

pre_state = None
ser_port = None
turn = 0
result = 0 # 0 draw, 1 PC, 2 HUMAN

def setup_serial_port():
    global ser_port
    for i in range(5):
        time.sleep(1)
        lcd.lcd_clear()
        lcd.lcd_string('trying port %s' % str(i),0)
        time.sleep(2)
        try:
            ser_port = serial.Serial('/dev/ttyACM%s' % str(i), 9600)
            lcd.lcd_clear()
            lcd.lcd_string('port %s up' % str(i),0)
            break
        except:
            lcd.lcd_clear()
            lcd.lcd_string('port %s empty' % str(i),0)
def initialize():
    global pre_state
    pre_state = '---------'
    lcd.setup()
    button.setup()
    lcd.lcd_string('Initializing ..',0)
    setup_serial_port()

def get_ack():
    lcd.lcd_clear()
    lcd.lcd_string('waiting for ack', 0)
    data = ser_port.readline()
    if len(data) > 0 and data == b'Done\n':
        lcd.lcd_clear()
        lcd.lcd_string('ack recieved', 0)
        return
        
def choose_start():
    lcd.lcd_clear()
    lcd.lcd_string('press the button',1)
    for i in range(7):
        lcd.lcd_string('to starts %s' % str(i),2)
        time.sleep(0.5)
        if button.check(): #change with button input
            turn = 1
            lcd.lcd_clear()
            lcd.lcd_string('You start (X)',  0)
            return
        time.sleep(0.5)
    lcd.lcd_clear()
    lcd.lcd_string('I start (O)', 0)
    

def play_turn():
    lcd.lcd_clear()
    lcd.lcd_string('looking ..', 0)
    os.system('raspistill -md 2 -o ./imgs/still.jpg')
    time.sleep(1)
    lcd.lcd_clear()
    lcd.lcd_string('thinking ..', 0)
    global pre_state
    state = img_proc.detect_board('./imgs/still.jpg')
    pre_state = state
    #TODO: check if current is valid from pre_state
    win, move = algo.nextMove(list(state),'O')
    square = 9 - move
    lcd.lcd_clear()
    lcd.lcd_string('moving ..', 0)
    ser_port.write(str.encode(str(square)))
    get_ack()
    lcd.lcd_clear()
    lcd.lcd_string('droping ..', 0)
    ser_port.write(b'drop')
    time.sleep(2)
    lcd.lcd_clear()
    lcd.lcd_string('moving back ..', 0)
    ser_port.write(b'0')
    get_ack()
    lcd.lcd_clear()
    ser_port.write(b'pick')
    global turn
    lcd.lcd_clear()
    lcd.lcd_string('Your turn ..', 0)
    turn = 1
    
def main():
    initialize()
    global turn
    time.sleep(4)
    while True:
        ser_port.write(b'0')
        get_ack()
        ser_port.write(b'pick')
        choose_start()
        if turn:
            time.sleep(4)
        lcd.lcd_clear()
        lcd.lcd_string('Checking board ..',0)
        global result
        result = 0
        #play
        while True:
            if algo.isWin(pre_state):
                if algo.whoWins(pre) == 'X':
                    result = 2
                else:
                    result = 1
                break
            if algo.isFull(pre_state):
                result = 0
                break
            while turn:
                if button.check():
                    lcd.lcd_clear()
                    lcd.lcd_string('My turn ..', 0)
                    turn = 0
                    break
            play_turn()
        
        lcd.lcd_clear()
        if result == 0:
            lcd.lcd_string('Draw', 0)
        elif result == 1:
            lcd.lcd_string('I win, you noob', 0)
        else:
            lcd.lcd_string('gg', 0)
        time.sleep(8)
        lcd.lcd_clear()
        lcd.lcd_string('again ?',0)
        while True:
            if button.check():
                break
main()
    