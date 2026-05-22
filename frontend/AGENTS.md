# Frontend Agent Guide

## Next.js Version

This project uses Next.js `16.2.6`, React `19.2.4`, Tailwind CSS `4`, TypeScript `5`, and the App Router.

Next.js APIs and conventions may differ from older versions. Before changing framework behavior, routing, server actions, proxy, metadata, caching, or build configuration, read the relevant local docs under `node_modules/next/dist/docs/` and follow current deprecation guidance.

## Product Context

The frontend is for an Ultra-Wide Band Indoor Positioning System. It is an operational dashboard, not a marketing site. The UI should feel professional, clean, dense enough for repeated use, and readable in both light and dark mode.

Use this palette consistently:

- Dark blue: `#0F2854`
- Blue: `#1C4D8D`
- Medium blue: `#4988C4`
- Light blue: `#BDE8F5`
- Black
- White

Avoid introducing unrelated dominant palettes. Use red only for destructive actions and error states, preferably as a softer red rather than a saturated warning tone.

## Project Structure

The main source tree is `src/`.

- `src/app/layout.tsx`: root HTML/body layout.
- `src/app/globals.css`: global styles.
- `src/proxy.ts`: route proxy/auth redirect logic.
- `src/app/(app)/sign-in`: sign-in route and sign-in-only local files.
- `src/app/(dashboard)/layout.tsx`: authenticated dashboard layout. This owns `DashboardShell`, so the sidebar persists across dashboard navigation.
- `src/app/(dashboard)/page.tsx`: dashboard root.
- `src/app/(dashboard)/admin/*`: admin pages grouped by sidebar group:
  - `admin/users`
  - `admin/roles`
  - `admin/permissions`
  - `admin/features`
- `src/app/(dashboard)/node/*`: node pages grouped by sidebar group:
  - `node/list`
  - `node/ranging`
- `src/app/_components`, `src/app/_actions`, `src/app/_assets`: app-shell level code used across dashboard routes, such as sidebar and sign out.
- `src/lib`: non-React application utilities, backend API helpers, auth/session/token utilities, server-action helpers, and URL/search-param helpers.
- `src/shared`: reusable React-facing UI and assets that are not tied to one route.
- `public`: public logos and static brand assets.

Route-local files should stay beside their route in `_actions`, `_components`, `_hooks`, or `_assets` folders. Promote code to `src/shared` only when it is a reusable React/UI concern. Promote code to `src/lib` when it is non-React application logic such as auth, API calls, formatting, action helpers, or navigation helpers.

## Routing And Layout

Keep the dashboard shell persistent. Do not wrap individual dashboard pages in `DashboardShell`; use `src/app/(dashboard)/layout.tsx`.

Sidebar menu entries are configured in `src/app/_components/Sidebar.tsx`. When adding sidebar entries:

- Add the menu to `sidebarConfig`.
- Put the menu under the correct group.
- Use a public route href, for example `/admin/users`.
- Set `featureName` to the backend feature gate, for example `user/view`.
- Use `featureNames` when a menu requires multiple backend feature gates.
- Add an icon under `src/app/_assets` if the icon is specific to the app shell.

Use Next `Link` for internal navigation. Do not use plain `<a href>` for app routes unless a full document navigation is intentional.

## Auth And Backend API

This frontend uses its own cookie-based auth mechanism, not NextAuth.

- Session and cookie logic belongs in `src/lib/auth`.
- Backend API base URL and auth header helpers belong in `src/lib/api`.
- Server actions that call the backend should use helpers in `src/lib/actions` when possible.
- Route-specific server actions stay under that route's `_actions` folder.

Public UI routes and backend API paths are different. For example, the users page is `/admin/users`, while the backend API path remains `/users`. Do not change backend API paths when moving frontend route folders.

When mutating data from a server action, call `revalidatePath` with the frontend route path, for example `/admin/users`.

## Components

Component names must be PascalCase.

Use the shared UI primitives before creating route-specific copies:

- `PageHeader`, `PageContent`, `AccessDenied`
- `FilterBar`
- `TextField`, `SelectField`, `ActionMessage`
- `Modal`, `ModalActions`
- `DataTable`, `TableHead`, `TableCell`, `RowActions`, `IconActionButton`, `TableLoadingOverlay`
- `Pagination`
- `ResourcePageContent` for CRUD pages that follow the roles/permissions/features pattern

Route-specific components are appropriate when they encode page-specific behavior, such as user filters, user modals, or user table columns.

Use `SelectField` for constrained option sets such as entries-per-page, roles, status, and state. Avoid freeform numeric/text inputs when the allowed values are known.

Use icon-only action buttons for dense table actions and include accessible labels/tooltips through the shared button component.

## Styling

Use Tailwind utility classes. Keep styling local to components unless it truly belongs in `globals.css`.

General UI rules:

- Support both light and dark mode with `dark:` classes.
- Keep admin/dashboard pages compact, predictable, and task-focused.
- Use clear spacing and stable dimensions for tables, sidebars, filters, modals, and action buttons.
- Do not use marketing hero layouts inside the dashboard.
- Avoid nested card layouts. Use cards only for repeated items, modals, or genuinely framed tools.
- Make table headers centered when the table is action/status-heavy.
- Keep text from overflowing buttons, filters, table cells, and sidebar labels.

## Assets

- App-shell icons belong in `src/app/_assets`.
- Shared UI icons belong in `src/shared/assets`.
- Public brand assets belong in `public`.
- Prefer SVG icons for UI controls.
- Use the existing app and UGM logos instead of recreating them.

## Data Pages

Admin CRUD pages should follow the current resource page pattern:

- Server component page fetches auth session, feature gates, and backend data.
- Access denied state returns `AccessDenied`.
- Page content uses `PageContent` and `PageHeader`.
- Shared CRUD tables should use `ResourcePageContent` where the data shape fits.
- Page-specific tables can use shared table primitives directly.
- Filters should update query params and show table-level loading overlays rather than inline spinners.

The current admin routes are:

- `/admin/users`
- `/admin/roles`
- `/admin/permissions`
- `/admin/features`

The current node routes are:

- `/node/list`
- `/node/ranging`

## Verification

Before finishing frontend code changes, run:

```bash
npm run lint
npm run build
```

If a change is purely documentation-only, a build is not required unless the documentation references code paths that need verification.
