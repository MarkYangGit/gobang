from flask import Flask, render_template
from flask_socketio import SocketIO, emit,join_room,leave_room
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import random
from checkLine import check_win

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key_here'

Base = declarative_base()

# Define the SQLAlchemy model
class Room(Base):
    __tablename__ = 'roomList'
    playerNum = Column(String(2))
    player1 = Column(String(255))
    player2 = Column(String(255))
    roomID = Column(String(6),primary_key=True)
    

# Connect to the MySQL database using SQLAlchemy
engine = create_engine('mysql+pymysql://root:112316@8.130.129.201/GoBang')
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
session = Session()

socketio = SocketIO(app, cors_allowed_origins='*')

@app.route("/")
def index():
    return render_template("index.html")
#进房间列表
@app.route("/roomList")
def showRoomList():
   return render_template("roomList.html") 

#进入
@app.route("/gamePvP")
def gamePvP():
    return render_template("gamePvP.html")

# ... (other routes remain unchanged)

@socketio.on('newRoom')
def newRoom(data):  
    player1 = data['userID']
    player2 = ''
    playerNum = ''
    roomID = str(random.randint(100000, 999999))
    # state = 0
    join_room(roomID)
    # Create a new Room object and add it to the database
    new_room = Room(player1=player1, player2=player2, roomID=roomID, playerNum=playerNum)
    session.add(new_room)
    session.commit()

    emit('room_created', {'player1': player1, 'player2': player2, 'roomID': roomID, 'state': 0},broadcast=True)

@socketio.on('roomList')
def roomList():
    room_data = []
    
    # Retrieve room data from the database
    rooms = session.query(Room).all()
    
    for room in rooms:
        room_data.append({'player1': room.player1, 'player2': room.player2, 'roomID': room.roomID})
    
    emit('room_list', room_data)

@socketio.on('joinRoom')
def joinRoom(data):
     player = data['userID'] # 请求加入房间者的userID
     roomID = data['roomID'] # 请求加入的房间号
     room = session.query(Room).filter_by(roomID=roomID).first()
     if room:
         if room.playerNum == '':
            room.playerNum += '1'
            session.commit()
            emit('joinRoom_success'+roomID, {'player1': player, 'player2': '', 'room': roomID, 'state': 0}, broadcast=True)
         elif room.playerNum == '1':
            join_room(roomID)
            room.player2 = player
            room.playerNum += '1'
            session.commit()
            emit('joinRoom_success'+roomID, {'player1': room.player1, 'player2': player, 'room': roomID, 'state': 1}, broadcast=True)
         else:
            emit('joinRoom_fail', {'room': roomID})
     else:
         emit('Error! Can not find the room!')

# @socketio.on('startGame')
# def startGame(data):
#     roomID = data['roomID']
#     emit('startGame', room=roomID)

@socketio.on('fallChess')
def fallChess(data):
    print(data)
    roomID = data['roomID']
    col = data['col']
    row = data['row']
    player = data['player']
    emit('fallChess_success'+roomID, {'col': col, 'row': row, 'player': player,'roomID':roomID},broadcast=True)
    #可以加一个存储棋步到数据库的操作
    
@socketio.on('checkWin')
def CheckWin(data):
    print(data)
    roomID = data['roomID']
    col = data['col']
    row = data['row']
    player = data['player']
    board_data = data['board_data']
    if check_win(player,row,col,board_data):
        emit('Win'+roomID,{'winer':player,'roomID':roomID,'status':1},broadcast=True)

@socketio.on('repentance')
def repentance(data):
    roomID = data['roomID']
    emit('repentance_success', room=roomID)


if __name__ == '__main__':
    socketio.run(app,host="0.0.0.0",port=5000)
