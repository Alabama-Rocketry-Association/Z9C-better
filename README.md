# Z9C-better
Zumlink Z9C radio with theading

Message Packet format

AAA{size} {message}

AAA denotes beginning of new packet
size denotes how long to read into the buffer
message is the binary string of the pickled python object
