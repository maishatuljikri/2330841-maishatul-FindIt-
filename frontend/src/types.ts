export type ReportType = 'lost' | 'found'
export type ItemStatus = 'open' | 'resolved'

export interface Student {
  student_id: string
  full_name: string
  phone_number: string | null
  whatsapp_number: string | null
  extra_contact_info: string | null
}

export interface CampusItem {
  id: number
  title: string
  description: string
  category: string
  report_type: ReportType
  location: string
  incident_date: string | null
  status: ItemStatus
  reporter_name: string
  created_at: string
  is_owner: boolean
  contact_available: boolean
  contact_info?: string | null
  image_url: string | null
}

export interface BoardStats {
  total_reports: number
  open_reports: number
  resolved_reports: number
  lost_reports: number
  found_reports: number
}

export interface LoginResponse {
  access_token: string
  token_type: string
  user: Student
}



export interface AuthUser {
  id: number
  student_id: string
  full_name: string
  email: string
  role: 'user' | 'admin'
  phone_number: string | null
  whatsapp_number: string | null
  extra_contact_info: string | null
}

export interface ProfileUpdateData {
  full_name?: string
  phone_number?: string | null
  whatsapp_number?: string | null
  extra_contact_info?: string | null
}

export interface PasswordChangeData {
  current_password: string
  new_password: string
}


export interface AuthTokenResponse {
  access_token: string
  token_type: 'bearer'
  expires_in: number
  user: AuthUser
}

export interface SignupData {
  student_id: string
  full_name: string
  email: string
  password: string
  phone_number?: string | null
  whatsapp_number?: string | null
  extra_contact_info?: string | null
}

export interface PasswordLoginData {
  email: string
  password: string
}


export interface ItemDraft {
  title: string
  description: string
  category: string
  report_type: ReportType
  location: string
  incident_date: string
  contact_info: string
  image_data?: string | null
}

export interface AdminOverview {
  total_students: number
  active_students: number
  banned_students: number
  admin_count: number
  total_reports: number
  open_reports: number
  resolved_reports: number
}

export interface AdminStudent {
  id: number
  student_id: string
  full_name: string
  email: string | null
  role: 'user' | 'admin'
  is_banned: boolean
  banned_at: string | null
  banned_reason: string | null
  last_login_at: string | null
  created_at: string
}

export interface AdminStudentFilters {
  q?: string
  status?: 'all' | 'active' | 'banned'
  limit?: number
  offset?: number
}
