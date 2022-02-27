#!/usr/bin/env python
# by bl4de | github.com/bl4de | twitter.com/_bl4de | hackerone.com/bl4de
import socket
import threading
import sys
import liquidcrystal_i2c
#import time
def usage():
    #lcd = liquidcrystal_i2c.LiquidCrystal_I2C(0x27, 1, numlines=4)
    print("IRC simple Python client | by bl4de | github.com/bl4de | twitter.com/_bl4de | hackerone.com/bl4de\n")
    #print("init task 0 - debug msg")
    #while 0 == 0:
        #lcd.printline(0, "test")
        #time.sleep(100)
    print("$ ./irc_client.py USERNAME CHANNEL\n")
    print("where: USERNAME - your username, CHANNEL - channel you'd like to join (eg. channelname or #channelname)")


def channel(channel):
    if channel.startswith("#") == False:
        return "#" + channel
    return channel

# helper function used as thread target
def print_response():
    lcd = liquidcrystal_i2c.LiquidCrystal_I2C(0x27, 1, numlines=4)
    resp = client.get_response()
    if resp:
        msg = resp.strip().split(":")
        if data <= 3:
            lcd.printline(data,"< {}> {}".format(msg[1].split("!")[0], msg[2].strip()))
        else:
            for x in range(0, 3):
                lcd.printline(x, "")
        #print("< {}> {}".format(msg[1].split("!")[0], msg[2].strip()))
        if data == 0:
            data = data + 1
        elif data == 1:
            data = data + 1
        elif data == 2:
            data = data + 1
        elif data == 3:
            data = data - 3
            for x in range(0, 3):
                lcd.printline(x, "")
        else:
            data = data - 3
            for y in range(0, 3):
                lcd.printline(y, "")


class IRCSimpleClient:

    def __init__(self, username, channel, server="irc.freenode.net", port=6667):
        self.username = username
        self.server = server
        self.port = port
        self.channel = channel

    def connect(self):
        self.conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.conn.connect((self.server, self.port))

    def get_response(self):
        return self.conn.recv(512).decode("utf-8")

    def send_cmd(self, cmd, message):
        command = "{} {}\r\n".format(cmd, message).encode("utf-8")
        self.conn.send(command)

    def send_message_to_channel(self, message):
        command = "PRIVMSG {}".format(self.channel)
        message = ":" + message
        self.send_cmd(command, message)

    def join_channel(self):
        cmd = "JOIN"
        channel = self.channel
        self.send_cmd(cmd, channel)


if __name__ == "__main__":
    if len(sys.argv) != 3:
        usage()
        exit(0)
    else:
        username = sys.argv[1]
        channel = channel(sys.argv[2])
    data = 0
    lcd = liquidcrystal_i2c.LiquidCrystal_I2C(0x27, 1, numlines=4)
    cmd = ""
    joined = False
    client = IRCSimpleClient(username, channel)
    client.connect()
    int_data = 0
    while(joined == False):
        resp = client.get_response()
        if int_data == 0:
            int_data = int_data + 1
        elif int_data == 1:
            int_data = int_data + 1
        elif int_data == 2:
            int_data = int_data + 1
        elif int_data == 3:
            int_data = int_data - 3
            for z in range(0, 3):
                lcd.printline(z, "")
        else:
            int_data = int_data - 3
            for i in range(0, 3):
                lcd.printline(i, "")
        #print(resp.strip())
        lcd.printline(int_data, resp.strip())
        if "No Ident response" in resp:
            client.send_cmd("NICK", username)
            client.send_cmd(
                "USER", "{} * * :{}".format(username, username))

        # we're accepted, now let's join the channel!
        if "376" in resp:
            client.join_channel()

        # username already in use? try to use username with _
        if "433" in resp:
            username = "_" + username
            client.send_cmd(
                "USER", "{} * * :{}".format(username, username))
            client.send_cmd("NICK", username)

        # if PING send PONG with name of the server
        if "PING" in resp:
            client.send_cmd("PONG", ":" + resp.split(":")[1])

        # we've joined
        if "366" in resp:
            joined = True

    while(cmd != "/quit"):
        cmd = input("< {}> ".format(username)).strip()
        if cmd == "/quit":
            client.send_cmd("QUIT", "Good bye!")
        client.send_message_to_channel(cmd)

        # socket conn.receive blocks the program until a response is received
        # to prevent blocking program execution, receive should be threaded
        response_thread = threading.Thread(target=print_response)
        response_thread.daemon = True
        response_thread.start()