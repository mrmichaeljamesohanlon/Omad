resource "azurerm_resource_group" "omad" {
  name     = var.resource_group_name
  location = var.location
}

resource "azurerm_static_web_app" "omad" {
  name                = var.static_web_app_name
  resource_group_name = azurerm_resource_group.omad.name
  location            = azurerm_resource_group.omad.location
  sku_tier            = "Free"
  sku_size            = "Free"

  tags = {
    app         = "omad"
    environment = "production"
    managed-by  = "terraform"
  }
}
