
import type {
  BoardStats,
  CampusItem,
  ItemDraft,
  AuthTokenResponse,
  AuthUser,
  SignupData,
  PasswordLoginData,
  ProfileUpdateData,
  PasswordChangeData,
} from './types'

// Backend API URL.
// Example: https://your-backend.onrender.com
const API_BASE_URL = (
  import.meta.env.VITE_API_BASE_URL ?? ''
).replace(/\/$/, '')

// Keep the short-lived access token in memory,
// not in localStorage.
let accessToken: string | null = null

// Prevent multiple simultaneous refresh requests.
let refreshInFlight: Promise<AuthTokenResponse> | null = null


// =====================================================
// ACCESS TOKEN MANAGEMENT
// =====================================================

export function getToken(): string | null {
  return accessToken
}

export function saveToken(token: string): void {
  accessToken = token
}

export function clearToken(): void {
  accessToken = null
}


// =====================================================
// LOW-LEVEL HTTP REQUEST
// =====================================================

async function sendRequest(
  path: string,
  options: RequestInit = {},
  attachToken = true,
): Promise<Response> {
  const headers = new Headers(options.headers)

  if (options.body && !headers.has('Content-Type')) {
    headers.set('Content-Type', 'application/json')
  }

  if (attachToken && accessToken) {
    headers.set('Authorization', `Bearer ${accessToken}`)
  }

  return fetch(`${API_BASE_URL}${path}`, {
    ...options,
    headers,
    credentials: 'include',
  })
}


// =====================================================
// RESPONSE HANDLING
// =====================================================

async function parseResponse<T>(response: Response): Promise<T> {
  if (response.status === 204) {
    return undefined as T
  }

  const data = await response.json().catch(() => ({}))

  if (!response.ok) {
    const detail =
      typeof data?.detail === 'string'
        ? data.detail
        : 'Something went wrong. Please try again.'

    throw new Error(detail)
  }

  return data as T
}


// =====================================================
// JWT REFRESH
// =====================================================

async function refreshAccessToken(): Promise<AuthTokenResponse> {
  if (!refreshInFlight) {
    refreshInFlight = (async () => {
      // The browser automatically sends the HTTP-only
      // refresh cookie. JavaScript cannot read that cookie.
      const response = await sendRequest(
        '/api/auth/refresh',
        { method: 'POST' },
        false,
      )

      const result = await parseResponse<AuthTokenResponse>(response)

      saveToken(result.access_token)

      return result
    })().finally(() => {
      refreshInFlight = null
    })
  }

  return refreshInFlight
}


// =====================================================
// SESSION RESTORATION
// =====================================================

export async function restoreSession(): Promise<AuthUser | null> {
  try {
    const result = await refreshAccessToken()
    return result.user
  } catch {
    clearToken()
    return null
  }
}


// =====================================================
// GENERAL API REQUEST
// =====================================================

interface ApiRequestOptions extends RequestInit {
  authRetry?: boolean
  attachToken?: boolean
}

async function request<T>(
  path: string,
  options: ApiRequestOptions = {},
): Promise<T> {
  const {
    authRetry = true,
    attachToken = true,
    ...fetchOptions
  } = options

  let response = await sendRequest(
    path,
    fetchOptions,
    attachToken,
  )

  // If an access token expires, try refreshing it once.
  if (
    response.status === 401 &&
    authRetry &&
    accessToken &&
    path !== '/api/auth/refresh'
  ) {
    try {
      await refreshAccessToken()

      response = await sendRequest(
        path,
        fetchOptions,
        true,
      )
    } catch {
      // The refresh session is no longer valid.
      // Clear the access token and retry as a guest.
      clearToken()

      response = await sendRequest(
        path,
        fetchOptions,
        false,
      )
    }
  }

  return parseResponse<T>(response)
}


// =====================================================
// SIGNUP
// =====================================================

export async function signUp(
  data: SignupData,
): Promise<AuthTokenResponse> {
  const result = await request<AuthTokenResponse>(
    '/api/auth/register',
    {
      method: 'POST',
      body: JSON.stringify(data),
      authRetry: false,
      attachToken: false,
    },
  )

  saveToken(result.access_token)

  return result
}


// =====================================================
// PASSWORD LOGIN
// =====================================================

