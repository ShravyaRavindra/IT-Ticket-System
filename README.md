# ServiceTrack — IT Incident & Resolution Management

ServiceTrack is a web-based IT incident and resolution management system designed to centralize employee IT support requests and manage them through a controlled incident lifecycle.

The system allows employees to create IT incidents, support agents to take ownership and work on them, and employees to confirm resolution before the incident is finally closed.

The project also demonstrates automated software testing using **pytest** for backend/API testing and **Selenium WebDriver** for browser-based functional testing.

---

## Table of Contents

- [Project Overview](#project-overview)
- [Problem Statement](#problem-statement)
- [Objectives](#objectives)
- [Key Features](#key-features)
- [User Roles](#user-roles)
- [Incident Lifecycle](#incident-lifecycle)
- [Technology Stack](#technology-stack)
- [System Architecture](#system-architecture)
- [Project Structure](#project-structure)
- [Database Design](#database-design)
- [API Endpoints](#api-endpoints)
- [Testing](#testing)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Running the Application](#running-the-application)
- [Running Backend Tests](#running-backend-tests)
- [Running Selenium Tests](#running-selenium-tests)
- [Application Workflow](#application-workflow)
- [Security and Validation](#security-and-validation)
- [Future Enhancements](#future-enhancements)
- [Limitations](#limitations)
- [Resume Description](#resume-description)
- [Interview Explanation](#interview-explanation)
- [Author](#author)

---

# Project Overview

ServiceTrack provides a centralized platform for managing internal IT incidents.

Instead of employees reporting technical problems through emails, messages or informal communication, each problem can be recorded as a structured incident containing:

- Title
- Description
- Category
- Priority
- Creator
- Assigned support agent
- Current status
- Creation timestamp
- Resolution timestamp
- Closure timestamp

The application manages the complete incident lifecycle and maintains a history of status changes.

---

# Problem Statement

In a typical organization, IT issues may be reported through multiple communication channels.

This can make it difficult to:

- Track reported incidents
- Identify who is responsible for an issue
- Prioritize incidents
- Monitor resolution progress
- Maintain an audit trail
- Confirm that an issue has actually been resolved
- Know which incidents are still pending

ServiceTrack addresses these problems by providing a centralized IT incident management workflow.

---

# Objectives

The main objectives of ServiceTrack are:

1. Centralize IT support incidents.
2. Allow employees to create structured incidents.
3. Allow support agents to manage assigned incidents.
4. Implement priority-based incident management.
5. Enforce valid incident status transitions.
6. Maintain incident history.
7. Provide role-based access.
8. Allow employees to confirm incident resolution.
9. Provide backend/API validation.
10. Automate UI testing using Selenium.
11. Maintain source code using Git/GitHub.

---

# Key Features

## Employee Features

- User login
- Employee dashboard
- Create IT incident
- Select incident category
- Select incident priority
- View submitted incidents
- Track incident status
- Confirm resolved incidents

## Agent Features

- Agent login
- Agent dashboard
- View incidents
- Assign incidents
- Start working on incidents
- Resolve incidents
- Track incident status

## Admin Features

- Administrative access
- Access to agent-side functionality
- Incident management capabilities

## System Features

- Authentication
- Role-based authorization
- Ticket/incident validation
- Status workflow management
- Incident history
- Database relationships
- REST-style API endpoints
- Automated backend testing
- Automated browser testing

---

# User Roles

| Role | Responsibilities |
|------|------------------|
| EMPLOYEE | Create incidents, view tickets and confirm resolution |
| AGENT | Manage assigned incidents, start work and resolve incidents |
| ADMIN | Administrative access to incident management |

---

# Incident Lifecycle

The incident follows a controlled workflow:

```text
NEW
 ↓
ASSIGNED
 ↓
IN_PROGRESS
 ↓
RESOLVED
 ↓
CLOSED
