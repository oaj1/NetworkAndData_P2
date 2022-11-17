from tkinter import *
import tkinter
import os
import tkinter.messagebox

import socket
import pickle
import random
import time
import os

# Authors: Ben Platt, Oliver James, Mark Ross, Raymond Johnson
# COSC: 635 Network and Data 1
# Professor X. David Zheng
# Last Updated: 11/17/2022

# This program is a Graphical User Interface (GUI) that combines all of our implementations of the
# Stop-And-Wait (SAW) and Go-Back-N (GBN) flow control mechanisms. The user can use our GUI to send a data file
# called "COSC635_P2_DataSent.txt" to another computer over the internet with simulated packet loss. The UDP channel is used
# for communications. The flow control mechanisms will ensure that errors are minimal. Basic statistics are
# displayed on the sender side after the file transfer is completed.

window = tkinter.Tk()
window.title("COSC635 Project GUI")
window.geometry("300x300")
menu = Menu(window)
from tkinter import messagebox
# define input 



def sawReceive():
    #os.system('python3 SAW_Receiver.py') # replace with actual code
    # ------------------------------------------ STEP 0: DECLARATIONS (depends on the protocol that we design) ------------------------------------------
    # addresses
    receiver_ip = socket.gethostbyname(socket.gethostname())
    port = 5051
    receiver_addr = (receiver_ip, port)

    sender_port = 15200
    sender_ip = socket.gethostbyname(socket.gethostname())
    sender_addr = (sender_ip, sender_port)

    # socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    # need to bind so we can receive data
    sock.bind(receiver_addr)
    # timeout is 10s for now so user can input something at the beginning of sender code
    sock.settimeout(100)

    # protocols
    buff_size = 1300

    # data stuff
    # this is the message indicating to stop waiting for data.
    kill_conn_message = "FINISH"
    # this is where we'll put all the decoded data that we receive
    file_data = []
    filename = "COSC635_P2_DataReceived.txt"

    print("Awaiting data on:", receiver_addr)

    # ------------------------------------------ STEP 1: RECEIVING THE DATA ------------------------------------------
    transmission_start = False
    start_receive = False

    while True:
        # receive the data
        data, sender_addr = sock.recvfrom(buff_size)

        # lets user know that data is being received
        if transmission_start is False:
            print("Receiving data...")
            transmission_start = True

        if start_receive is False and data is not None:
            start_receive = True
            sock.settimeout(5)

        # unpack the data
        data_received_list = pickle.loads(data)

        # length of data received
        data_received_len = data_received_list[0]

        # decode the packet and send to the list
        message = data_received_list[1]
        # print(message)

        # SEQ number
        SEQ = data_received_list[2]

        # if the message is the "kill connection" message then break the loop, we are done
        if message == kill_conn_message:
            break

        # otherwise, add the data to the list
        file_data.append(message)


        # prepare the ACK and send it
        ACK = (SEQ + 1) % 2

        ack_length = len(b'ACK')

        response_list = [ack_length, ACK]
        response = pickle.dumps(response_list)

        try:
            sock.sendto(response, sender_addr)
        except socket.timeout:
            print("Uh oh! Disconnected from the sender")

    print("Data has been received...")
    # ------------------------------------------ STEP 1: RECEIVING THE DATA ------------------------------------------

    print("writing the data to a file called", filename)

    # creates the new file within the project directory if it doesn't already exist
    # append the file by writing all the data received to it
    file = open(filename, "a")
    for data in file_data:
        file.write(data)
    file.close()

    print("file has been created and written to! Check your directory for", filename)
    # maybe give the user an option to read the data? idk, we can just open the txt file from the directory after this.
    
