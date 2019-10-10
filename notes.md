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
- ?: split large messages into series (values, traces)
- Message length - limitation: possibly get the client to recieve parts of the message separately? (Or limit users per room, then add kicking)

## ROADMAP

Fri - delay next roll (in general and after err); roll decline send back (message); listbox

Future - Remove debug messages, artificial requests/messages, complete TODOs, move functionality appropriately, server-side timeout and override; user list selection
To decide - splitting
TESTING
https://www.youtube.com/watch?v=ULywIB97XfA LISTBOX

## Questions:
Config file? or arbitrary (strings?)
Documentation form (http://www.doxygen.nl/ + https://graphviz.org/ ?)
Hex validation or just allow strings? (value length validation?)
Server-side timeouts?
RDE for everyone? or what?

### Cons notes:
[x] user name change notification
[x] server DDOS protection (message buffer and outgoing message queue with delay) - 
queue per room
[x] chat message(s) concatenation
NOTE: The server can handle information at speeds that make sockets stop sending coherent messages; It is far greater than what a client can handle

![ ] contested state - out of scope. possibly halt the next roll / feature to get other users to save/submit their traces

[x] calculation: pseudorandom number generation w/ seed ; separate module ; API

[x] join newly/randomly created room (Login checkbox - create a new room)

[ ] potentially - only 'logout' permanently drops connection

[ ] DF key negotiation & symmetric encryption / Future: ring usage - In thesis: All messages go through the server, all protests might be ignored. Worth distributing the application completely to P2P
https://pycryptodome.readthedocs.io/en/latest/src/cipher/aes.html
https://www.josephrex.me/symmetric-encryption-in-python/
https://pl.wikipedia.org/wiki/Protok%C3%B3%C5%82_Diffiego-Hellmana
