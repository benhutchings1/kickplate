az login --use-device-code
terraform init -backend-config="locs/dev.backend.tfvars"
terraform apply -var-file="vars/dev.tfvars"

terraform init -backend-config="locs/prod.backend.tfvars"
terraform apply -var-file="vars/prod.tfvars"