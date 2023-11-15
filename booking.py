# Prerequisites
# Install python
# Install imgkit + wkhtmltopdf https://pypi.org/project/imgkit/
from datetime import date 
from datetime import timedelta
import json
import imgkit

class RoomAlreadyExists(Exception):
    pass
class RoomDoesntExist(Exception):
    pass
class TimeslotNotAvailable(Exception):
    pass
class InvalidBookingOnWeekend(Exception):
    pass
class BookingTooFarAhead(Exception):
    pass
class BookingInThePastForbidden(Exception):
    pass

# Internal structure of the booking system
# Map of rooms to days to open and booked slots
# {
#     "HW.003": {
#         "2023-12-30": {
#             "open_slots": [0, 2, 3...],
#             "booked_slots": []
#         }
#     }
# }

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
    def book_room(self, room_number, day, time_slot):
        if not room_number in self.rooms:
            raise RoomDoesntExist()
        self.validate_day(day)

        room = self.rooms[room_number]

        if not day.isoformat() in room:
            room[day.isoformat()] = {"open_slots": list(range(0, len(self.timeslots))), "booked_slots": []}

        room_at_day = room[day.isoformat()]
        if time_slot in room_at_day["booked_slots"]:
            raise TimeslotNotAvailable()
        room_at_day["booked_slots"].append(time_slot)
        room_at_day["open_slots"].remove(time_slot)
        
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
                if self.is_room_taken_at(room_number, day, slot):
                    table += "<td style=\"background-color:#ff7373\">------</td>"
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

    def is_room_taken_at(self, room, day, timeslot):
        room = self.rooms[room]
        if not day in room:
            return False
        room_at_day = room[day]
        return timeslot in room_at_day["booked_slots"]
    
        
def main():
    booking_system = BookingSystem()
    while True:
        line = input("> ").split()
        if len(line) == 2 and line[0] == "render":
            booking_system.render_image_to_file(line[1], "output.jpg")
        elif len(line) == 1 and line[0] == "quit":
            break
        elif len(line) == 1 and line[0] == "help":
            print_help()
        elif len(line) == 3 and line[0] == "add" and line[1] == "room":
            booking_system.add_room(line[2])
        elif len(line) == 4:
            room = line[1]
            d = date.fromisoformat(line[2])
            if not line[3] in booking_system.timeslots:
                print("Invalid slot " + line[3])
            else:
                booking_system.book_room(room, d, booking_system.timeslots.index(line[3]))
            pass
        else:
            print_help()

def print_help():
    print('''
Usage:
To quit:
    > quit
To add a room
    > add room HW.003
To book a room
    > book HW.003 2023-11-15 08:00-08:45
To render a room table
    > render HW.003
                  ''')

main()
