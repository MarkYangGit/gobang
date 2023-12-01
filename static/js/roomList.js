function createRoomItem(roomID, blackPlayer, whitePlayer) {
    // 创建各个元素
    var roomItem = document.createElement('div');
    roomItem.classList.add('roomItem');
    roomItem.setAttribute('data-roomid', roomID);
    roomItem.addEventListener('click', joinRoom);

    var roomIDBox = document.createElement('div');
    roomIDBox.classList.add('roomIDBox');

    var idText = document.createElement('div');
    idText.classList.add('idText');
    idText.innerHTML = '<span>房间ID：</span>';

    var roomIDElement = document.createElement('div');
    roomIDElement.classList.add('roomID');
    roomIDElement.textContent = roomID;

    var separator = document.createElement('div');
    separator.style.height = '1px';
    separator.style.backgroundColor = 'black';

    var userList = document.createElement('div');
    userList.classList.add('userList');

    var blackUserBox = createUserBox('黑方：', blackPlayer);
    var whiteUserBox = createUserBox('白方：', whitePlayer);

    // 添加所有子元素到对应的父元素中
    roomIDBox.appendChild(idText);
    roomIDBox.appendChild(roomIDElement);

    userList.appendChild(blackUserBox);
    userList.appendChild(whiteUserBox);

    roomItem.appendChild(roomIDBox);
    roomItem.appendChild(separator);
    roomItem.appendChild(userList);

    return roomItem;
}

// 创建用户框
function createUserBox(userType, userName) {
    var userBox = document.createElement('div');
    userBox.classList.add('userBox');

    var userTitle = document.createElement('div');
    userTitle.classList.add('userTitle');
    userTitle.innerHTML = `<span>${userType}</span>`;

    var userNameElement = document.createElement('div');
    userNameElement.classList.add('userName');
    userNameElement.innerHTML = `<span>${userName}</span>`;

    userBox.appendChild(userTitle);
    userBox.appendChild(userNameElement);

    return userBox;
}

// 添加新的 roomItem 到 roomList
function addRoomToList(roomID, blackPlayer, whitePlayer) {
    var roomList = document.getElementById('roomList');
    // roomList.innerHTML = null
    var newRoomItem = createRoomItem(roomID, blackPlayer, whitePlayer);
    roomList.appendChild(newRoomItem);
}

function joinRoom(e) {
    var roomId = e.target.dataset.roomId

    window.location.href = "./gamePvP?roomid=" + roomId;
}
let socket = null
function onLoad() {
    
}
function createRoom() {
    socket.emit("newRoom")
}
document.addEventListener("DOMContentLoaded", function() {
    socket = io('http://127.0.0.1:5000/');
    socket.emit("roomList");
    socket.on("room_list", (res) => {
        console.log(res)
        var roomList = document.getElementById('roomList');
        roomList.innerHTML = null 
        res.forEach(element => {
            addRoomToList(element.roomID, element.player1, element.player2);
        });
        
        // window.location.href = "./gamePvP?roomID="+res.roomID;
    }) 
    socket.on("room_created",res=>{
        addRoomToList(res.roomID, res.player1, res.player2); 
    })
});
function getRoomList() {
    socket = io('http://127.0.0.1:5000/');
    socket.on("connect", (res) => {
        console.log("连接成功")
        
    })
    console.log('9')
    socket.emit("roomList");
    socket.on("room_list", (roomList) => {
        console.log(roomList); // 打印 roomList 列表
        roomList.forEach(element => {
            addRoomToList(element.roomID,element.player1,element.player2) 
        });
    });

}

function addClick()
{
    const index = document.getElementById("indexPage")
    index.addEventListener("click",function(){
        window.location.href = "/"; 
    })
}
addClick()

onLoad()
