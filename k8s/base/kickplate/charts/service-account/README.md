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
    labels: yaml - subtree of key:value pairings specific to this service account

[ example ]
serviceAccounts:
-   name: testSA
    giveRoles: ["readMap"]
    namespace: default
    createSecret: True
    labels:
        role: testacc

## roles
List of roles to create, to then map to service accounts
Role parameters
    roleName: str
    verb: [str]
    resources: [str]
    apiGroups: [str]
    labels: yaml - subtree of key:value pairings specific to this service account

[ example ]
roles:
-   roleName: readMap
    verbs: ["get"]
    resources: ["ConfigMap"]
    apiGroups: ["v1"]
    labels:
        role: testenv

### Predefine role verbs
There are currently 3 predefined roles which are short hand for sets of verbs
- reader: ["get", "describe", "list", "watch"]
- contributor: ["get", "describe", "list", "watch", "create", "patch", "update"]
- owner: ["get", "describe", "list", "watch", "create", "patch", "update", "delete", "deleteCollection"]

If a set of verbs are provided then the predefined roles are overwritten
Useage of the predefined role are found below
roles:
-   roleName: readMap
    role: "reader"
    resources: ["ConfigMap"]
    apiGroups: ["v1"]
    labels:
        role: testenv

Expected outcome verbs
["get", "describe", "list", "watch"]

## Common Labels
labelsCommon: yaml - subtree of key:value pairings common to every generated resource

e.g.
labelsCommon:
    appName: testapp