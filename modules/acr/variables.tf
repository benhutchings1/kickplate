variable "resource_group_name" {
  description = "Name of resource to deploy within"
  type = string
}

variable "tags" {
  description = "Tags to apply to ACR resource"
  type = map
  default = null
}

variable "env" {
  description = "Environment to deploy within"
  type = string
  validation {
    condition = contains(["prod", "dev"], var.env)
    error_message = "Given ${var.env}, expected 'prod' or 'dev'"
  }
}

variable "location" {
  description = "Location to deploy resource in"
  type = string
}

variable "sku" {
  description = "Version of ACR"
  type = string
  default = "Standard"
}