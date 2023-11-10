from flask import Flask

app = Flask(__name__)

class BookingSystem:
    rooms = ["HW.007", "HW.003"]

    def book_room(self, room_number, time):
        pass

    def get_all_rooms(self):
        return "Return something sensible here. a list or image or html"

booking_system = BookingSystem()

@app.route("/rooms")
def rooms():
    return booking_system.get_all_rooms()

@app.route('/rooms/<room_id>', methods=['POST'])
def book_room(room_id):
    booking_system.book_room(room_id, None)
    return f'Successfully booked room {room_id}'