def sawSend(): # pass input variable for packet loss
    #os.system('python3 SAW_Sender.py') # replace with actual code
    root = tkinter.Tk()
    root.geometry("300x300")
    #Label(window, text="Enter Number Between 0 and 99, for Packet Loss: ", font=('Calibri 10')).pack()


    def num():
        user = e.get()
        user = int(user)
        seed = user
        #print(type(seed))
        #print(seed)

        receiver_ip = socket.gethostbyname(socket.gethostname())
        receiver_port = 5051
        receiver_addr = (receiver_ip, receiver_port)

        sender_port = 15200
        sender_ip = socket.gethostbyname(socket.gethostname())
        sender_addr = (sender_ip, sender_port)

        # socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        # need to bind so we can receive ACK
        sock.bind(sender_addr)
        sock.settimeout(5)

        buff_size = 1300
        # this is minimum payload_size. The number of bytes from the file that we want to send at one time. Note: 1 byte = 1 char.
        # setting this as 8 for now
        payload_size = 8

        # data - gonna put all of the packets we want to send into a list so that we
        # can just iterate through the list to send everything in order
        #
        # header changes with each packet so we can just do something like header = SEQ = index of data in list % 2
        # (will be either 0 or 1)
        packets = []
        # name of the file to be sent, should be located within the project directory so we don't have to navigate to it.
        #filename = "../../../Downloads/COSC635_P2_DataSent.txt"
        filename ="COSC635_P2_DataSent.txt"

        # Statistic data
        # total frames sent
        frames_sent = 0
        # total frames lost
        frames_lost = 0
        # size of file in bytes
        file_size = os.path.getsize(filename)

        # ------------------------------------------ STEP 1: DEALING WITH THE FILE ------------------------------------------
        # this step deals with: Open the file, read the file, add encoded (utf-8) bytes into the packets list


        # tell the user that the file is being read
        print("parsing the file...")

        # open file, r is the mode to open the file in. All the resources I looked at used r.
        file = open(filename, "r")

        # iterate over file (character by character) and add the encoded strings to the packets list
        # I think this should work as expected but not 100%. Not sure if it breaks out of while loop correctly.
        while 1:
            payload = ""
            char = ''
            # read in a payloads worth of chars
            for i in range(payload_size):
                # read 1 character
                char = file.read(1)
                if not char:
                    break
                # concatenate char to decoded payload
                payload += char
            # encodes in utf-8 by default
            # payload_encoded = payload_decoded.encode()
            packets.append(payload)
            # breaks while loop if no char stored from for loop
            if not char:
                break
        file.close()

        # last step for this part: add some "kill connection" message to the file data so the
        # while loop on the sender side doesn't keep waiting for data
        kill_conn_message = "FINISH"
        packets.append(kill_conn_message)

        print("parsing complete!")

        print("sending the data...")

        # data_length is the total number of "frames" that are being sent, doesn't change throughout the loop, only declare once
        data_length = len(packets)

        start = time.perf_counter()
        for i in range(len(packets)):
            # packet to be sent
            data = packets[i]

            # -------- Simulated packet loss --------
            random_number = random.randint(0, 99)
            if random_number < seed:
                frames_lost += 1
                # shouldn't actually "lose" the packet, just include it in the statistics
                # continue

            # figure out what the SEQ should be (0 for even items, 1 for odd items)
            SEQ = i % 2
            expected_ACK = (SEQ + 1) % 2

            # udp_header = [source_port, destination_port, total_length] CAN'T USE STRUCTS WITH LISTS, need to just
            # put all the individual items into the struct

            # prepare the header and the packet to be sent.
            # sending a list containing the relevant information
            # can send it with udp thanks to a library called "pickle" pickle.dumps(list) turns a
            # list into a byte representation that can be sent using udp methods. MUCH easier than using structs as I did previously
            data_list = [data_length, data, SEQ]
            data_to_send = pickle.dumps(data_list)

            # put the communications into a try except block
            try:
                # send the data and add statistic data
                sock.sendto(data_to_send, receiver_addr)
                frames_sent += 1

                # *********** NOT SURE ABOUT THIS LINE: if this was the last message, don't wait for ack, just kill connection ***********
                if packets[i] == kill_conn_message:
                    break

                # wait for ACK before proceeding, separate
                while True:
                    data_received, addr_received = sock.recvfrom(buff_size)
                    # load the list of data received
                    data_rec_list = pickle.loads(data_received)
                    data_rec_len = data_rec_list[0]
                    ACK_received = data_rec_list[1]
                    if ACK_received is expected_ACK:
                        # print("going next")
                        # send next packet
                        break
                    else:
                        print("I've received an unexpected ACK... trying again")
                        # not expected, try again
                        i -= 1
                    # no ACK, try iteration again
                    # run this iteration of the loop again
            except socket.timeout:
                print("timeout error")
                i -= 1
        stop = time.perf_counter()
        print("data has been sent!")


        # transmission time
        transmission_time = stop-start
        # percentage of lost frames
        if frames_sent > 0:
            loss_percent = (frames_lost/frames_sent)*100
        else:
            loss_percent = 100

        print("-------------------")
        print("")
        print("Transmission Statistics")
        print("")
        print("Transmission time: ", transmission_time, "seconds")
        print("File Size:", file_size, "bytes")
        print("Total frames in file:", data_length)
        print("Total frames sent:", frames_sent)
        print("Total frames 'lost' (simulated):", frames_lost)
        print("Percentage of lost frames:", loss_percent, "%")
        print("")
        print("-------------------")


    e = Entry(root)
    e.pack()
    b = Button(root, text= "Packet Loss, Between 0-99", command=num )
    b.pack()

    

