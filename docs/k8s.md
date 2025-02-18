# K8s
Directory `k8s/` contains all kubernetes related resources, including: 
- Manifests for deployments, generated using Helm and Kustomize
- Operators 

## Usage
The base manifests are create using helm. The raw base manifests can be generated using

 ```helm template .```
  from `k8s/manifests/base/kickplate`. 

The last mile configuration is done on a per-environment basis in `overlays/`. These last mile configurations include image injection and assignment of external identities. 

`base` + `overlay` produces the manifests for the overlayed environment. These can be generated using

```kubectl kustomize --enable-helm .``` 

and then deployed to a cluster using 

`kubectl kustomize --enable-helm . | kubectl apply -f -` 