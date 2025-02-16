output "name" {
  value = local.acr_name
}

output "id" {
  value = azurerm_container_registry.acr.id
}
