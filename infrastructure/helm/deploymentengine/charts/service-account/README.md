# Description
This chart can 
- create many service accounts and roles.
- generate secrets for the service accounts
- bind service accounts to roles

# Values
## serviceAccounts
Takes list of service accounts to create
Service account parameters
    name: str - unique name of SA
    giveRoles: [str] - list of rolenames, corresponding to roles made below. Will be bound to the SA
    namespace: str - if null, wont namespace
    createSecret: bool - whether to create secret

[ example ]
serviceAccounts:
-   name: testSA
    giveRoles: ["readMap"]
    namespace: default
    createSecret: True

## roles
List of roles to create, to then map to service accounts
Role parameters
    roleName: str
    verb: [str]
    resources: [str]
    apiGroups: [str]

[ example ]
roles:
-   roleName: readMap
    verbs: ["get"]
    resources: ["ConfigMap"]
    apiGroups: ["v1"]