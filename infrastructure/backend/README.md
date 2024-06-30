# Backend
Sets up a storage account and container to store remote terraform state </br>
Once executed, delete the tfstate
## Usage
Showing run for each environment
```
az login --use-device-code
terraform init -backend-config="locs/dev.backend.tfvars"
terraform apply -var-file="vars/dev.tfvars"

terraform init -backend-config="locs/prod.backend.tfvars"
terraform apply -var-file="vars/prod.tfvars"
```
or 
```
./run.sh
```