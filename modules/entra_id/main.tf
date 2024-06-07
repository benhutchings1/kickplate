data "azuread_client_config" "current" {}
resource "random_uuid" "application_access_scope_id" {}
resource "random_uuid" "application_access_role_id" {}

resource "azuread_application" "platform-access-control"{
    display_name = "ben-test"
    identifier_uris = ["api://bentestapp"]
    owners = [data.azuread_client_config.current.object_id]
    
    api {
      requested_access_token_version = 2

      oauth2_permission_scope {
            user_consent_description = "Allows the application to execute workflows on the platform"
            user_consent_display_name = "user.execute"
            id = random_uuid.application_access_scope_id.result
            type = "User"

      }
    }

    app_role {
      allowed_member_types = ["User"]
      display_name = "Engine User"
      description = "User of the platform"
      enabled = true
      id = random_uuid.application_access_role_id.result
      value = "User"
    }
}

resource "azuread_application_redirect_uris" "auth_redirects"{
    application_id = azuread_application.platform-access-control.id
    type = "SPA"

    redirect_uris = [
        "http://localhost:8000/docs/oauth2-redirect",
        "https://localhost"
    ]
}
