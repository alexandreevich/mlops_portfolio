# Контексты 
### Смотрим че есть
- kubectl config get-contexts

### пилим у себя локально новый 
- vim new-cluster-config.yaml

### Далее меджик
- KUBECONFIG=~/.kube/config:new-cluster-config.yaml \
  kubectl config view --flatten > l

### Потом еще
- mv ~/.kube/config-merged ~/.kube/config

### Смотрим что появился еще один слоненок
- - kubectl config get-contexts

### И осталось махнуть
- kubectl config use-context r-mlops-k8s-9-1-3-854415502-context