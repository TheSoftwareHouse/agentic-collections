# Worked example: a fully populated epic with stories

The shape [`benchmark-template.md`](./benchmark-template.md) produces when applied to a
real workshop. Match this level of detail and tone.


### Epic: User Authentication: Secure Login and Account Access

**Jira Key**: —
**Status**: —
**Priority**: Highest

**Description**:
```
h2. Overview

Enable users to securely log in, manage their accounts, and recover access if credentials are lost. This is the foundational epic that gates access to all application features.

h2. Business Value

Without authentication, the application cannot distinguish between users, enforce permissions, or protect user data. This epic enables personalised experiences and regulatory compliance (GDPR, SOC2).

h2. Success Metrics

* Users can register, log in, and access their personalised dashboard
* Password recovery flow resolves 95% of access issues without support intervention
* All authentication flows complete in under 3 seconds
```

**Acceptance Criteria**:
```
(/) Users can create an account with email and password
(/) Users can log in with valid credentials
(/) Users receive an error message for invalid credentials
(/) Users can reset their password via email
(/) Session timeout redirects users to the login page
```

**Labels**: `auth`, `workshop-2026-02-19`

---

### Story 1.1: User can register a new account

**Parent**: User Authentication: Secure Login and Account Access
**Jira Key**: PROJ-124
**Status**: In Progress
**Priority**: Highest
**Sizing Guidance**: Medium (5-8)

**Description**:
```
h2. Context

This story is part of the [User Authentication: Secure Login and Account Access] epic. It enables new users to create an account and gain access to the application.

h2. User Story

As a new user, I want to register an account with my email and password so that I can access the application's features.

h2. Requirements

# Registration form collects email address and password
# Email address must be unique across all accounts
# Password must meet minimum security requirements (discussed: at least 8 characters)
# User receives a confirmation email after registration
# User is redirected to the dashboard after successful registration

h2. Technical Notes

Discussed during workshop: SSO integration may be added later as a separate story. For now, email/password registration only.
```

**Acceptance Criteria**:
```
(/) Registration form is accessible from the landing page
(/) Duplicate email addresses are rejected with a clear error message
(/) Passwords shorter than 8 characters are rejected with guidance
(/) Confirmation email is sent within 1 minute of registration
(/) Successful registration redirects to user dashboard
```

**Labels**: `auth`, `workshop-2026-02-19`

---

### Story 1.2: User can log in with existing credentials

**Parent**: User Authentication: Secure Login and Account Access
**Jira Key**: —
**Status**: —
**Priority**: Highest
**Sizing Guidance**: Small (1-3)

**Description**:
```
h2. Context

This story is part of the [User Authentication: Secure Login and Account Access] epic. It allows returning users to access their account.

h2. User Story

As a returning user, I want to log in with my email and password so that I can access my account and data.

h2. Requirements

# Login form collects email and password
# Valid credentials grant access to the user dashboard
# Invalid credentials display a clear error message without revealing which field is wrong
# Session is created with appropriate timeout

h2. Technical Notes

No specific technical considerations discussed.
```

**Acceptance Criteria**:
```
(/) Login form is accessible from the landing page
(/) Valid credentials redirect to the user dashboard
(/) Invalid credentials show a generic error message
(/) Three consecutive failed attempts trigger a temporary lockout
```

**Labels**: `auth`, `workshop-2026-02-19`

---

### Story 1.3: User can reset forgotten password

**Parent**: User Authentication: Secure Login and Account Access
**Jira Key**: PROJ-126
**Status**: To Do
**Priority**: High
**Sizing Guidance**: Medium (5-8)

**Description**:
```
h2. Context

This story is part of the [User Authentication: Secure Login and Account Access] epic. It provides a self-service recovery path for users who forget their password.

h2. User Story

As a user who forgot my password, I want to reset it via email so that I can regain access to my account without contacting support.

h2. Requirements

# "Forgot password" link is visible on the login page
# User enters their email to request a password reset
# Reset link is sent to the registered email
# Reset link expires after a defined period
# User can set a new password via the reset link

h2. Technical Notes

Discussed during workshop: Reset link should expire after 24 hours. Team to confirm exact duration during refinement.
```

**Acceptance Criteria**:
```
(/) "Forgot password" link is visible and accessible on the login page
(/) Password reset email is sent within 1 minute of request
(/) Reset link expires after the configured period
(/) Expired links show a clear message and option to request a new one
(/) New password must meet the same requirements as registration
```

**Labels**: `auth`, `workshop-2026-02-19`
