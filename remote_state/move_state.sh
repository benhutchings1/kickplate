# # Vars
resourcePrefix="ben-tfstate"
storageaccPrefix="bentfstate"
location="westeurope"
tags="terraform=true repository=https://github.com/benhutchings1/deployment-engine"
subscriptionID="8c11bf93-bc1d-4db6-b668-158dd1e8072c"

# set correct subscription
az account set --subscription $subscriptionID
echo "Set subscription to ${subscriptionID}"

# Create resources
az group create \
    --location $location \
    --name "${resourcePrefix}-rg" \
    --tags $tags
echo "Created resource group ${resourcePrefix}-rg"

az storage account create \
    --name              "${storageaccPrefix}storage" \
    --location          $location \
    --resource-group    "${resourcePrefix}-rg" \
    --sku               "Standard_LRS" \
    --access-tier       "Cool" \
    --tags              $tags 
echo "Created storage account ${storageaccPrefix}storage"

az storage container create\
    --name              "${storageaccPrefix}-store"\
    --account-name      "${storageaccPrefix}storage"
echo "Created storage container ${storageaccPrefix}-store"

# # Move terraform state to remote storage
terraform init  -migrate-state\
                -backend-config="resource_group_name=${resourcePrefix}-rg"\
                -backend-config="storage_account_name=${storageaccPrefix}storage"\
                -backend-config="container_name=${storageaccPrefix}-store"\
                -backend-config="key=dev.terraform.tfstate"
terraform apply