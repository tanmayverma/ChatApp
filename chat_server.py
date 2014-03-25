# Tcp Chat server
 
import socket, select
 
#Function to broadcast chat messages to all connected clients
def broadcast_data (sock, message, room, blocked_by_list):
    #Do not send the message to master socket and the client who has send us the message
    for socket in CONNECTION_LIST.keys():
        if socket != server_socket and socket != sock :
		if(CONNECTION_LIST[socket]["state"] == "connected" and CONNECTION_LIST[socket].has_key("room")) :
			if CONNECTION_LIST[socket]["room"] == room and CONNECTION_LIST[socket]["name"] not in blocked_by_list:
				if(private_message(socket, message) == False):
					del CONNECTION_LIST[socket]

def private_message(socket, message):
            try :
                socket.send(message)
		return True
            except :
                # broken socket connection may be, chat client pressed ctrl+c for example
		cleanup(socket)
		return False

def cleanup(sock):
	if CONNECTION_LIST[sock].has_key("room"):
		room = CONNECTION_LIST[sock]["room"]
                broadcast_data(sock,"* user has left %s: %s\n" % (room,CONNECTION_LIST[sock]["name"]),room, [])
                del CONNECTION_LIST[sock]["room"]
                rooms[room] = rooms[room] - 1
	if CONNECTION_LIST[sock].has_key("name"):
        	del usernames[CONNECTION_LIST[sock]["name"]]
        sock.close()
        del CONNECTION_LIST[sock]
 
