# BSc Thesis notes
https://www.youtube.com/watch?v=D8-snVfekto for layout

- Server command to get logs and check (add server room to logs)
- Optional: Dummies and unit testing
- Polish: User name / room collision (init fault?)
- Polish: commands (!roll !)
- Optional: Add contest option and contested room state if something goes wrong

GUI: Player list and command buttons
Client-side command validation

Late messages(after timeout) - solution: states ?
Server exception handling

IMPERATIVE: split large messages into series
Message length - limitation: possibly get the client to recieve parts of the message separately?
Dropout - what if first, what if middle, what if last? What if GM?

## ROADMAP:
Mon - GM dropout, roll invocation function, input validation on login screen (with prompts)
Tue - user list selection?