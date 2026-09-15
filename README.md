JJ - Just Job

Recruitment platform on FastAPI. Three roles: applicant, tenant (employer), admin. Covers vacancies, resumes, responses (applications) and interview invitations.

Features

Role-based access: applicant, tenant, admin. Admins can act on any vacancy, resume, response or invitation, owners act on their own. Ownership and admin-override checks live in shared FastAPI dependencies (check_*_owner_or_admin), so each resource has one route and one service, not separate admin and user endpoints.

Vacancies and resumes: tenants post and manage vacancies, applicants create and manage resumes.

Responses: applicants apply to a vacancy with a resume, tenants review responses and set status (hired, rejected, etc) for their own vacancies, admins can act on any response.

Invitations: tenants invite applicants to an interview, either side manages their own, admins can act on any invitation.

Search for vacancies, resumes and responses runs on Meilisearch, synced from Postgres through Celery tasks on create/update/delete.

Caching of hot reads (profile info, my vacancies/resumes/responses) via Redis, invalidated on writes.

Background jobs (search sync, mail, cleanup) run through Celery with RabbitMQ as broker, viewable in Flower.

Rate limiting on sensitive endpoints (creating vacancies/resumes, search, invitations).

Mail sent through a mail service, viewable locally via MailDev.

Monitoring: request metrics via prometheus-fastapi-instrumentator, logs through Promtail into Loki, dashboards in Grafana, metrics in Prometheus.

Migrations via Alembic.

Tech stack

FastAPI, PostgreSQL, SQLAlchemy (async), Alembic, Redis, Celery, RabbitMQ, Meilisearch, Docker Compose, Prometheus, Grafana, Loki, Promtail, Nginx

API overview

/users - sign up/in, my profile, password/name update, self delete
/admin/users - admin only, search/update/delete any user
/vacancies - create/list own (tenant), update/delete via owner-or-admin dependency
/resumes - create/list own (applicant), update/delete via owner-or-admin dependency
/responses - apply to vacancy, search, list own, delete, set status, via owner-or-admin dependencies
/invitations - send/update/delete/search, via owner-or-admin dependencies
/search - Meilisearch search over vacancies and resumes

Full schemas are in the auto-generated docs at /docs once the app is running.

Running with Docker

Copy .prod.env.example to .prod.env and fill in the values, set DB_HOST to db. Then run:

docker compose -p jj-web up --build

This starts the API, Postgres, Redis, RabbitMQ, Celery worker and Flower, Meilisearch, Nginx, MailDev, and the monitoring stack. Migrations run automatically on backend startup.

Creating an admin

docker exec -it jj_db psql -U postgres -d name_of_db
UPDATE users SET role = 'admin' WHERE email = 'email@example.com';

Tests

Run with pytest -s -v from the tests directory. Uses testcontainers to spin up real Postgres and Meilisearch for integration coverage, Celery tasks are mocked in unit tests. Config in .test.env and pytest.ini.