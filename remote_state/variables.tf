variable "location" {
  type = string
  default = "West Europe"
  description = "Location of resources"
}

variable "resource_prefix" {
  type = string
  default = "ben-tfstate-"
  description = "prefix to all resource names"
}

variable "sub_id" {
  type = string
  default = "8c11bf93-bc1d-4db6-b668-158dd1e8072c"
  description = "subscription id to use"
}

variable "ten_id" {
  type = string
  default = "301dacd7-60f1-42bf-84ce-a38206717103"
  description = "tenant id to use"
}