# Dolphin Island Tours — Rebuild

Modern booking site for [dolphinislandtours.com](https://dolphinislandtours.com).

**Stack:** Django 5 + DRF (backend) · React 18 + Vite + Tailwind (frontend) · PostgreSQL · Square Web Payments · Resend email · Docker Compose deploy.

## Features

### Customer
- Signup / login / logout (JWT)
- Update profile, delete account
- Browse tours (Dolphin Wildlife Excursion, Sunset Cruise)
- Pick date + time slot
- Party size **3–6** at **$60/person** (enforced server-side)
- Pay with credit card via **Square** (sandbox or live)
- Booking confirmation email + receipt via **Resend**
- View past + upcoming bookings

### Admin (`/admin/`)
- Add/edit **tours** (services): name, description, duration, image, sort order
- Add/edit individual **slots** (date + time + capacity + active flag)
- **Bulk-create slots**: pick tour, date range, weekdays, times, capacity → one click
- View, filter, search **bookings**; see Square payment IDs
- Manage **users**, mark staff, reset passwords
- Automatic email to admin on every new booking

## Repo layout
```
backend/   Django + DRF API
frontend/  React + Vite + Tailwind SPA
scrape/    raw HTML + images scraped from live site
```

## Local development

### 1. Backend
```bash
cd backend
cp .env.example .env       # fill in Square + Resend keys (optional for local)
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py seed              # creates 2 tours + 30 days of slots
python manage.py createsuperuser   # for /admin
python manage.py runserver
```

### 2. Frontend
```bash
cd frontend
npm install
npm run dev    # http://localhost:5173
```

Vite proxies `/api` → `localhost:8000`.

### 3. Square sandbox
1. Sign up at https://developer.squareup.com
2. Create an app → Sandbox Application ID + Access Token + Location ID
3. Fill `SQUARE_*` vars in `backend/.env` and set `SQUARE_APP_ID` so the frontend can mount the card form
4. Test card: `4111 1111 1111 1111`, any future date, any CVV

For production: change `SQUARE_ENV=production` and swap the script tag in `frontend/index.html` from `sandbox.web.squarecdn.com` to `web.squarecdn.com`.

### 4. Resend
1. Sign up at https://resend.com, verify your sending domain
2. Add `RESEND_API_KEY` and `EMAIL_FROM` to `backend/.env`
3. Without a key, the backend logs emails to stdout (dev-friendly no-op)

## Deploy (single VPS, Docker Compose)

```bash
# On your VPS (Ubuntu 22.04+)
sudo apt update && sudo apt install -y docker.io docker-compose-plugin git
git clone <your-repo> dolphin && cd dolphin
cp backend/.env.example backend/.env   # fill real values + DATABASE_URL=postgres://dolphin:dolphin@db:5432/dolphin
docker compose up -d --build
docker compose exec backend python manage.py migrate
docker compose exec backend python manage.py seed
docker compose exec backend python manage.py createsuperuser
```

Site runs on port 80. Put Caddy or nginx in front for HTTPS:
```
dolphinislandtours.com {
  reverse_proxy localhost:80
}
```

## Docker tests

Run all checks from Docker, not the host environment:

```bash
docker compose exec backend python manage.py test api --noinput --keepdb
docker compose --profile test run --rm e2e
```

The backend container startup intentionally runs only `migrate`, `collectstatic`, and `gunicorn`; tests are kept as explicit commands so a production restart cannot be blocked by a test database lifecycle issue.

## Business rules (configurable via `.env`)
| Var | Default | Meaning |
|---|---|---|
| `PRICE_PER_PERSON` | `60` | USD |
| `MIN_PARTY` | `3` | min guests per booking |
| `MAX_PARTY` | `6` | max guests per booking |

Booking refuses any party outside `[MIN_PARTY, MAX_PARTY]` and any party larger than `slot.seats_remaining`.

## API quick reference
```
POST /api/auth/signup/         {email,password,first_name,last_name,phone}
POST /api/auth/login/          {email,password} → {access,refresh}
GET  /api/auth/me/             current user
PATCH /api/auth/me/            update profile
DELETE /api/auth/me/           delete account
GET  /api/config/              {price_per_person, min_party, max_party, square_*}
GET  /api/tours/               list active tours
GET  /api/slots/?tour=<slug>   future slots
GET  /api/bookings/            current user's bookings
POST /api/bookings/create-and-pay/  {slot_id, party_size, customer_*, source_id}
```

## Notes on the scrape

The original site uses GoDaddy's website builder with a JS-rendered booking widget, so tour descriptions/pricing aren't in static HTML. The two tour names (`Dolphin Wildlife Excursion`, `Sunset Cruise`) and the address/contact info were recovered from the rendered DOM. Logo + welcome + hero images were downloaded from `img1.wsimg.com` and copied into `frontend/public/images/`. The client can swap in higher-res photos via the Tour admin.
