# Bellweaver - Project Plan

## Problem Statement

Parents receive overwhelming amounts of communication from multiple sources:

- **School**: Compass (calendar system) + Class Dojo (teacher communications) - multiple year level events create noise
- **Kinder**: HubHello
- **Daycare**: Xplore

**Core Issue**: Important, time-critical information (permissions, payments, reminders) gets lost in irrelevant noise. No unified calendar view across multiple children/institutions.

## Desired Outcome

A unified event aggregation and filtering system that:

1. Consolidates events from multiple sources into a single calendar
2. Filters for relevant events (based on child/year level/event type)
3. Provides advance notifications/reminders
4. Syncs to Google Calendar for easy mobile access
5. Displays summary dashboards (web, email, smart display compatible)
6. Shows "next 2 weeks" view at a glance

---

## Architecture Overview

### Event Sources

- Compass
- Class Dojo
- HubHello
- Xplore

### Data Collection Layer

- Python backend (GCP) with adapters for each source
- Secure credential storage for client tenancy for each source (e.g. API key, username/password)

### Normalization & Storage

- Firestore/Cloud SQL with unified event schema

### Filtering, Enrichment

- Free text rules engine, use LLM to select and summarise relevant events

### Presentation Layer

- Web Dashboard
- Google Calendar sync
- Email Summary
- Notification scheduler

---

## Tech Stack

### Backend

- **Language**: Python
- **Platform**: Google Cloud Platform (GCP)
- **Compute**: Cloud Run (serverless)
- **Database**: Firestore (flexible schema, easy to query) or Cloud SQL (structured)
- **Task Scheduling**: Cloud Scheduler + Cloud Tasks
- **Secrets**: Secret Manager

### Data Sources

#### MVP

- **Compass**: Use existing [heheleo/compass-education JS library](https://github.com/heheleo/compass-education)

#### Post MVP

- **Class Dojo**: API integration (if available) or web scraping
- **HubHello**: API integration (if available)
- **Xplore**: API integration (if available)

### Output Channels

- **Google Calendar**: Python Google Calendar API
- **Email**: SendGrid or Cloud Mail (Gmail API)
- **Web Dashboard**: Simple Flask/FastAPI + Vue/React (optional MVP)
- **Smart Display**: IFTTT integration or webhook-based webhooks

## Principles

- use existing API integrations where possible, even if they use a different language, wrappers should provide abstractions between remote systems / provider and standard models (to be determined)

---

## User Journey

1. Onboarding

- Parent configures credentials for remote systems (e.g. Compass)
- Parent configures institutions / schools / centres and which remote systems should be connected to each institution
- Parent defines children what centres they attend, year level / class details, special interests (e.g hockey, athletics)

1. Daily / on demand - calendar only (initially)

- Scheduler triggers integrations to poll calendars, newsletters, notifications from centres
- Integration queries for new events etc
- Finds: "Year 3 Excursion to Zoo - Dec 15"
- Normalizes and stores in database

3. Filtering:

- System checks: shoult this event be "synced" into this child's calendar based on their details and interests

4. Dashboard:

- Show a summary of all events coming up for the next 14 days, and which children they apply to

---

## Next Steps

1. **Architecture**: Propose and evaluate architecture options for MVP
2. **Assess integrations**: Research which sources have APIs vs need scraping
3. **Begin Phase 1**: Start with Compass, assuming local development only initially
