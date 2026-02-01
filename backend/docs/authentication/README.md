# Authentication System

This document describes the lightweight mobile + password authentication added to the
Patient & Hospital Copilot backend.

## Overview
- Auth is based on a single `accounts` table keyed by `role` + `mobile`.
- Passwords are stored as PBKDF2 hashes (SHA-256) with a per-user salt.
- Patients can create an account during patient creation by including `mobile` and `password`.
- Doctors and hospitals can log in if an account exists for their role.

## Endpoints
Base URL: `/api/v1/auth`

### Patient login
`POST /patients/login`

Request:
```json
{"mobile": "+1 555 123 4567", "password": "secret"}
```

Response:
```json
{"status": "ok", "role": "patient", "account_id": 1, "patient_id": 42}
```

### Doctor login
`POST /doctors/login`

Request:
```json
{"mobile": "+1 555 555 0001", "password": "secret"}
```

Response:
```json
{"status": "ok", "role": "doctor", "account_id": 2, "patient_id": null}
```

### Hospital login
`POST /hospitals/login`

Request:
```json
{"mobile": "+1 555 555 0002", "password": "secret"}
```

Response:
```json
{"status": "ok", "role": "hospital", "account_id": 3, "patient_id": null}
```

## Creating patient accounts
`POST /api/v1/patients`

Include both `mobile` and `password` to create a patient account:
```json
{
  "name": "Jane Doe",
  "age": 30,
  "sex": "F",
  "mobile": "+1 555 123 4567",
  "password": "secret"
}
```

If only one of `mobile` or `password` is provided, the request is rejected.

## Data model
Table: `accounts`

Columns:
- `id` (int, primary key)
- `role` (string, indexed)
- `mobile` (string, indexed)
- `password_hash` (string, PBKDF2)
- `patient_id` (int, nullable, FK -> patients.id)
- `created_at` (datetime)

Unique constraint:
- `(role, mobile)`

## Implementation notes
- Hashing: `app/utils/passwords.py`
- Login handlers: `app/api/v1/routes/auth.py`
- Account model: `app/models/account.py`
- Patient signup integration: `app/api/v1/routes/patients.py`

## Limitations
- No token/JWT issuance yet.
- No password reset or MFA.
- Doctor/hospital registration is not exposed by API; accounts must be seeded or created manually.

## Quick manual seed (SQLite)
If you want to create doctor or hospital accounts manually, insert into `accounts`
with `role = 'doctor'` or `role = 'hospital'` and a hashed password from
`app/utils/passwords.py`.
