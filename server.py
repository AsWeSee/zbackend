import os
import time

from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_socketio import SocketIO, join_room, leave_room, send, emit, rooms


app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret'
CORS(app)
ws = SocketIO(app, cors_allowed_origins='*')

all_rooms = {}
all_content = {}


@ws.on('join')
def on_join(room):
    join_room(room)
    send(
        {
            'message': 'A new person has entered the room.',
            'timestamp': int(time.time()),
        },
        room=room
    )
    all_rooms.setdefault(room, 0)
    all_rooms[room] += 1

@ws.on('leave')
def on_leave(room):
    leave_room(room)
    send(
        {
          'message': 'Someone has left the room.',
          'timestamp': int(time.time()),
        },
        room=room
    )
    all_rooms[room] -= 1
    if all_rooms[room] == 0:
        all_rooms.pop(room)

@ws.on('message')
def on_message(msg):
    # broadcast to everyone in the same room on the 'message' channel
    my_rooms = rooms() # get all rooms of this user
    my_rooms.remove(request.sid) # remove personal room
    emit(
        'message', 
        {
            'message': msg, 
            'timestamp': int(time.time())
        },
        room=my_rooms[-1],
        json=True
    )

@app.route('/rooms')
def list_rooms():
    return jsonify(list(all_rooms.keys()))

@app.route('/content', methods=['GET', 'POST'])
def content():
    print(request)
    if request.method == 'POST':

        request_data = request.get_json()

        id = request_data['id']
        content = request_data['content']

        all_content[id] = content

        #id = request.form.get('id')
	#content = requesr.form.get('content')
        return 'nice'
    else:
        #request_data = request.get_json()

        id = request.args.get('id')
        print(id)
        content = all_content.get(id)
        print(content)
        data = {'content': content}

        return jsonify(data)




    return jsonify(list(all_rooms.keys()))

if __name__ == '__main__':
    ws.run(
        app,
        host='0.0.0.0', # listen to outside requests 
        port=int(os.getenv('PORT', '5001')),
        debug=True,
    )