export async function signIn(
  data: PasswordLoginData,
): Promise<AuthTokenResponse> {
  const result = await request<AuthTokenResponse>(
    '/api/auth/login',
    {
      method: 'POST',
      body: JSON.stringify(data),
      authRetry: false,
      attachToken: false,
    },
  )

  saveToken(result.access_token)

  return result
}


// =====================================================
// CURRENT USER
// =====================================================

export function getMe(): Promise<AuthUser> {
  return request<AuthUser>('/api/auth/me')
}


// =====================================================
// STUDENT PROFILE MANAGEMENT
// =====================================================

export function updateProfile(
  data: ProfileUpdateData,
): Promise<AuthUser> {
  return request<AuthUser>(
    '/api/auth/profile',
    {
      method: 'PATCH',
      body: JSON.stringify(data),
    },
  )
}


// =====================================================
// CHANGE PASSWORD
// =====================================================

export async function changePassword(
  data: PasswordChangeData,
): Promise<void> {
  await request<void>(
    '/api/auth/change-password',
    {
      method: 'POST',
      body: JSON.stringify(data),
    },
  )

  // The backend revokes all refresh sessions.
  // Clear this browser's access token too.
  clearToken()
}



// =====================================================
// LOGOUT
// =====================================================

export async function signOut(): Promise<void> {
  try {
    await request<void>(
      '/api/auth/logout',
      {
        method: 'POST',
        authRetry: false,
        attachToken: false,
      },
    )
  } finally {
    clearToken()
  }
}


// =====================================================
// LOST & FOUND ITEM IMAGE NORMALIZATION
// =====================================================

function normalizeItem(item: CampusItem): CampusItem {
  if (!item.image_url || /^https?:\/\//i.test(item.image_url)) {
    return item
  }

  return {
    ...item,
    image_url: `${API_BASE_URL}${item.image_url}`,
  }
}


// =====================================================
// BOARD STATISTICS
// =====================================================

export function getStats(): Promise<BoardStats> {
  return request<BoardStats>('/api/stats')
}


// =====================================================
// LOST & FOUND ITEMS
// =====================================================

export function getItems(filters: {
  q?: string
  category?: string
  reportType?: string
  status?: string
}): Promise<CampusItem[]> {
  const params = new URLSearchParams()

  if (filters.q?.trim()) {
    params.set('q', filters.q.trim())
  }

  if (filters.category && filters.category !== 'All items') {
    params.set('category', filters.category)
  }

  if (filters.reportType && filters.reportType !== 'all') {
    params.set('report_type', filters.reportType)
  }

  if (filters.status) {
    params.set('status', filters.status)
  }

  const query = params.toString()

  return request<CampusItem[]>(
    `/api/items${query ? `?${query}` : ''}`,
  ).then((items) => items.map(normalizeItem))
}


export function getItem(id: number): Promise<CampusItem> {
  return request<CampusItem>(
    `/api/items/${id}`,
  ).then(normalizeItem)
}


export function createItem(draft: ItemDraft): Promise<CampusItem> {
  return request<CampusItem>(
    '/api/items',
    {
      method: 'POST',
      body: JSON.stringify({
        ...draft,
        incident_date: draft.incident_date || null,
      }),
    },
  ).then(normalizeItem)
}


export function updateItem(
  id: number,
  draft: ItemDraft,
): Promise<CampusItem> {
  return request<CampusItem>(
    `/api/items/${id}`,
    {
      method: 'PUT',
      body: JSON.stringify({
        ...draft,
        incident_date: draft.incident_date || null,
      }),
    },
  ).then(normalizeItem)
}


export function updateStatus(
  id: number,
  status: 'open' | 'resolved',
): Promise<CampusItem> {
  return request<CampusItem>(
    `/api/items/${id}/status`,
    {
      method: 'PATCH',
      body: JSON.stringify({ status }),
    },
  ).then(normalizeItem)
}


// =====================================================
// ITEM CONTACT DETAILS
// =====================================================

export function getContact(id: number): Promise<{
  reporter_name: string
  phone_number: string | null
  whatsapp_number: string | null
  extra_contact_info: string | null
  contact_info: string
}> {
  return request(
    `/api/items/${id}/contact`,
  )
}


// =====================================================
// DELETE ITEM
// =====================================================

export function deleteItem(id: number): Promise<void> {
  return request<void>(
    `/api/items/${id}`,
    { method: 'DELETE' },
  )
}
