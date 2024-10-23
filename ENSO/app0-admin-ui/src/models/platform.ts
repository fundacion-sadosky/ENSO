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

export interface AppRole {
  id?: string
  name: string
  description: string
  application?: string
  can_delete?: boolean
  enabled?: boolean
}

export interface AppDef {
  id?: string
  name: string
  description: string
  url: string
  default_role: string
  image?: string
  enabled?: boolean
  use_emulator?: boolean
  file_resource_gams_source?: any
  file_resource_input_sample?: any
  file_resource_output_sample?: any
}
