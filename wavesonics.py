# Imports
import socket
import time
import re
import random
import sys

# Configure the bot
server = "irc.snoonet.org"  # Server
port = 6667  # Port
recv_port = 2048  # Receive Port
# channel = "#climbing"  # Channel
channel = "#wavesonicstest"
bot_nick = "WavesonicsBot"  # Bots nick
bot_description = "This is my bot, there are many like it but this one is mine."

if len(sys.argv) > 1:
	print sys.argv
	bot_password = sys.argv[1]
else:
	bot_password = raw_input("Enter nickserv password: ")


def respond_to_ping(msg):  # Respond to server Pings.
	irc_send("PONG :" + msg.body)


def sendmsg(chan, msg):  # Simply sends messages to the channel.
	irc_send("PRIVMSG " + chan + " :" + msg)


def respond_to_message(message, body):
	if message.channel == bot_nick:
		sendmsg(message.name, body)
	else:
		sendmsg(message.channel, body)


# A more specific message type, a chat message from a user
class UserMessage(object):
	def __init__(self, msg):
		self.name = msg.source.split('!')[0]
		self.command = msg.command
		self.channel = msg.params[0]
		self.body = msg.body
		self.body_lower = msg.body.lower()


# A general IRC message
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


def join_chan(chan):  # Join an IRC channel
	irc_send("JOIN " + chan)


def hello(msg):  # Responds to a user that inputs "Hello BotName"
	sendmsg(msg.channel, "Hello " + msg.name + "!")


def nick_auth():  # Authorize your nick name
	irc_send("PRIVMSG NickServ :identify " + bot_nick + " " + bot_password)


def irc_send(message):  # Send a raw message to the IRC server
	print("\nSEND: " + message + "\n")
	irc_sock.send(message + "\n\r")


def find_watch_word_response(msg_words):
	watch_word = None
	for words in watch_words:
		for word in words[0]:
			if word in msg_words:
				watch_word = random.choice(words[1])
				break
	return watch_word


def find_directed_response(msg_words):
	response = None
	for words in directed:
		for word in words[0]:
			if word in msg_words:
				response = random.choice(words[1])
				break
	return response


# Responses when we see our name
common_responses = ["lol", "LOL", "LOLOL", "hehe", "haha", ":P", "SpaceX", "interesting", "ya", "yaaaa", "cool", "nice", "nice!"]
common_response_chance = 500  # 1 in X chance of spouting a common response

# Randomly spouted into the channel
tid_bits = \
	[
		"Space is so fucking cool!",
		"Trad climbers am I right?",
		"lol cats",
		"Rock climbing is pretty cool I guess",
		"Man it's hot in here",
		"brb"
	]
tid_bit_chance = 1000  # 1 in X chance of spouting a tid bit

# If we see any of these words we will say the corresponding response
watch_words = \
	[
		[["destiny"], ["Oh man, TTK must be out by now... I'm going to have to play that when I get back", "I hear their companion app is awesome."]],
		[["cats", "cat", "kitten", "kittens"], ["aw", "cute"]],
		[["freesolo", "free-solo"], ["whoa that's crazy man", "Alex Honnold"]],
		[["yosemite", "yos"], ["Hey that's where I am right now!!! :D"]],
		[["space", "spacex"], ["SpaceX pushed back their return to flight again by a few months :("]],
		[["wavesonics"], ["Damn that guy is cool", "so handsome", "I hear he's out climbing in Yosemite right now"]],
		[["dicks", "dick"], ["Whoa there!"]],
		[["beer"], ["I could go for one", "attaboy nonsense", "beta kill"]],
	]

# Only respond to these if they are directed at us
directed = \
	[
		[["goodnight", "night"], ["Good night :)", "nighty night"]],
		[["tinyonion"], ["That guy's all right", "Not so tiny, but he'll make you cry"]],
		[["toasti"], ["Toasted", "Gotta butter him up"]],
		[["kdj"], ["It's just a bunch of letters that became sentient", "Katie Jay"]],
		[["ned"], ["Flanders"]],
		[["nonsense"], ["I could beat him in a fight", "beta kill nonsense"]],
		[["beta"], ["nonsense beta", "na he's cool"]],
	]

irc_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
irc_sock.connect((server, port))  # Connect to the server using port 6667

irc_send("NICK " + bot_nick)  # Actually assign the nick to the bot
irc_send("USER " + bot_nick + " " + bot_nick + " " + bot_nick + " :" + bot_description)  # User authentication

running = True
while running:  # Message pump
	irc_blob = irc_sock.recv(recv_port)  # Receive data from the server, could be a batch of messages
	irc_msgs = irc_blob.strip().split('\n')

	if irc_msgs:
		for msg_str in irc_msgs:
			msg_str = msg_str.strip()

			if msg_str:
				print("RECV: '" + msg_str + "'")  # Print what's coming from the server
				irc_msg = IrcMessage(msg_str)

				# Handle the general IRC message type
				if irc_msg.command == 'PRIVMSG':
					user_message = UserMessage(irc_msg)
					individual_words = user_message.body_lower.split()
					found_watch_word = find_watch_word_response(individual_words)
					# Respond to our watch words
					if found_watch_word:
						sendmsg(channel, found_watch_word)
					# respond to things directed at us
					elif user_message.body_lower.find(bot_nick.lower()) != -1:
						directed_response = find_directed_response(individual_words)
						if directed_response:
							sendmsg(channel, directed_response)
						# Greetings
						elif user_message.body_lower.find("hello") != -1 \
								or user_message.body_lower.find("hi") != -1 \
								or user_message.body_lower.find("yo") != -1:
							hello(user_message)
						# Soft quit
						elif user_message.body_lower.find("leave") != -1 and (user_message.name.lower() == "wavesonics" or user_message.name.lower() == "tinyonion"):
							if user_message.name.lower() == "tinyonion":
								sendmsg(channel, "Fiiiiine, but only because I like you")
							else:
								sendmsg(channel, "Good bye")
							print("I was told to leave")
							running = False
						# Random response
						else:
							respond_to_message(user_message, random.choice(common_responses))
					# A low random chance to say a common response
					elif random.randint(0, common_response_chance) == 1:
						sendmsg(channel, random.choice(common_responses))
					# A lower random chance to say something out of the blue
					elif random.randint(0, tid_bit_chance) == 1:
						sendmsg(channel, random.choice(tid_bits))
				elif irc_msg.command == 'NOTICE':
					# Handle the login & join sequence
					if irc_msg.source == 'NickServ!NickServ@snoonet/services/NickServ' \
							and irc_msg.params[0] == bot_nick \
							and irc_msg.body.find('nick') == 0:
						nick_auth()
					elif irc_msg.source == 'NickServ!NickServ@snoonet/services/NickServ' \
							and irc_msg.params[0] == bot_nick \
							and irc_msg.body.find('Password accepted') == 0:
						join_chan(channel)
				# Handle other general commands
				elif irc_msg.command == "PING":  # if the server pings us then we've got to respond!
					respond_to_ping(irc_msg)
				elif irc_msg.command == "ERROR":
					if irc_msg.body.find("Closing link:") != -1:
						print("Socket closed.")
						running = False
					else:
						print("Error!")
				else:
					print("Unhandled message type: " + irc_msg.command)

irc_sock.close()
