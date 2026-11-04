output "app_url" {
  description = "Javni URL aplikacije"
  value       = "https://${azurerm_container_app.main.latest_revision_fqdn}"
}

output "acr_login_server" {
  description = "Adresa container registry-ja (za docker push)"
  value       = azurerm_container_registry.main.login_server
}

output "resource_group" {
  value = azurerm_resource_group.main.name
}

output "container_app_name" {
  value = azurerm_container_app.main.name
}
