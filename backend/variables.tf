variable "tenant_id" {
    type = string
    description = "Azure Entra ID tenant"
    default = "301dacd7-60f1-42bf-84ce-a38206717103"
}

# Variables pulled from tfvars file
variable "subscription_id" {
    type = string
    description = "Subscription to use"
}

variable "env" {
    type = string
    description = "Environment to deploy resources"
}

variable "location" {
    type = string
    description = ""
    default = ""
}