# Resume Gap Analyzer

An AI-powered internship/job matching and gap-analysis platform.

Upload a resume and target job postings, receive a match score plus detailed
gap analysis — ranked by which missing skills appear most frequently across
the target postings.

## Architecture

- **backend-laravel/** — Laravel 12 app: auth, CRUD, orchestration
- **ml-service/** — FastAPI microservice: resume/posting parsing, embeddings, matching, gap ranking
- **frontend** — Vue 3 + Vuetify (served via Laravel/Vite)

## Status

In active development — see the feature spec for module status.

Built as final year project (CACS452) at [university].
