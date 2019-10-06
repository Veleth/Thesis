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
Sun - roll with user subset (Server), user roll and command area improvement (client), client logout and connection drop, GM leave info for players

Ahead:
Mon - TO CONFIRM: trace gathering (server/client), trace displaying, trace order, contested state & popup; server-side timeout and override
Tue - 
Wed - 
Future - Remove debug messages, artificial requests/messages, complete TODOs, move functionality appropriately
To decide - user list selection, splitting


## Questions:
Neceessary?: split large messages into series
User selection (for the roll) (list? etc)
Calculation algorithm
Encoding / encrypting
Reconnects?
What if wrong result/input not included? (anything more than a message?)