def gbnReceive():
    #os.system('python3 GBN_receiver.py') # replace with actual code
    # ------------------------------------------ STEP 0: DECLARATIONS (depends on the protocol that we design) ------------------------------------------
    # addresses
    receiver_ip = socket.gethostbyname(socket.gethostname())
    port = 5051
    receiver_addr = (receiver_ip, port)

    sender_port = 15200
    sender_ip = socket.gethostbyname(socket.gethostname())
    sender_addr = (sender_ip, sender_port)

    # socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    # need to bind so we can receive data
    sock.bind(receiver_addr)
    # timeout is 100s until data is being received. This allows sender to run code and enter input.
    sock.settimeout(100)
    start_receive = False

    # protocols
    buff_size = 1300

    # data stuff
    # this is the message indicating to stop waiting for data.
    kill_conn_message = "FINISH"
    # this is where we'll put all the decoded data that we receive
    file_data = []
    filename = "COSC635_P2_DataReceived.txt"

    print("Awaiting data on:", receiver_addr)

    # ------------------------------------------ STEP 1: RECEIVING THE DATA ------------------------------------------
    nextseqnum = 0
    max_data = None
    while True:
        # these lines let it know when to stop trying to receive
        if max_data is not None:
            if max_data == nextseqnum:
                break
        try:
            # receive the data
            data, sender_addr = sock.recvfrom(buff_size)

            # fix timeout
            if start_receive is False and data is not None:
                print("Begun receiving data...")
                sock.settimeout(2)
                start_receive = True

            # unpack data
            data_rec = pickle.loads(data)
            max_data = data_rec[0]#length of data received

            if data_rec[1] == nextseqnum: 
                file_data.append(data_rec[2]) 
                data_list = [1, nextseqnum]
                data_to_send = pickle.dumps(data_list)
                sock.sendto(data_to_send, sender_addr)
                nextseqnum += 1
            else:
                data_list = [0, nextseqnum]
                data_to_send = pickle.dumps(data_list)
                sock.sendto(data_to_send, sender_addr)

        except socket.timeout:
            continue
    print("Data has been received...")
    # ------------------------------------------ STEP 1: RECEIVING THE DATA ------------------------------------------

    print("writing the data to a file called", filename)

    # creates the new file within the project directory if it doesn't already exist
    # append the file by writing all the data received to it
    file = open(filename, "a")
    for data in file_data:
        file.write(data)
    file.close()

    print("file has been created and written to! Check your directory for", filename)
    
