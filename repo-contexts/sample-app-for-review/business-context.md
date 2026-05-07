# Business Context — sample-app-for-review

## Product

`sample-app-for-review` is the backend API for a B2B SaaS platform serving
enterprise HR and payroll management clients.

## Users

| Role            | Description |
|-----------------|-------------|
| Admin           | Full platform access; manages tenants and billing |
| HR Manager      | Manages employees, leave requests, and payroll runs |
| Employee        | Self-service portal: view payslips, submit leave |
| Auditor         | Read-only access to all records for compliance |

## Core Domains

1. **Employee Management** — CRUD on employee profiles, org chart
2. **Payroll Processing** — Monthly payroll runs, statutory deductions, payslips
3. **Leave Management** — Leave requests, approvals, balances
4. **Reporting** — Exportable compliance reports (XLSX, PDF)
5. **Authentication & RBAC** — Multi-tenant, role-based access control

## Compliance Requirements

- GDPR: Personal data must be encrypted at rest and in transit.
- SOC 2 Type II: All data access must be logged with user ID and timestamp.
- Data retention: Employee records retained for 7 years post-termination.

## SLAs

- API uptime: 99.9%
- P99 response time: < 500ms
- Payroll processing: Must complete within 30 minutes for up to 10,000 employees.

## Current Sprint Focus

- Completing payroll run approval workflow (US-101, US-102)
- Fixing leave balance calculation edge cases
- Adding audit log export feature

## Business Rules

- Payroll runs cannot be processed on weekends.
- Leave approval requires manager sign-off within 48 hours or auto-approves.
- Salary changes require dual approval (HR Manager + Admin).
