variable "tenant_id" {
  type = string
  description = "Tenant ID to use"
  default = "301dacd7-60f1-42bf-84ce-a38206717103"
}

variable "subscription_id" {
    type = string
    description = "Subscription to use"
    default = "8c11bf93-bc1d-4db6-b668-158dd1e8072c"
}

variable "env" {
    type = string
    description = "Environment to deploy resources"
    default = ""
    validation {
      condition = contains(["prod", "dev"], var.env)
      error_message = "Environment should be either prod or dev"
    }
}

variable "resource_prefix" {
    type = string
    description = ""
    default = ""
}

variable "location" {
    type = string
    description = ""
    default = ""
}