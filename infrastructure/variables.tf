variable "tenant_id" {
  type = string
  description = "Tenant ID to use"
}

variable "subscription_id" {
    type = string
    description = "Subscription to use"
}

variable "env" {
    type = string
    description = "Environment to deploy resources"
    
    validation {
      condition = contains(["prod", "dev"], var.env)
      error_message = "Environment should be either prod or dev"
    }
}

variable "resource_prefix" {
    type = string
    description = "Prefix to add to all resource names"
}

variable "location" {
    type = string
    description = "Deployment location of resources"
}