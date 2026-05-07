# Architecture

This project follows a service-layer architecture.

Rules:
- Route files must not directly access databases
- Business logic should remain inside services
- Middleware handles authentication and authorization
- Authentication uses JWT tokens
- Input validation is mandatory for all APIs