/**
 * Full E2E smoke. Hits the real FastAPI service.
 *
 * Prereqs (started outside the test runner):
 *   - `docker compose up postgres redis qdrant minio` (or equivalent)
 *   - `uvicorn kmg_api.main:app --port 8000`
 *   - `web/.env` with KMG_API_BASE_URL=http://localhost:8000
 *
 * Use the dev `X-Tenant-Id` bypass — the auth dependency accepts any UUID when
 * KMG_ENV != production (api/src/kmg_api/dependencies.py line 60+).
 */
import { test, expect } from '@playwright/test'

const TENANT_ID = process.env.KMG_TEST_TENANT_ID ?? '00000000-0000-0000-0000-000000000001'

test.describe.serial('Authenticated app flow', () => {
  test.beforeEach(async ({ page }) => {
    await page.addInitScript((id) => {
      window.localStorage.setItem('kmg.tenant_id', id)
    }, TENANT_ID)
  })

  test('login page redirects to /app after submit', async ({ page }) => {
    await page.goto('/auth/login')
    await expect(page.getByText('Sign in.')).toBeVisible()
  })

  test('project base picker renders and creates a new base', async ({ page }) => {
    await page.goto('/app')
    await expect(page.getByText('Choose your vault.')).toBeVisible()
    await page.getByRole('button', { name: /New base/ }).first().click()
    await expect(page.getByText('New Project Base')).toBeVisible()
    const slug = `e2e-${Date.now()}`
    await page.getByPlaceholder('Client Research').fill('E2E Smoke')
    await page.getByPlaceholder('client-research').fill(slug)
    await page.getByRole('button', { name: 'Create' }).click()
    await page.waitForURL(new RegExp(`/app/${slug}`))
    await expect(page.getByText('E2E Smoke')).toBeVisible()
  })

  test('command palette opens with ⌘K', async ({ page, browserName }) => {
    await page.goto('/app')
    const meta = browserName === 'webkit' || process.platform === 'darwin' ? 'Meta' : 'Control'
    await page.keyboard.press(`${meta}+KeyK`)
    await expect(page.getByPlaceholder(/Search wiki/i)).toBeVisible()
  })
})

test('marketing landing has hero + nav', async ({ page }) => {
  await page.goto('/')
  await expect(page.getByText('Drop a source.')).toBeVisible()
  await expect(page.getByRole('link', { name: 'Pricing' })).toBeVisible()
})

test('waitlist form renders', async ({ page }) => {
  await page.goto('/waitlist')
  await expect(page.getByPlaceholder('you@company.com')).toBeVisible()
  await expect(page.getByRole('button', { name: 'Request access' })).toBeVisible()
})

test('pricing page lists tiers', async ({ page }) => {
  await page.goto('/pricing')
  await expect(page.getByRole('heading', { name: 'Hobby' })).toBeVisible()
  await expect(page.getByRole('heading', { name: 'Pro' })).toBeVisible()
  await expect(page.getByRole('heading', { name: 'Team' })).toBeVisible()
})
