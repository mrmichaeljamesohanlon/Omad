variable "resource_group_name" {
  type        = string
  description = "Azure resource group for OMAD."
  default     = "rg-omad-prod-uks"
}

variable "location" {
  type        = string
  description = "Azure region."
  default     = "uksouth"
}

variable "static_web_app_name" {
  type        = string
  description = "Globally unique-ish Azure Static Web App name."
  default     = "omad-michael-prod"
}
