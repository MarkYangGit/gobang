from flask import Flask, render_template
from flask_socketio import SocketIO, emit
import random
from checkLine import check_win
import shareData

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key_here'

socketio = SocketIO(app, cors_allowed_origins='*')

@app.route("/")
def index():
    return render_template("index.html")



@app.route("/roomList")
def showRoomList():
   return render_template("roomList.html") 


@app.route("/gamePvP")
def gamePvP():
    return render_template("gamePvP.html")


@socketio.on('newRoom')
def newRoom(data):  
    player1 = data['userID']
    player2 = ''
    playerNum = ''
    moves=[]
    isAgainGame = []
    roomID = str(random.randint(100000, 999999))
    shareData.rooms.add_room(roomID,player1,player2,playerNum,moves,isAgainGame)
    emit('room_created', {'player1': player1, 'player2': player2, 'roomID': roomID, 'state': 0},broadcast=True)


@socketio.on('roomList')
def roomList():
    room_data = []
    current = shareData.rooms.head
    while current is not None:
        room_data.append({
            'roomID': current.roomID,
            'player1': current.player1,
            'player2': current.player2
        })
        current = current.next
    print(room_data)
    emit('room_list',room_data)


@socketio.on('joinRoom')
def joinRoom(data):
    player = data['userID'] #请求加入房间者的userID
    roomID = data['roomID']
    current = shareData.rooms.get_room(roomID)
    if current is not None:
        if current.playerNum == '':
            current.playerNum += '1'
            # 新建房间时已进行player1的赋值
            emit('joinRoom_success'+roomID, {'player1': player, 'player2': '', 'room': roomID, 'state': 0}, broadcast=True)
        elif current.playerNum == '1':
            current.player2 = player
            current.playerNum += '1'
            emit('joinRoom_success'+roomID, {'player1': current.player1, 'player2': player, 'room': roomID, 'state': 1}, broadcast=True)
        else:
            emit('joinRoom_fail', {'room': roomID})
    else:
        print('Cant find the room!'+roomID)



@socketio.on('fallChess')
def fallChess(data):
    roomID = data['roomID']
    col = data['col']
    row = data['row']
    player = data['player']
    current = shareData.rooms.get_room(roomID)
    current.moves.append([row,col,player])
    emit('fallChess_success'+roomID, {'col': col, 'row': row, 'player': player,'roomID':roomID},broadcast=True)


@socketio.on('checkWin')
def checkWin(data):
    roomID = data['roomID']
    player = data['player']
    board_data = data['board_data']
    current = shareData.rooms.get_room(roomID)
    # print(player,current.moves[-1][0],current.moves[-1][1],board_data)
    if(check_win(player,current.moves[-1][0],current.moves[-1][1],board_data)):
        emit('Win'+roomID,{'winer':current.moves[-1][2],'roomID':roomID,'status':1},broadcast=True)



#发起悔棋操作
@socketio.on('repentance')
def repentance(data):
    roomID = data['roomID']
    player = data['player']
    emit('IsRepentance'+roomID,{"roomID":roomID,"player":player},broadcast=True)


#悔棋操作结果
@socketio.on('AcceptRepentance')
def AcceptRepentance(data):
    roomID = data['roomID']
    player = data['player']
    isAccept = data['isAccept']
    current = shareData.rooms.get_room(roomID)
    current.moves.pop()
    current.moves.pop()
    if(isAccept == "1"):
        emit("RepentanceResult"+roomID,{"result":1,"moves":current.moves},broadcast=True)
    else:
        emit("RepentanceResult"+roomID,{"result":0},broadcast=True)


#认输
@socketio.on('AdmitDefeat')
def AdmitDefeat(data):
    roomID = data['roomID']
    player = data['player']
    emit("AdmitDefeat"+roomID,{"player":player},broadcast=True)



#求和
@socketio.on("Peace")
def Peace(data):
    roomID = data['roomID']
    player = data['player']
    emit('Peace'+roomID,{"roomID":roomID,"player":player},broadcast=True)



#确认求和
@socketio.on('AcceptPeace')
def AcceptPeace(data):
    print(data)
    roomID = data['roomID']
    player = data['player']
    isAccept = data['isAccept']
    print(type(isAccept))
    if(isAccept == "1"):
        emit("AcceptPeace"+roomID,{"result":1},broadcast=True)
    else:
        emit("AcceptPeace"+roomID,{"result":0},broadcast=True)



#再来一局
@socketio.on('AgainGame')
def AgainGame(data):
    roomID = data['roomID']
    userID = data['userID']
    isAgain = data['isAgain']
    current = shareData.rooms.get_room(roomID)
    if isAgain == "1":
        current.isAgainGame.append(userID)

    if len(shareData.isAgainGame[roomID]) == 2:
        emit("AgainGame"+roomID,{"againGame":1, "isAgain":isAgain},broadcast=True)
        current.isAgainGame = []
    else:
        emit("AgainGame"+roomID,{"againGame":0, "isAgain":isAgain},broadcast=True)


if __name__ == '__main__':
    socketio.run(app,host="0.0.0.0",port=5001)
