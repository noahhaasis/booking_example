# Prerequisites
# Install python
# Install imgkit + wkhtmltopdf https://pypi.org/project/imgkit/
from dataclasses import dataclass
from datetime import date 
from datetime import timedelta
import json
import imgkit

class RoomAlreadyExists(Exception):
    def __str__(self):
        return "This room already exists."
class RoomDoesntExist(Exception):
    def __str__(self):
        return "This room doesn't exist."
class TimeslotNotAvailable(Exception):
    def __str__(self):
        return "This timeslot is not available."
class InvalidBookingOnWeekend(Exception):
    def __str__(self):
        return "Invalid booking on the weekend."
class BookingTooFarAhead(Exception):
    def __str__(self):
        return "This booking is too far ahead."
class BookingInThePastForbidden(Exception):
    def __str__(self):
        return "Bookings in the past are not allowed."

# Internal structure of the booking system
# Map of rooms to days to open and booked slots
# {
#     "HW.003": {
#         "2023-12-30": {
#             "open_slots": [0, 2, 3...],
#             "booked_slots": [create_booking(1, "Statistik", "Wermuth")]
#         }
#     }
# }

def create_booking(slot, class_name = None, prof_name = None):
    return {"slot": slot, "class_name": class_name, "prof_name": prof_name}

class BookingSystem:
    timeslots = [
        "08:00-08:45",
        "08:45-09:30",
        "09:45-10:30",
        "10:30-11:15",
        "11.30-12:15",
        "12:15-13:00",
        "13:00-14:00",
        "14:00-14:45",
        "14:45-15:30",
        "15:45-16:30",
        "16:30-17:15",
        "17:30-18:15",
        "18:15-19:00"
    ]
    rooms = {}

    def __init__(self):
        try:
            with open("bookings.json") as storage_file:
                self.rooms = json.load(storage_file)
        except IOError:
            pass

    # Example Usage:
    # > booking_system.add_room("HW.003")
    def add_room(self, room_number):
        if room_number in self.rooms:
            raise RoomAlreadyExists()
        
        self.rooms[room_number] = {}
        self.persist()

    # Example Usage:
    # > booking_system.book_room("HW.003", date.fromisoformat("2023-12-28"), 1)
    def book_room(self, room_number, day, booking):
        if not room_number in self.rooms:
            raise RoomDoesntExist()
        self.validate_day(day)

        room = self.rooms[room_number]

        if not day.isoformat() in room:
            room[day.isoformat()] = {"open_slots": list(range(0, len(self.timeslots))), "booked_slots": []}

        room_at_day = room[day.isoformat()]
        if any(b["slot"] == booking["slot"] for b in room_at_day["booked_slots"]):
            raise TimeslotNotAvailable()
        room_at_day["booked_slots"].append(booking)
        room_at_day["open_slots"].remove(booking["slot"])
        
        self.persist()

    def render_table(self, room_number):
        if not room_number in self.rooms:
            raise RoomDoesntExist()
        
        monday = date.today() - timedelta(days=date.today().weekday())
        days_of_this_week = [(monday + timedelta(days=i)).isoformat() for i in range(0, 5)]

        table = '''
            <style>
                th {
                    width: 85px;
                }
                table {
                    height: 450px;
                    text-align: center;
                }
                #container {}
                    
            </style>
            <div style="width: 800px">
            <table style="margin: 0 auto">
                <caption><h3>
        ''' + room_number + '''
                </h3></caption>
                <tr>
                    <th scope="col"></th>
                    <th scope="col">Montag</th>
                    <th scope="col">Dienstag</th>
                    <th scope="col">Mittwoch</th>
                    <th scope="col">Donnerstag</th>
                    <th scope="col">Freitag</th>
                </tr>
        '''
        for slot in range(0, len(self.timeslots)):
            table += "  <tr><th scope=\"row\">" + self.timeslots[slot] + "</th>"
            for day in days_of_this_week:
                booking = self.get_booking_at(room_number, day, slot)
                if booking is not None:
                    content = (booking["class_name"] if "class_name" in booking else "------") + (("<br>" + booking["prof_name"]) if "prof_name" in booking else "")
                    table += "<td style=\"background-color:#ff7373\">" + content + "</td>"
                else:
                    table += "<td style=\"background-color:#c3fcab\"></td>"
            table += "</tr>"
        table += "</table></div>"
        return table

    def render_image_to_file(self, room, filename):
        # 480 * 800
        options = {'width': 800, 'height': 480, 'disable-smart-width': ''}
        imgkit.from_string(self.render_table(room), 'out.jpg', options=options)

    def persist(self):
        with open("bookings.json", "w") as storage_file:
            json.dump(self.rooms, storage_file)
        
    def validate_day(self, day):
        # within the next two weeks
        if day.weekday() in [5, 6]:
            raise InvalidBookingOnWeekend()
        
        num_days_ahead = (day - date.today()).days
        # not on the weekend
        if num_days_ahead > 13:
            raise BookingTooFarAhead()
        # not in the past
        if num_days_ahead < 0:
            raise BookingInThePastForbidden()

    def get_booking_at(self, room, day, timeslot):
        room = self.rooms[room]
        if not day in room:
            return None
        room_at_day = room[day]
        return next(filter(lambda booking: booking["slot"] == timeslot, room_at_day["booked_slots"]), None)
    
        
def main():
    booking_system = BookingSystem()
    while True:
        line = input("> ").split()
        try:
            if len(line) == 2 and line[0] == "render":
                booking_system.render_image_to_file(line[1], "output.jpg")
            elif len(line) == 1 and line[0] == "quit":
                break
            elif len(line) == 1 and line[0] == "help":
                print_help()
            elif len(line) == 3 and line[0] == "add" and line[1] == "room":
                booking_system.add_room(line[2])
            elif len(line) == 4 and line[0] == "book":
                room = line[1]
                d = date.fromisoformat(line[2])
                if not line[3] in booking_system.timeslots:
                    print("Invalid slot " + line[3])
                else:
                    booking = create_booking(booking_system.timeslots.index(line[3]))
                    booking_system.book_room(room, d, booking)
            elif len(line) == 7 and line[0] == "book" and line[1] == "class":
                room = line[4]
                d = date.fromisoformat(line[5])
                class_name = line[2]
                prof_name = line[3]
                if not line[6] in booking_system.timeslots:
                    print("Invalid slot " + line[6])
                else:
                    booking = create_booking(booking_system.timeslots.index(line[6]), class_name, prof_name)
                    booking_system.book_room(room, d, booking)
            else:
                print_help()
        except Exception as e:
            print_error(e)

def print_help():
    print('''
Usage:
To quit:
    > quit
To add a room
    > add room HW.003
To book a room as a student
    > book HW.003 2023-11-15 08:00-08:45
To book a room for a class
    > book class Statistik Wermuth HW.003 2023-11-15 08:00-08:45
To render a room table
    > render HW.003
                  ''')

def print_error(error):
    # Print the error in yellow
    print("\033[93m" + str(error) + "\033[0m")

main()
