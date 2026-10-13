# Fixture

Set `DATABASE_URL` in `.env` first, see `.env.example`.

```bash
npm install
npm run dev
```

Build with `npm run build`, lint with `npm run lint`. <!-- expect: README-SCRIPT -->

The service lives in `src/app/service.py`, helpers in `web/lib/format.ts`.
Old helpers were in `web/utils/old.ts`. <!-- expect: README-PATH -->
See [the architecture](ARCHITECTURE.md) and [setup notes](docs/setup.md). <!-- expect: README-PATH -->

Runs on Node.js 20 with `pnpm install` or `yarn`.
