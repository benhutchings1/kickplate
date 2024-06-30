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

variable "dns_prefix" {
  type = string
}

variable "system_node_pool" {
  description = "Configuration of system control node pool"
  type = object({
    "vm_size" = string
    "node_count" = number
  })
  default = {
    vm_size = "Standard_D2_v2"
    node_count = 2
  }
}

variable "engine_node_pools" {
  description = "Configuration of node pool for executing models [optional]"
  type = list(object({
    "name" = string
    "vm_size" = string
    "node_count" = number
  }))
  default = null
}
