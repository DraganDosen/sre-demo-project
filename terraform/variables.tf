variable "project_name" {
  description = "Prefiks za imena svih resursa (malo slova i crtice)"
  type        = string
  default     = "sre-demo"
}

variable "location" {
  description = "Azure region"
  type        = string
  default     = "eastus"
}
