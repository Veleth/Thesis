# BSc Thesis notes

## To - dos

- Client/server comms: dual-thread operation. A dedicated listener thread in each client and sender loop (Observer pattern?)
- Server waiting for response
- Client able to send from stdin
- Introduce communication + protocol
- Tunnel comms
- Prepare rooms
- Prepare GMs
- Prepare commands
- Client: stdin validation
- Client: Calculation trace logging
- Server command to get logs and check
- Optional: HTTP client as well
- Optional: Dummies and unit testing
- User name / room collision

## Things to keep in mind/clarify later

### Communication

- The comms have to be organized as follows:
  - Server : receiving loop which can analyze and send
  (individual client)
  - Server : sending functionality that can target any user/room (general)
  - Client : receiving loop which prints to stdout/invokes some action ( threaded/timed?)

### Server

- s.accept() waits for one last client before terminating the server

### Client
