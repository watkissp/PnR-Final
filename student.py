
import pigo
import time  # import just in case students need
import random

# setup logs
import logging
LOG_LEVEL = logging.INFO
LOG_FILE = "/home/pi/PnR-Final/log_robot.log"  # don't forget to make this file!
LOG_FORMAT = "%(asctime)s %(levelname)s %(message)s"
logging.basicConfig(filename=LOG_FILE, format=LOG_FORMAT, level=LOG_LEVEL)


class Piggy(pigo.Pigo):
    """Student project, inherits teacher Pigo class which wraps all RPi specific functions"""

    def __init__(self):
        """The robot's constructor: sets variables and runs menu loop"""
        print("I have been instantiated!")
        # Our servo turns the sensor. What angle of the servo( ) method sets it straight?
        self.MIDPOINT = 77
        # YOU DECIDE: How close can an object get (cm) before we have to stop?
        self.SAFE_STOP_DIST = 30
        self.HARD_STOP_DIST = 15
        # YOU DECIDE: What left motor power helps straighten your fwd()?
        self.LEFT_SPEED = 135
        # YOU DECIDE: What left motor power helps straighten your fwd()?
        self.RIGHT_SPEED = 145
        # This one isn't capitalized because it changes during runtime, the others don't
        self.turn_track = 0
        # Our scan list! The index will be the degree and it will store distance
        self.scan = [None] * 180
        self.set_speed(self.LEFT_SPEED, self.RIGHT_SPEED)
        # let's use an event-driven model, make a handler of sorts to listen for "events"
        if __name__ == "__main__":
            while True:
                self.stop()
                self.menu()

    def menu(self):
        """Displays menu dictionary, takes key-input and calls method"""
        ## This is a DICTIONARY, it's a list with custom index values
        # You may change the menu if you'd like to add an experimental method
        menu = {"n": ("Navigate forward", self.nav),
                "d": ("Dance", self.dance),
                "o": ("Obstacle count", self.obstacle_count),
                "c": ("Calibrate", self.calibrate),
                "s": ("Check status", self.status),
                "h": ("Open House", self.open_house),
                "t": ("Test", self.skill_test),
                "q": ("Quit", quit_now)
                }
        # loop and print the menu...
        for key in sorted(menu.keys()):
            print(key + ":" + menu[key][0])
        # store the user's answer
        ans = raw_input("Your selection: ")
        # activate the item selected
        menu.get(ans, [None, error])[1]()

    def skill_test(self):
        """demonstrates two nav skills"""
        choice = raw_input("Left/Right or Turn Until Clear?")

        if "l" in choice:
            self.wide_scan(count=4)  #scan the area
            # create two variables, left_total and right_total
            left_total = 0
            right_total = 0
            # loop from self.MIDPOINT - 60 to self.MIDPOINT
            for angle in range(self.MIDPOINT - 60, self.MIDPOINT):
                if self.scan[angle]:
                    # add up the numbers to right_total
                    right_total += self.scan[angle]
            # loop from self.MIDPOINT to self.MIDPOINT + 60
            for angle in range(self.MIDPOINT, self.MIDPOINT + 60):
                if self.scan[angle]:
                    # add up the numbers to left_total
                    left_total += self.scan[angle]
            # if right is bigger:
            if right_total > left_total:
                # turn right
                self.encR(4)
                self.encF(10)
            # if left is bigger:
            else:
                # turn left
                self.encL(4)
                self.encF(10)

        else:
            #turns until it's clear
            pass


    def open_house(self):
        """reacts to dist measurement in a cute way"""
        while True:
            if self.dist() < 20:
                self.encB(3)
                time.sleep(1)
                self.encR(3)
                time.sleep(1)
                self.encL(6)
                time.sleep(1)
                self.encR(3)
                time.sleep(1)
                self.encF(3)
                time.sleep(1)
                for x in range(5):
                    self.servo(self.MIDPOINT - 30)
                    self.servo(self.MIDPOINT + 30)
                self.servo(self.MIDPOINT)
            time.sleep(.1)

    # YOU DECIDE: How does your GoPiggy dance?
    def dance(self):
        """executes a series of methods that add up to a compound dance"""
        if not self.safe_to_dance():
            print("\n---- Not Safe To Dance----\n")
            return
        print("\n---- LET'S DANCE ----\n")

        for x in range(1):
            self.dab_on_them()
            self.shoot()
            self.whip()
            self.nae_nae()
            self.fade()
            self.sprinkler()

    def safe_to_dance(self):
        """checks for obstacles in way"""
        for x in range(4):
            if not self.is_clear():
                return False
            self.encR(10)
        return True

    def dab_on_them(self):
        """"Head turns while body moves same direction"""
        for x in range(3):
            self.servo(self.MIDPOINT - 30)
            self.encL(10)
            self.servo(self.MIDPOINT + 30)
            self.servo(self.MIDPOINT + 30)
            self.encR(10)
            self.servo(self.MIDPOINT - 30)

    def shoot(self):
        """"Head turns while body moves forward"""
        for x in range(3):
            self.servo(self.MIDPOINT - 30)
            self.encF(1)
            self.right_rot()
            self.servo(self.MIDPOINT + 30)
            self.servo(self.MIDPOINT + 30)
            self.encF(1)
            self.left_rot()
            self.servo(self.MIDPOINT - 30)
            self.servo(self.MIDPOINT - 30)

    def whip(self):
        """"Head turns back and forth"""
        for y in range(10):
            for x in range(self.MIDPOINT - 30, self.MIDPOINT + 30, 30):
                self.servo(x)

    def nae_nae(self):
        """Moves right, left, then back 3 times"""
        for x in range(3):
            self.encL(3)
            self.encR(3)
            self.encB(5)

    def fade(self):
        """Head turns while body moves opposite direction"""
        for x in range(2):
            self.right_rot()
            self.servo(self.MIDPOINT - 30)
            time.sleep(1)
            self.left_rot()
            self.servo(self.MIDPOINT + 30)
            time.sleep(1)
            self.stop()

    # FROM MR. ADILETTA
    def sprinkler(self):
            """"moves your head like a sprinkler"""
            # repeat the move 5 times
            for x in range(5):
                for angle in range(self.MIDPOINT - 20, self.MIDPOINT + 20, 5):
                    self.servo(angle)

    def obstacle_count(self):
        """scans and estimates the number of obstacles within sight"""
        self.wide_scan()
        found_something = False
        counter = 0
        for ang, distance in enumerate(self.scan):
            if distance and distance < 150 and not found_something:
                found_something = True
                counter += 1
                print("Object # %d found, I think" % counter)
            if distance and distance > 150 and found_something:
                found_something = False
        print("\n----I SEE %d OBJECTS----\n" % counter)

    def safety_check(self):
        """subroutine of the dance method"""
        self.servo(self.MIDPOINT)  # look straight ahead
        for loop in range(4):
            if not self.is_clear():
                print("NOT GOING TO DANCE")
                return False
            print("Check #%d" % (loop + 1))
            self.encR(8)  # figure out 90 deg
        print("Safe to dance!")
        return True

    def nav(self):
        """auto pilots and attempts to maintain original heading"""
        logging.debug("Starting the nav method")
        print("-----------! NAVIGATION ACTIVATED !------------\n")
        print("-------- [ Press CTRL + C to stop me ] --------\n")
        print("-----------! NAVIGATION ACTIVATED !------------\n")
        while True:
            if self.is_clear():
                self.cruise()
            else:
                self.encR(10)

    def cruise(self):
        """ drive straight while path is clear """
        self.fwd()
        while self.dist() > self.SAFE_STOP_DIST:
            time.sleep(.5)
        self.stop()
####################################################
############### STATIC FUNCTIONS

def error():
    """records general, less specific error"""
    logging.error("ERROR")
    print('ERROR')


def quit_now():
    """shuts down app"""
    raise SystemExit

##################################################################
######## The app starts right here when we instantiate our GoPiggy


try:
    g = Piggy()
except (KeyboardInterrupt, SystemExit):
    pigo.stop_now()
except Exception as ee:
    logging.error(ee.__str__())
