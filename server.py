import socket
from _thread import *
import sys
from time import sleep
import json
import random
import math

ip = input('Ip: ')

server = ip
port = 5555

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

oldData = None

try:
    s.bind((server, port))
except socket.error as e:
    print(str(e))
    quit()

s.listen(2)
print("Waiting for a connection, Server Started")

def read_pos(str):
    str = str.split(",")
    return int(str[0]), int(str[1])


def make_pos(tup):
    return str(tup[0]) + "," + str(tup[1])


p1_bullets = []
p2_bullets = []

game_state =[
    {
        'pos':[255,500],
        'bullets' : [],
        'astroids' : [], 
        'speedyAstroids' : [],
        'player' : 2,
        'inGame' : False
    },
    {
        'pos':[255,500],
        'bullets' : [],
        'astroids' : [],
        'speedyAstroids' : [],
        'player' : 1,
        'inGame' : False
    }
]
pos = [game_state[0]['pos'],game_state[1]['pos']]
bullets = [game_state[0]['bullets']+game_state[1]['bullets']]


print(game_state[0])
game_state_as_str = json.dumps(game_state)
#conn.send(game_state_as_str.encode('utf-8'))


#in our server threaded_client loop

astroidPoses = []
gameTime = 0

def threaded_client(conn, player):
    #conn.send(str.encode(make_pos(pos[player])))
    print(game_state_as_str)
    temp = json.dumps(game_state[player])
    conn.send(str.encode(temp))
    reply = ""
    test = False
    while True:
        try:
            strData = conn.recv(2048).decode()
            try:
                from_pos = strData.find('{')
                to_pos = strData.find('}') + 1
                strData = strData[from_pos:to_pos]
                data = json.loads(strData)           
            except:
                data = oldData
            try:
                game_state[player]['pos'] = data['pos']
                #print(game_state[int(player)]['pos'])
                game_state[player]['bullets'] = data['bullets']
                game_state[player]['astroids'] = data['astroids']
                game_state[player]['speedyAstroids'] = data['speedyAstroids']
                game_state[player]['inGame'] = data['inGame']
            except:
                pass
            
            #print(game_state)

           

            if not data:
                print("Disconnected")
                
            else:
                if player ==1:
                    result = game_state[0]
                    reply = json.dumps(result)
                    #game_state[1]['astroids'] = game_state[0]['astroids']
                    
                    
                else:
                    result = game_state[1]
                    reply = json.dumps(result)
                    #game_state[0]['astroids'] = data['astroids']
                    
                    

                #print("Received: ", data)
                #print("Sending : ", reply)
                

            conn.send(reply.encode('utf-8'))
        except Exception as e:
            print('ERROR!')
            print('strdata', strData)
            print(e)
            #quit()
            break
    
    

    print("Lost connection")
    conn.close()

currentPlayer = 0
while True:
    conn, addr = s.accept()
    print("Connected to:", addr)

    start_new_thread(threaded_client, (conn, currentPlayer))
    #global gameTime
    #global astroidPoses

    currentPlayer += 1


    