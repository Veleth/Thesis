# BSc Thesis notes
https://www.youtube.com/watch?v=D8-snVfekto for layout
http://zetcode.com/tkinter/menustoolbars/ for menu
https://realpython.com/python-sockets/#echo-client-and-server basic client server
http://www.science.smith.edu/dftwiki/index.php/Color_Charts_for_TKinter colors in TKinter

Libs : pip install pycryptodome pyDHE
Crypto-1.4.1 Naked-0.1.31 pyDHE-1.0.0 pyyaml-5.1.2 shellescape-3.4.1
pycryptodome-3.9.0

TO-DOs:
- Config in config file
- (Optional) Dark mode
TESTING

## ROADMAP
soon - dark mode; https://coolors.co/95a3a4-b7d1da-424f6b-fdfffc-1c1c1c

Future - Remove debug messages, artificial requests/messages, complete TODOs, server-side timeout and override;, salt - ip+port
TESTING
https://www.youtube.com/watch?v=ULywIB97XfA LISTBOX

## Questions:
Config file? or arbitrary (strings?)
Documentation form (http://www.doxygen.nl/ + https://graphviz.org/ ?) - function headers, parameters, functionality, return

RDE for everyone? or what?

Bibliography? Documentation?
DH key exchange
Salsa
AES - why not used (block cipher)
P2P, socket reference
Introduction: small modular reminders of what's used and how it works
Distributed generating pseudorandom numbers, why this particular method chosen.
MPC- why not used 
Lib documentation, references
webpages - time of access
Appendix - summary in Polish (what the plan was / combine introduction and summary, what was done, what can be improved, how it works); 20-30pages 50-60 upper limit. Thesis should be exhaustive.

Language? Front page?
count per chapter or subchapter?

debugging; testing (vega/skipfish for security)
buffer overflow;

grading sheet - faculty website/prof. Cichon
not too many UML - flowchart better
emphasis on important stuff i.e. safe generation etc


### Questions Vol. 2:
How to link appendices?

What to keep in the introduction, what to keep in case study?
Repetitions will happen.

Communication/message examples - how to show them?

Header/message detailed examples? Listing?
one example ok, details can be included in appendices

Paper deadline? 
2 jan.

Code deadline?
same, everything is submitted; appropriate size and name; check every char of the thesis title

Code submission?
ASAP

Code/paper changes after submission?
No changes in ASAP, .zip is sent.

Doxygen docstrings or not?


MSc studies - 

Code testing? Vega/skipfish have other uses than http servers?

### Questions vol. 3:

- TikZ arrows

#### Testing:

Write - every module was tested, how, which assertions were proven.
Show that functional requirements were met.
How disconnections/hotjoins are handled - test or prove, for example clone and modify app.

- Include in code?
No

- What to check/unit test?
Has to be anything. Monte Carlo cool, for example 30 trials in which a random number > 1 disconnected.
Not formally, but prove that functional requirements were met.

- How to time rolls?
Graph, start->get result, for GM only sum time to compute and time to fetch result, for multiple users time the process.

Sender + matplotlib on the server.

- How to simulate heavy loads?
Execute:

Describe:

- How to test drop ins/ drop outs?
Execute:

Describe:

- Type Errors and Buffer overflow - which functionalities? How?
Load balancing and buffer overlow (Describe that the interpreter is resistant)

Test or check?


Diagrams? Colors, style, info?
Leave out complicated stuff, describe in caption
Simple scheme

Presentation? SD?
10 min theoretically, little shorter is ok, little longer might be problematic. 8-12 slides most likely. What is the goal, motivation etc. Case analysis, what the problem is, 
known solutions (MPC, Homomorphic encryption - dangerous because there can be questions). Later the solution - flow chart (screenshots no), later tests, summary - what was done,
 what wasn't done, what can be added in the future, what is the biggest pride, etc.

Key: distributed system, sell the generation and verification (and explain further)

Always in Polish, presentation can be in English. Beamer.
Refrain from low-contrast light colors.


Teoretycznie 10 minut, odrobinę krótsze - ok. Odrobinę dłuższe może być przerwane. Około 8-12 slajdów. Opisać cel, motywacje, itp. Case study, opis problemu, dostepne rozwiązania.
Później opis rozwiązania, flow chart spoko, bez screenshotów. Następnie testy, podsumowanie - co zostało zrobione, co nie zostało zrobione, najfajniejsze elementy, coś z czego jest się dumnym,
potencjał na rozwój w przyszłości itp.
Sprzedać kluczowe części (w moim przypadku generacja i weryfikacja). Te elementy można opisać dokładniej, reszta ogółami bo jest mało czasu.
Prezentacja może być w dowolnej formie, ale do beamera nikt się nie przyczepi. Przy jasnych kolorach unikać niskiego kontrastu.

### Notes (2):
Case study - mention that all commits are sent by the users before being sent to them and why one user's input is essentially random
End problem overview after 3 paragraphs, include `building blocks` paragraph or a couple, and add `possible solutions` subsection

Don't be afraid of long captions in flowcharts, describe images in the text (tikz)

CD contents - first appendix - pdf file with the thesis, source codes + documentation (where)
### Cons notes:
[x] user name change notification
[x] server DDOS protection (message buffer and outgoing message queue with delay)
queue per room
[x] chat message(s) concatenation
NOTE: The server can handle information at speeds that make sockets stop sending coherent messages; It is far greater than what a client can handle

[x] calculation: pseudorandom number generation w/ seed ; separate module ; API

[x] join newly/randomly created room (Login checkbox - create a new room)

[x] DF key negotiation & symmetric encryption / Future: ring usage - In thesis: All messages go through the server, all protests might be ignored. Worth distributing the application completely to P2P
https://pycryptodome.readthedocs.io/en/latest/src/cipher/aes.html
https://www.josephrex.me/symmetric-encryption-in-python/
https://pl.wikipedia.org/wiki/Protok%C3%B3%C5%82_Diffiego-Hellmana


[x] server-side validation of user login data (size)
