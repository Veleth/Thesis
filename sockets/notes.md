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

### Server

- s.accept() waits for one last client before terminating the server

### Client
