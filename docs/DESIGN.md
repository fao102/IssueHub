# IssueHub - System Design Document

## Vision

IssueHub is a lightweight AI-powered IT Service Management (ITSM) platform for
individuals, small businesses and organisations. It combines helpdesk ticket
management with AI-assisted workflows, authentication, collaboration and a
future Retrieval-Augmented Generation (RAG) knowledge base.

## Goals

- Desktop-first responsive web application.
- Lightweight architecture with minimal storage requirements.
- Support both single users and multi-user organisations.
- Production-ready deployment and clean, modular architecture.
- Portfolio-quality project demonstrating full-stack engineering and AI integration.

## Technology Stack

- **Frontend:** React (Vite), Bootstrap 5, Axios
- **Backend:** Django, Django REST Framework, JWT Authentication
- **Database:** PostgreSQL
- **Deployment:** Docker, Railway (backend), Vercel (frontend)
- **Future AI:** Google Gemini, pgvector, LangChain (optional)

## Core Features

- Authentication (register, login, JWT, email verification, password reset)
- Organisation support with Admin and Member roles
- Ticket management (CRUD, priorities, categories, status tracking)
- Comments and file attachments
- Dashboard with ticket metrics and activity feed

## Ticket Model

- Title, Description, Category, Priority, Status
- Created By, Assigned To, Organisation
- Comments, Attachments, Audit History

## AI Roadmap

- AI ticket categorisation and priority suggestions
- AI-generated ticket summaries
- Suggested support responses
- Duplicate ticket detection

## Knowledge Base & RAG

- Admins create searchable support articles.
- Embed articles into a vector database (pgvector).
- Retrieve relevant documents before sending context to Gemini.
- Generate grounded answers using retrieved knowledge.

## Development Roadmap

- **Sprint 1:** Authentication & Foundation
- **Sprint 2:** Ticket Management
- **Sprint 3:** Organisations & User Invitations
- **Sprint 4:** Dashboard & Analytics
- **Sprint 5:** AI Features
- **Sprint 6:** Knowledge Base & RAG
- **Sprint 7:** Deployment, Testing & Polish

## High-Level Architecture

React Frontend → Django REST API → PostgreSQL

Authentication, Organisations, Tickets and Knowledge Base exposed through
REST APIs.

Future integrations: Gemini AI, Email Notifications, Microsoft Graph.

## Folder Structure

- `frontend/` (pages, components, hooks, api)
- `backend/` (accounts, organisations, tickets, comments, attachments,
  knowledge, ai, core)
- `docs/` (architecture, API, database documentation)

## Future Enhancements

- AWS S3 attachments
- Email notifications
- Microsoft Graph integration
- Slack/Discord notifications
- Monitoring, logging and CI/CD improvements
