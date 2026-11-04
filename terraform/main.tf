terraform {
  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 4.0"
    }
    random = {
      source  = "hashicorp/random"
      version = "~> 3.6"
    }
  }
}

provider "azurerm" {
  features {}
}

# Jedinstveni sufiks da imena resursa ne koliduju globalno
resource "random_string" "suffix" {
  length  = 6
  special = false
  upper   = false
}

# --- Resource Group ---
resource "azurerm_resource_group" "main" {
  name     = "rg-${var.project_name}"
  location = var.location
}

# --- Azure Container Registry (cuva Docker image) ---
resource "azurerm_container_registry" "main" {
  name                = "acr${replace(var.project_name, "-", "")}${random_string.suffix.result}"
  resource_group_name = azurerm_resource_group.main.name
  location            = azurerm_resource_group.main.location
  sku                 = "Basic"
  admin_enabled       = true
}

# --- Log Analytics (za logove i metrike aplikacije) ---
resource "azurerm_log_analytics_workspace" "main" {
  name                = "log-${var.project_name}"
  resource_group_name = azurerm_resource_group.main.name
  location            = azurerm_resource_group.main.location
  sku                 = "PerGB2018"
  retention_in_days   = 30
}

# --- Container Apps okruzenje ---
resource "azurerm_container_app_environment" "main" {
  name                       = "env-${var.project_name}"
  resource_group_name        = azurerm_resource_group.main.name
  location                   = azurerm_resource_group.main.location
  log_analytics_workspace_id = azurerm_log_analytics_workspace.main.id
}

# --- Sama aplikacija ---
resource "azurerm_container_app" "main" {
  name                         = "app-${var.project_name}"
  resource_group_name          = azurerm_resource_group.main.name
  container_app_environment_id = azurerm_container_app_environment.main.id
  revision_mode                = "Single"

  registry {
    server               = azurerm_container_registry.main.login_server
    username             = azurerm_container_registry.main.admin_username
    password_secret_name = "acr-password"
  }

  secret {
    name  = "acr-password"
    value = azurerm_container_registry.main.admin_password
  }

  template {
    min_replicas = 0 # scale-to-zero: ne placas dok niko ne koristi app
    max_replicas = 2

    container {
      name   = "api"
      # Placeholder image; pravi image deployujes posle sa az containerapp update
      image  = "mcr.microsoft.com/k8se/quickstart:latest"
      cpu    = 0.25
      memory = "0.5Gi"
    }
  }

  ingress {
    external_enabled = true
    target_port      = 8000

    traffic_weight {
      latest_revision = true
      percentage      = 100
    }
  }
}
