# Import some necessary libraries.
import socket
import time
import re
import random
import sys

# Some basic variables used to configure the bot        
server = "irc.snoonet.org"  # Server
port = 6667  # Port
recv_port = 2048  # Receive Port
# channel = "#climbing"  # Channel
channel = "#wavesonicstest"
bot_nick = "WavesonicsBot"  # Your bots nick

if len(sys.argv) > 1:
	print sys.argv
	bot_password = sys.argv[1]
else:
	bot_password = raw_input("Enter nickserv password: ")


def respond_to_ping(msg):  # This is our first function! It will respond to server Pings.
	irc_send("PONG :" + msg.body)


def sendmsg(chan, msg):  # This is the send message function, it simply sends messages to the channel.
	irc_send("PRIVMSG " + chan + " :" + msg)


def respond_to_message(message, body):
	if message.channel == bot_nick:
		sendmsg(message.name, body)
	else:
		sendmsg(message.channel, body)


class UserMessage(object):
	def __init__(self, msg):
		self.name = msg.source.split('!')[0]
		self.command = msg.command
		self.channel = msg.params[0]
		self.body = msg.body
		self.body_lower = msg.body.lower()


class IrcMessage(object):
	def __init__(self, msg):
		if msg[0] == ':':
			start_of_body = msg.find(':', 1)
			params = msg[1:start_of_body - 1].split()
			self.body = msg[start_of_body + 1:]
		else:
			start_of_body = msg.find(':')
			params = msg[0:start_of_body - 1].split()
			self.body = msg[start_of_body + 1:]
		self.params = []

		if msg[0] == ':':
			self.source = params[0]
			self.command = params[1]
			if len(params) > 2:
				for param in params[2:]:
					self.params.append(param)
		else:
			self.source = None
			self.command = params[0]
			if len(params) > 1:
				for param in params[1:]:
					self.params.append(param)


def join_chan(chan):  # This function is used to join channels.
	irc_send("JOIN " + chan)


def hello(msg):  # This function responds to a user that inputs "Hello Mybot"
	sendmsg(msg.channel, "Hello " + msg.name + "!")


def auth():
	irc_send("PRIVMSG NickServ :identify " + bot_nick + " " + bot_password)


def irc_send(message):
	print("\nSEND: " + message + "\n")
	irc_sock.send(message + "\n\r")


def find_watch_word_response(msg_words):
	watch_word = None
	for words in watch_words:
		for word in words[0]:
			if word in msg_words:
				watch_word = words[1]
				break
	return watch_word


# Responses when we see our name
common_responses = ["lol", "LOL", "hehe", "haha", ":P", "SpaceX", "interesting", "ya", "yaaaa", "cool"]
# Randomly spouted into the channel
tid_bits = ["Space is so fucking cool!", "Trad climbing", "lol cats"]
tid_bit_chance = 100
# If we see any of these words we will say the corresponding response
watch_words = \
	[
		[["destiny"], "Oh man, TTK must be out by now... I'm going to have to play that when I get back"],
		[["cats", "cat", "kitten", "kittens"], "aw"],
		[["free solo", "freesolo", "free-solo"], "whoa that's crazy man"],
		[["yosemite", "yos"], "Hey that's where I am right now!!! :D"],
		[["space", "spacex"], "SpaceX pushed back their return to flight again by a few months :("],
		[["wavesonics"], "Damn that guy is cool"],
	]

irc_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
irc_sock.connect((server, port))  # Here we connect to the server using port 6667

irc_send("NICK " + bot_nick)  # here we actually assign the nick to the bot
irc_send("USER " + bot_nick + " " + bot_nick + " " + bot_nick + ":I am a bot")  # user authentication

running = True
while running:  # Be careful with these! It might send you to an infinite loop
	irc_blob = irc_sock.recv(recv_port)  # receive data from the server
	irc_msgs = irc_blob.strip().split('\n')

	if irc_msgs:
		for msg_str in irc_msgs:
			msg_str = msg_str.strip()

			if msg_str:
				print("RECV: '" + msg_str + "'")  # Here we print what's coming from the server
				irc_msg = IrcMessage(msg_str)

				# Handle the general IRC message type
				if irc_msg.command == 'PRIVMSG':
					user_message = UserMessage(irc_msg)
					individual_worlds = user_message.body_lower.split()
					found_watch_word = find_watch_word_response(individual_worlds)
					if found_watch_word:
						sendmsg(channel, found_watch_word)
					elif user_message.body_lower.find(bot_nick.lower()) != -1:
						if user_message.body_lower.find("hello") != -1 or user_message.body_lower.find("hi") != -1:  # Standard greeting
							hello(user_message)
						elif user_message.body_lower.find("leave") != -1:
							sendmsg(channel, "Good bye")
							print("I was told to leave")
							running = False
						else:  # Random response
							respond_to_message(user_message, random.choice(common_responses))
					elif random.randint(0, tid_bit_chance) == 1:
						sendmsg(channel, random.choice(tid_bits))
				elif irc_msg.command == 'NOTICE':
					# Handle the login & join sequence
					if irc_msg.source == 'NickServ!NickServ@snoonet/services/NickServ' \
							and irc_msg.params[0] == bot_nick \
							and irc_msg.body.find('nick') == 0:
						auth()
					elif irc_msg.source == 'NickServ!NickServ@snoonet/services/NickServ' \
							and irc_msg.params[0] == bot_nick \
							and irc_msg.body.find('Password accepted') == 0:
						join_chan(channel)
				# Handle other general commands
				elif irc_msg.command == "PING":  # if the server pings us then we've got to respond!
					respond_to_ping(irc_msg)
				elif irc_msg.command == "ERROR":
					if msg_str.find("ERROR :Closing link:") != -1:
						print("Socket closed.")
						break
					else:
						print("Error!")
				else:
					print("Unhandled message type: " + irc_msg.command)

irc_sock.close()
