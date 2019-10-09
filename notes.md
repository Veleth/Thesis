# BSc Thesis notes
https://www.youtube.com/watch?v=D8-snVfekto for layout
http://zetcode.com/tkinter/menustoolbars/ for menu

- Polish: roll with user subset
- Polish: login screen remember choice
- Optional: Add contest option and contested room state if something goes wrong
- Code polishing: unify names to use camelcase in gui/client/server/room/user
- Client-side command validation
- Late messages(after timeout) - solution: states ?
- Server exception handling
- server-side timeout
- Client exception handle on leave
- IMPERATIVE: split large messages into series (values, traces)
- Message length - limitation: possibly get the client to recieve parts of the message separately? (Or limit users per room, then add kicking)

## ROADMAP

Wed - 1-3 from the list, exit button fix; server-side incoming message buffer;
5-6 from the list;
Thu - trace gathering (server/client), trace displaying, trace order, ; server-side timeout and override; partially 4 from the list
Fri - trace save popup and signal; delay next roll; roll decline send back (message); append file

Future - Remove debug messages, artificial requests/messages, complete TODOs, move functionality appropriately
To decide - user list selection, splitting


## Questions:
Config file? or arbitrary (strings?)

### Cons notes:
[x] user name change notification
[x] server DDOS protection (message buffer and outgoing message queue with delay) - 
queue per room
[x] chat message(s) concatenation
NOTE: The server can handle information at speeds that make sockets stop sending coherent messages; It is far greater than what a client can handle

[ ] contested state - out of scope. possibly halt the next roll / feature to get other users to save/submit their traces

[x] calculation: pseudorandom number generation w/ seed ; separate module ; API

[x] join newly/randomly created room (Login checkbox - create a new room)

[ ] potentially - only 'logout' permanently drops connection

[ ] DF key negotiation & symmetric encryption / Future: ring usage - In thesis: All messages go through the server, all protests might be ignored. Worth distributing the application completely to P2P
