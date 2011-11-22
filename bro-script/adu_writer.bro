@load adu

global clientfd: file;
global serverfd: file;

event bro_init()
{
	clientfd = open("adu_blocks_client");
	serverfd = open("adu_blocks_server");
}

event bro_done()
{
	close(clientfd);
	close(serverfd);
}

event adu_tx(c:connection, astate: adu::adu_state)
{
	local mess = fmt("%s", astate$adu);
	print clientfd, fmt("****************************************** %s %d %d %s", c$uid, astate$seen_adu_tx, byte_len(mess), mess);
}

event adu_rx(c: connection, astate: adu::adu_state)
{
	local mess = fmt("%s", astate$adu);
	print serverfd, fmt("****************************************** %s %d %d %s", c$uid, astate$seen_adu_rx, byte_len(mess), mess);
}


