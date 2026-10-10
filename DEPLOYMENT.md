# Publish OpportunityOS with Vercel and Render

The frontend, backend, and PostgreSQL database are separate services. Deploy
the backend first, then configure the frontend with its URL, and finally allow
the frontend origin in the backend's CORS settings.

## 1. Prepare the repository

Push the source to a Git repository accessible to your hosting accounts.
Keep `frontend/` and `backend/` directly under the repository root. Include
`frontend/package-lock.json`, `backend/seeds/skills.csv`, and the deployment
files. Exclude private `.env` files, local databases, `node_modules`, virtual
environments, caches, and old build output.

## 2. Deploy the backend and database on Render

For the included Blueprint, choose **New > Blueprint** and connect the
repository. Review the service and database plans before applying it. The
`render.yaml` file provisions the Python backend and PostgreSQL, sets
`DATABASE_URL`, generates a private JWT secret, and starts in demo mode.
Python 3.12 is selected by `.python-version`. The default CORS list is empty
until the actual frontend origin is added in step 4.

### Use the database already created in My Workspace

The existing `opportunityos-db` is in Singapore. Use
`render.existing-db.yaml` to deploy just the backend and reference that database
automatically, without copying its secret connection URL.

1. In Render, choose **New > Blueprint** and connect `neevbaldha2007/OpportunityOS`.
2. Select branch `codex/hosting-ready-20261010` and set **Blueprint Path** to
   `render.existing-db.yaml`.
3. Confirm the workspace is **My Workspace**, then deploy the Blueprint.

This file defines one free Python web service in Singapore and no new database.
It generates the JWT secret and allows the assigned Vercel production origin,
`https://opportunityos-omega.vercel.app`. Once the backend is live, continue
with the frontend deployment using its actual URL.

For manual creation, create PostgreSQL and a Python Web Service in the same
region. Use these settings for the web service:

| Setting | Value |
| --- | --- |
| Root Directory | `backend` |
| Build Command | `pip install -r requirements.txt` |
| Start Command | `uvicorn app.main:app --host 0.0.0.0 --port $PORT` |
| Health Check Path | `/health` |

Set these environment variables on the backend:

| Variable | Value |
| --- | --- |
| `APP_ENV` | `production` |
| `API_PREFIX` | Empty string |
| `DATABASE_URL` | The database's Internal Database URL |
| `JWT_SECRET` | A private random secret of at least 32 characters |
| `JWT_EXPIRE_MINUTES` | `1440` |
| `CORS_ORIGINS` | `[]` initially |
| `DEMO_MODE` | `true` initially |

Generate a JWT secret locally if you are creating the service manually:

```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

Paste the result only into Render's environment settings. Keep the same
secret across normal redeployments so existing logins remain valid.

The app converts `postgres://` and `postgresql://` connection strings to
`postgresql+psycopg://` automatically. You do not need to edit the provider's
URL yourself. Database tables and the skills catalog initialize on startup.

If creating services with an API that cannot set Root Directory, use
`cd backend && pip install -r requirements.txt` as Build Command and
`cd backend && uvicorn app.main:app --host 0.0.0.0 --port $PORT` as Start
Command. Keep the root `.python-version` file.

After deployment, open the returned backend URL with `/health` appended.
Expect JSON containing `"status": "ok"`. `/docs` provides the API reference.

## 3. Deploy the frontend on Vercel

Import the same repository into Vercel:

| Setting | Value |
| --- | --- |
| Root Directory | `frontend` |
| Framework Preset | Vite |
| Node.js Version | `24.x` |
| Install Command | `npm ci` |
| Build Command | `npm run build` |
| Output Directory | `dist` |

Set `VITE_API_BASE_URL` in the **Production** environment to the actual HTTPS
backend URL from Render. Use the backend root URL, without `/docs`, `/health`,
or an `/api` suffix when `API_PREFIX` is empty. Then deploy.

The build rejects an absent API URL, HTTP URLs, and localhost URLs in
production. `frontend/vercel.json` preserves SPA routing, including refreshing
`/dashboard`. Changing environment variables requires a new deployment.

`VITE_` variables are included in browser JavaScript. Keep `DATABASE_URL`,
`JWT_SECRET`, and `SERPAPI_API_KEY` on Render's backend only.

## 4. Set the frontend origin on Render

Copy the stable production domain assigned by Vercel. In the backend's
Render Environment settings, replace the empty `CORS_ORIGINS` with that
origin, for example `https://your-actual-project.vercel.app`. Do not include
a page path. Multiple allowed origins can be comma-separated or a JSON list.
Redeploy the backend after the change. Production rejects wildcard `*` CORS.

For an existing Blueprint deployment, also change its CORS entry from `[]`
to the actual public origin in your repository, or use `sync: false` for that
entry after setting it in Render, so a future Blueprint sync does not reset
your configured origin. Origins are public configuration, not secrets.

## 5. Test the public app

1. Open the Vercel production URL in a new browser session.
2. Register a new account and complete onboarding.
3. Run opportunity search. Demo mode uses labeled sample results.
4. Save an opportunity and create or update an application.
5. Check skill gaps, roadmap, and search history.
6. Refresh `/dashboard` and confirm it still loads.

To enable real listings, add your SerpApi key as `SERPAPI_API_KEY` on Render,
set `DEMO_MODE=false`, and redeploy the backend. Verify results and API usage
on your own account.

## Local development and verification

Use `backend/.env.example` and `frontend/.env.example` for local development.
Start the backend from `backend` with `uvicorn app.main:app --reload --port
8000`, and start the frontend from `frontend` with `npm run dev`.

For a local production-style preview against localhost, set
`VITE_API_BASE_URL=http://localhost:8000` and use `npm run build -- --mode
development`, then `npm run preview`. This mode is for local checks; Vercel
should keep the default production build command.

Install `backend/requirements-dev.txt` for tests. The CI suite checks
authentication, profile setup, the demo agent workflow, saved opportunities,
applications, skill gaps, roadmaps, category/scoring regressions, and
deployment configuration with disposable data. The existing
`test_live_system.py` additionally assumes a pre-populated demo account;
it is not part of the clean-database CI suite.

## Official references

- https://render.com/docs/deploy-fastapi
- https://render.com/docs/blueprint-spec
- https://render.com/docs/python-version
- https://render.com/docs/postgresql-creating-connecting
- https://vercel.com/docs/frameworks/frontend/vite
- https://vercel.com/docs/environment-variables