def gbnSend(): # pass input variable for packet loss
    #os.system('python3 gbns.py') # replace with actual code
    root = tkinter.Tk()
    root.geometry("300x300")
    #Label(window, text="Enter Number Between 0 and 99, for Packet Loss: ", font=('Calibri 10')).pack()
    def num():
        user = e.get()
        user = int(user)
        seed = user
        print(type(seed))
        print(seed)

        # addresses
        # both are this local machine for now
        # using different ports for send and receive, can't be listening on same port
        # receiver_ip = "192.168.1.201"
        receiver_ip = socket.gethostbyname(socket.gethostname())
        receiver_port = 5051
        receiver_addr = (receiver_ip, receiver_port)

        sender_port = 15200
        sender_ip = socket.gethostbyname(socket.gethostname())
        sender_addr = (sender_ip, sender_port)

        # socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        # need to bind so we can receive ACK
        sock.bind(sender_addr)
        # doing 2 second timeout here since the code relies on the timeout
        sock.settimeout(2)

        # protocols
        window_size = 7
        buff_size = 1300 * window_size
        # this is minimum payload_size. The number of bytes from the file that we want to send at one time. Note: 1 byte = 1 char.
        # setting this as 8 for now
        payload_size = 8

        # data - gonna put all of the packets we want to send into a list so that we
        # can just iterate through the list to send everything in order
        #
        # header changes with each packet so we can just do something like header = SEQ = index of data in list % 2
        # (will be either 0 or 1)
        packets = []
        # name of the file to be sent, should be located within the project directory so we don't have to navigate to it.
        #filename = "../../../Downloads/COSC635_P2_DataSent.txt"
        filename = "COSC635_P2_DataSent.txt"

        # Statistic data
        # total frames sent
        frames_sent = 0
        # total frames lost
        frames_lost = 0
        # size of file in bytes
        file_size = os.path.getsize(filename)

        # ------------------------------------------ STEP 1: DEALING WITH THE FILE ------------------------------------------
        # this step deals with: Open the file, read the file, add encoded (utf-8) bytes into the packets list


        # tell the user that the file is being read
        print("parsing the file...")

        # open file, r is the mode to open the file in. All the resources I looked at used r.
        file = open(filename, "r")

        # iterate over file (character by character) and add the encoded strings to the packets list
        # I think this should work as expected but not 100%. Not sure if it breaks out of while loop correctly.
        while 1:
            payload = ""
            char = ''
            # read in a payloads worth of chars
            for i in range(payload_size):
                # read 1 character
                char = file.read(1)
                if not char:
                    break
                # concatenate char to decoded payload
                payload += char
            # encodes in utf-8 by default
            # payload_encoded = payload_decoded.encode()
            packets.append(payload)
            # breaks while loop if no char stored from for loop
            if not char:
                break
        file.close()

        # No need for kill_conn_message on this one, that's done by "max_data"

        print("parsing complete!")

        # ------------------------------------------ STEP 2: SEND THE DATA ------------------------------------------

        print("sending the data...")

        # data_length is the total number of "frames" that are being sent, doesn't change throughout the loop, only declare once
        max_data = len(packets)

        #start the timer
        start = time.perf_counter()
        send_base = 0
        nextseqnum = 0
        while nextseqnum < max_data:
            skip = False
            try:
                # -------- Simulated packet loss --------
                random_number = random.randint(0, 99)
                if random_number < seed:
                    # packet isn't actually being "lost" so this code needs to be commented out
                    # data_list = [max_data, nextseqnum, ""]
                    # data_to_send = pickle.dumps(data_list)
                    # sock.sendto(data_to_send, receiver_addr)
                    skip = True

                # try to send data
                # if packet is being "lost" then only do this if skip = False
                if nextseqnum < send_base + window_size:
                    data_list = [max_data, nextseqnum, packets[nextseqnum]]#can you explain why packets[nextseqnum]? I'm imagining that is because that would be the index to send for the packet list?
                    data_to_send = pickle.dumps(data_list)
                    sock.sendto(data_to_send, receiver_addr)
                    nextseqnum += 1

                # try to receive data
                data, sender_addr = sock.recvfrom(buff_size)
                if data is not None:
                    data_rec = pickle.loads(data) 
                    if data_rec[0] == 1:
                        if data_rec[1] == send_base:
                            send_base += 1
                            if skip is False:
                                frames_sent += 1
                            else:
                                frames_lost += 1
                        else:
                            # wait for timeout, this isn't the ACK for the SEQ we expected
                            # frames_lost += 1
                            time.sleep(2)
                else:
                    # wait for timeout, we got a rejected ACK
                    # frames_lost += 1
                    time.sleep(2)
            # timeout means that we need to go back and resend certain packets
            except socket.timeout:
                # send all packets again
                nextseqnum = send_base
                # frames_sent = send_base
                continue


        stop = time.perf_counter()
        print("data has been sent!")

        # ------------------------------------------ STEP 3: DISPLAY STATISTICS ------------------------------------------
        # transmission time
        transmission_time = stop-start
        # percentage of lost frames
        if max_data > 0:
            loss_percent = (frames_lost/max_data)*100
        else:
            loss_percent = 100

        print("-------------------")
        print("")
        print("Transmission Statistics")
        print("")
        print("Transmission time: ", transmission_time, "seconds")
        print("File Size:", file_size, "bytes")
        print("Total frames in file:", max_data)
        print("Total frames sent:", frames_sent)
        print("Total frames 'lost' (simulated):", frames_lost)
        print("Percentage of lost frames:", loss_percent, "%")
        print("")
        print("-------------------")
    e = Entry(root)
    e.pack()
    b = Button(root, text= "Packet Loss, Between 0-99", command=num )
    b.pack()


    def num():
        user = e.get()
        user = int(user)
        seed = user
        #print(type(seed))
        #print(seed)
    

def instructions():
    instruction = "Select the Desired Protocol and transmission role.  If sending to yourself on the same computer you need to open a separate send/receive window for each transmission direction!"
    tkinter.messagebox.showinfo(title='Help', message=instruction)


window.config(menu=menu)
filemenu = Menu(menu)
menu.add_cascade(label='Protocols', menu=filemenu)
filemenu.add_command(label="Stop and Wait Send", command=sawSend)
filemenu.add_command(label="Stop and Wait Receive", command=sawReceive)
filemenu.add_command(label="Go-back-N Send", command=gbnSend)
filemenu.add_command(label="Go-back-N Receive", command=gbnReceive)

filemenu.add_separator()
filemenu.add_command(label='Exit', command=window.quit)
helpmenu = Menu(menu)
menu.add_cascade(label="Help", menu=helpmenu)
helpmenu.add_command(label='Instructions', command=instructions)


window.mainloop()
