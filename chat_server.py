# Tcp Chat server
 
import socket, select
 
#Function to broadcast chat messages to all connected clients
def broadcast_data (sock, message, room):
    #Do not send the message to master socket and the client who has send us the message
    for socket in CONNECTION_LIST.keys():
        if socket != server_socket and socket != sock :
		if(CONNECTION_LIST[socket]["state"] == "connected" and CONNECTION_LIST[socket].has_key("room")) :
			if CONNECTION_LIST[socket]["room"] == room:
				if(private_message(socket, message) == False):
					del CONNECTION_LIST[socket]

def private_message(socket, message):
            try :
                socket.send(message)
		return True
            except :
                # broken socket connection may be, chat client pressed ctrl+c for example
                socket.close()
		return False
 
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
		#print sockfd
                #print "Client (%s, %s) connected" % addr
                #broadcast_data(sockfd, "[%s:%s] entered room\n" % addr)
             
            #Some incoming message from a client
            else:
                # Data recieved from client, process it
                #try:
                    #In Windows, sometimes when a TCP program closes abruptly,
                    # a "Connection reset by peer" exception will be thrown
                    data = sock.recv(RECV_BUFFER)
                    if data:
			if data.strip() == "/quit":
				if CONNECTION_LIST[sock].has_key("room"):
					room = CONNECTION_LIST[sock]["room"]
					broadcast_data(sock,"* user has left %s: %s\n" % (room,CONNECTION_LIST[sock]["name"]),room)
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
			elif CONNECTION_LIST[sock]["state"] == "connected":
				if CONNECTION_LIST[sock].has_key("room"):
					if data.strip() == "/leave":
						room = CONNECTION_LIST[sock]["room"]
						broadcast_data(sock,"* user has left %s: %s\n" % (room,CONNECTION_LIST[sock]["name"]),room)
						private_message(sock,"* user has left %s: %s (** this is you)\n" % (room,CONNECTION_LIST[sock]["name"]))
						del CONNECTION_LIST[sock]["room"]
						rooms[room] = rooms[room] - 1	
					else: 
                        			broadcast_data(server_socket, "%s: %s\n" % (CONNECTION_LIST[sock]["name"], data),CONNECTION_LIST[sock]["room"])
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
							broadcast_data(sock,"* new user joined chat: %s\n" % CONNECTION_LIST[sock]["name"], room)
						else:
							rooms[room] = 1
							CONNECTION_LIST[sock]["room"] = room
                #except:
                   # broadcast_data(sock, "Client (%s, %s) is offline" % addr)
                   # print "Client (%s, %s) is offline" % addr
                   # sock.close()
                   # del CONNECTION_LIST[sock]
                   # continue
     
    server_socket.close()
