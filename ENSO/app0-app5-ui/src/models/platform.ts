export interface IdDescription {
  value: string
  label: string
  internal_id?: string
  details?: Object
}

export interface PlatformFile {
  bucket: string
  filename: string
  size: number
  src_filename: string
  object_id: string
  creation_date?: string
}

export interface User {
  id?: string
  username: string
  firstname: string
  surname: string
  email: string
  phone_number: string
  enabled?: boolean
}