if __name__ == "__main__":
     
    # List to keep track of socket descriptors
    CONNECTION_LIST = {}
    RECV_BUFFER = 4096 # Advisable to keep it as an exponent of 2
    PORT = 5000

    usernames = {}
    rooms = {"chat":0}
     
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # this has no effect, why ?
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind(("0.0.0.0", PORT))
    server_socket.listen(10)
 
    # Add server socket to the list of readable connections
    CONNECTION_LIST[server_socket] = {"name": "server"}
 
    print "Chat server started on port " + str(PORT)
 
    while 1:
        # Get the list sockets which are ready to be read through select
        read_sockets,write_sockets,error_sockets = select.select(CONNECTION_LIST,[],[])
 
        for sock in read_sockets:
            #New connection
            if sock == server_socket:
                # Handle the case in which there is a new connection recieved through server_socket
                sockfd, addr = server_socket.accept()
		private_message(sockfd, "Welcome to Tanmay's Chatserver\nLogin Name?\n")
                CONNECTION_LIST[sockfd]={"state":"connecting"}
             
            #Some incoming message from a client
            else:
                # Data recieved from client, process it
                try:
                    #In Windows, sometimes when a TCP program closes abruptly,
                    # a "Connection reset by peer" exception will be thrown
                    data = sock.recv(RECV_BUFFER)
                    if data:
			if data.strip() == "/quit":
				if CONNECTION_LIST[sock].has_key("room"):
					room = CONNECTION_LIST[sock]["room"]
					broadcast_data(sock,"* user has left %s: %s\n" % (room,CONNECTION_LIST[sock]["name"]),room, [])
					private_message(sock,"* user has left %s: %s (** this is you)\n" % (room,CONNECTION_LIST[sock]["name"]))
					del CONNECTION_LIST[sock]["room"]
					rooms[room] = rooms[room] - 1
				private_message(sock, "BYE\n")
				if CONNECTION_LIST[sock].has_key("name"):
					del usernames[CONNECTION_LIST[sock]["name"]]
                   		sock.close()
				del CONNECTION_LIST[sock]
				continue

			if CONNECTION_LIST[sock]["state"] == "connecting":
				if(usernames.has_key(data)):
					private_message(sock, "Sorry, Name Taken\nLogin Name?\n")
				else:
					CONNECTION_LIST[sock]["name"] = data
					private_message(sock, "Welcome, %s!\n" % CONNECTION_LIST[sock]["name"])
					usernames[data] = 0
					CONNECTION_LIST[sock]["state"]="connected"
					CONNECTION_LIST[sock]["blocked_by"] = []
			elif CONNECTION_LIST[sock]["state"] == "connected":
				if data.strip().split()[0] == "/block":
					if len(data.strip().split())!=2:
						private_message(sock,"Usage: /block <name>\n")
						continue
					to_block = data.strip().split()[1]
					if to_block == CONNECTION_LIST[sock]["name"]:
						private_message(sock,"Sorry! You can't block/unblock yourself\n")
                                                continue
					if usernames.has_key(to_block):
						for user in CONNECTION_LIST.keys():
							if CONNECTION_LIST[user]["name"] == to_block:
								if CONNECTION_LIST[sock]["name"] not in CONNECTION_LIST[user]["blocked_by"]:
									CONNECTION_LIST[user]["blocked_by"].append(CONNECTION_LIST[sock]["name"])
									private_message(sock,"%s has been blocked! To unblock use the following command /unblock <name>\n" % to_block)
								else:
									private_message(sock,"%s has been blocked by you already! To unblock use the following command /unblock <name>\n" % to_block)
								break
						continue
					else:
						private_message(sock,"No user with the name %s\n" % to_block)
						continue
				if data.strip().split()[0] == "/unblock":
					if len(data.strip().split())!=2:
                                                private_message(sock,"Usage: /unblock <name>\n")
                                                continue
					to_unblock = data.strip().split()[1]
					if to_unblock == CONNECTION_LIST[sock]["name"]:
                                                private_message(sock,"Sorry! You can't block/unblock yourself\n")
                                                continue
					if usernames.has_key(to_unblock):
                                                for user in CONNECTION_LIST.keys():
                                                        if CONNECTION_LIST[user]["name"] == to_unblock:
								if CONNECTION_LIST[sock]["name"] in CONNECTION_LIST[user]["blocked_by"]:
                                                                	CONNECTION_LIST[user]["blocked_by"].remove(CONNECTION_LIST[sock]["name"])
                                                                	private_message(sock,"%s has been unblocked! To block use the following command /block <name>\n" % to_unblock)
                                                                	break
								else:
									private_message(sock,"%s hasn't been blocked by you! To block use the following command /block <name>\n" % to_unblock)
                                                                        break
                                                continue
                                        else:
                                                private_message(sock,"No user with the name %s\n" % to_block)
                                                continue
				if data.strip().split()[0] == "/message":
					if len(data.strip().split())<3:
                                                private_message(sock,"Usage: /message <user> <text>\n")
                                                continue
					reciever = data.strip().split()[1]
					if reciever == CONNECTION_LIST[sock]["name"]:
                                                private_message(sock,"Sorry! You can't message yourself\n")
                                                continue
					if usernames.has_key(reciever):
                                                for user in CONNECTION_LIST.keys():
                                                        if CONNECTION_LIST[user]["name"] == reciever:
                                                                if CONNECTION_LIST[user]["name"] not in CONNECTION_LIST[sock]["blocked_by"]:
									message = "Private Message from %s:" % CONNECTION_LIST[sock]["name"]
                                                                        private_message(user,"Private Message from %s: %s\n" % (CONNECTION_LIST[sock]["name"]," ".join(data.strip().split()[2:])))
                                                                else:
                                                                        private_message(sock,"%s has blocked you!\n" % reciever)
                                                                break
                                                continue
                                        else:
                                                private_message(sock,"No user with the name %s\n" % reciever)
                                                continue

						 
				if CONNECTION_LIST[sock].has_key("room"):
					if data.strip() == "/leave":
						room = CONNECTION_LIST[sock]["room"]
						broadcast_data(sock,"* user has left %s: %s\n" % (room,CONNECTION_LIST[sock]["name"]),room, [])
						private_message(sock,"* user has left %s: %s (** this is you)\n" % (room,CONNECTION_LIST[sock]["name"]))
						del CONNECTION_LIST[sock]["room"]
						rooms[room] = rooms[room] - 1	
					else: 
                        			broadcast_data(server_socket, "%s: %s\n" % (CONNECTION_LIST[sock]["name"], data),CONNECTION_LIST[sock]["room"], CONNECTION_LIST[sock]["blocked_by"] )
				else:
					if data.strip() == "/rooms":
						reply = 'Active rooms are:\n'
						for room in rooms.keys():
							reply = reply + "* " + room + " (" + str(rooms[room]) +  ")\n" 
						reply = reply + "end of list.\n"
						private_message(sock, reply)
					elif data.strip().split()[0] == "/join":
						room = data.strip().split()[1]
						if rooms.has_key(room):
							private_message(sock, "entering room: %s\n" % room )
							CONNECTION_LIST[sock]["room"] = room
							rooms[room] = rooms[room] + 1
							users = ""
							for user in CONNECTION_LIST.keys():
								if CONNECTION_LIST[user].has_key("name") and CONNECTION_LIST[user].has_key("room"):
									if(CONNECTION_LIST[user]["room"] == room):
										if user == sock:
											users = users + "* %s (** this is you)\n" % CONNECTION_LIST[user]["name"]
										else:
											users = users + "* %s\n" % CONNECTION_LIST[user]["name"]
                                                	users = users + "end of list.\n"
							private_message(sock, users)
							broadcast_data(sock,"* new user joined chat: %s\n" % CONNECTION_LIST[sock]["name"], room, [])
						else:
							rooms[room] = 1
							CONNECTION_LIST[sock]["room"] = room
                except:
			cleanup(sock)
                        continue
     
    server_socket.close()
