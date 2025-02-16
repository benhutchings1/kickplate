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

variable "location" {
    type = string
    description = "Deployment location of resources"
}

variable "worker_node_pool_size" {
    type = number
    description = "Number of nodes in control node pool"
}