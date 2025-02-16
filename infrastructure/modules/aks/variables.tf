variable "resource_group_name" {
  description = "Name of resource to deploy within"
  type        = string
}

variable "tags" {
  description = "Tags to apply to ACR resource"
  type        = map(any)
  default     = null
}

variable "env" {
  description = "Environment to deploy within"
  type        = string
  validation {
    condition     = contains(["prod", "dev"], var.env)
    error_message = "Given ${var.env}, expected 'prod' or 'dev'"
  }
}

variable "location" {
  description = "Location to deploy resource in"
  type        = string
}

variable "dns_prefix" {
  type = string
}

variable "system_node_pool" {
  description = "Configuration of system control node pool"
  type = object({
    vm_size    = string
    node_count = number
  })
  default = {
    vm_size    = "Standard_D2_v2"
    node_count = 1
  }
}

variable "worker_node_pools" {
  description = "Configuration of worker node pool  [optional]"
  type = list(object({
    name       = string
    vm_size    = string
    node_count = number
  }))
  default = []
}


variable "acr_id" {
  description = "ID of private container registry to connect"
  type        = string
}
