<div style="font-size: 48px; font-weight: bold;">HW-1 : KUBERNETES</div>

# Стартуем
```bash
kaiser@fedora ~/w/r/p/d/kuber (main)> minikube start --driver=docker                                                         (base) 
😄  minikube v1.35.0 on Fedora 40
✨  Using the docker driver based on existing profile
👍  Starting "minikube" primary control-plane node in "minikube" cluster
🚜  Pulling base image v0.0.46 ...
🔄  Restarting existing docker container for "minikube" ...
🐳  Preparing Kubernetes v1.32.0 on Docker 27.4.1 ...
🔎  Verifying Kubernetes components...
    ▪ Using image docker.io/kubernetesui/dashboard:v2.7.0
    ▪ Using image docker.io/kubernetesui/metrics-scraper:v1.0.8
    ▪ Using image gcr.io/k8s-minikube/storage-provisioner:v5
💡  Some dashboard features require the metrics-server addon. To enable all features please run:

        minikube addons enable metrics-server

🌟  Enabled addons: storage-provisioner, dashboard, default-storageclass
🏄  Done! kubectl is now configured to use "minikube" cluster and "default" namespace by default
```

# Добавляем Deployment
```bash
kaiser@fedora ~/w/r/p/d/kuber (main)> kubectl apply -f deployment.yaml                                                       (base) 
deployment.apps/simpsons-deployment created
kaiser@fedora ~/w/r/p/d/kuber (main)> kubectl get pods                                                                       (base) 
NAME                                   READY   STATUS              RESTARTS   AGE
simpsons-deployment-6ccc7c7d9d-pmxkq   0/1     ContainerCreating   0          35s
simpsons-deployment-6ccc7c7d9d-qp7dz   0/1     ContainerCreating   0          35s
simpsons-deployment-6ccc7c7d9d-xtcv8   0/1     ContainerCreating   0          35s
```
Смотреть что не так с подом через describe pod ... -n ./. (namespace)

```bash
Events:
  Type     Reason                           Age    From               Message
  ----     ------                           ----   ----               -------
  Normal   Scheduled                        9m48s  default-scheduler  Successfully assigned default/simpsons-deployment-6ccc7c7d9d-pmxkq to minikube
  Warning  FailedToRetrieveImagePullSecret  9m47s  kubelet            Unable to retrieve some image pull secrets (regcred); attempting to pull the image may not succeed.
  Normal   Pulling                          9m47s  kubelet            Pulling image "kaiser7lu/simpsons_model:latest"
```
# Обзор ошибок
Сначала просто не так были прописаны креды :) 

Креды прописывать 
```bash
kubectl create secret docker-registry regcred \
--docker-server=https://index.docker.io/v1/ \
--docker-username= \
--docker-password= \
--docker-email= 
```

Безопасный вариант:

```bash
read -p "Docker Username: " DOCKER_USERNAME
read -p "Docker Email: " DOCKER_EMAIL
read -s -p "Docker Password: " DOCKER_PASSWORD
echo

kubectl create secret docker-registry regcred \
  --docker-server=https://index.docker.io/v1/ \
  --docker-username="$DOCKER_USERNAME" \
  --docker-password="$DOCKER_PASSWORD" \
  --docker-email="$DOCKER_EMAIL" \
  -n your-namespace
```
Проверить, что точно все добавилось: 
`kubectl get secrets`

После фикса проблема не исчезла, однаок после внимательного рассмотрения Dockerfile выяснилось, что просто не запускался сервер и контейнер самоуничтожался. Поэтому пришлось переделать образ

удаляем поды при помощи `kubectl delete deployment simpsons-deployment`

В minikibe dashboard:
![all pods are running](pics/dashboard.png)

В консольке
```
kaiser@fedora ~/w/r/p/d/kuber (main) [1]> kubectl get pods                                                     (base) 
NAME                                   READY   STATUS    RESTARTS   AGE
simpsons-deployment-6ccc7c7d9d-ctdhd   1/1     Running   0          7m15s
simpsons-deployment-6ccc7c7d9d-mr9sc   1/1     Running   0          7m15s
simpsons-deployment-6ccc7c7d9d-sd2sj   1/1     Running   0          7m15s
```
Добавляем сервис:

`kubectl apply -f service.yaml`
Смотрим сервисы через `kubectl get service`
```bash
NAME               TYPE        CLUSTER-IP      EXTERNAL-IP   PORT(S)        AGE
kubernetes         ClusterIP   10.96.0.1       <none>        443/TCP        29d
simpsons-service   NodePort    10.103.249.33   <none>        80:30756/TCP   20m
```
Так как не был указан NodePort, он был выдан случайно. Зафиксируем его и перезапустим:
```bash
kaiser@fedora ~/w/r/p/d/kuber (main)> kubectl delete service simpsons-service                                  (base) 
service "simpsons-service" deleted
kaiser@fedora ~/w/r/p/d/kuber (main)> kubectl apply -f service.yaml                                            (base) 
service/simpsons-service created 
```

# Демонстрация работы модели
Доступ к серверу через `http:"minikube ip":30080`

Я использую swagger api для простоты
![swagger ](<pics/swagger.png>)
![everything works fine](pics/prediction.png)

Завершаем работу : `minikube stop`

```bash
✋  Stopping node "minikube"  ...
🛑  Powering off "minikube" via SSH ...
🛑  1 node stopped.
```

Или `minikube delete`, чтобы вообще удалить кластер

# LoadBalancer

```bash
NAME               TYPE           CLUSTER-IP     EXTERNAL-IP   PORT(S)        AGE
kubernetes         ClusterIP      10.96.0.1      <none>        443/TCP        2d1h
simpsons-service   LoadBalancer   10.103.71.31   <pending>     80:30737/TCP   8m16s
```

Чтобы задать external-ip
```bash
minikube service simpsons-service --url
```
Для получения external-ip, при помощи которого мы будем обращаться к сервису


Можно через туннелирование
```bash
󰣛 kaiser …/kuber   main   base   20:37  ❯ minikube tunnel 
[sudo] password for kaiser: 
Status:	
	machine: minikube
	pid: 98730
	route: 10.96.0.0/12 -> 192.168.49.2
	minikube: Running
	services: [simpsons-service]
    errors: 
		minikube: no errors
		router: no errors
		loadbalancer emulator: no errors
```

Добавляем Ingress, [ссылка на yaml](ingress.yaml)

```bash
minikube addons enable ingress
💡  ingress is an addon maintained by Kubernetes. For any concerns contact minikube on GitHub.
You can view the list of minikube maintainers at: https://github.com/kubernetes/minikube/blob/master/OWNERS
    ▪ Using image registry.k8s.io/ingress-nginx/controller:v1.12.2
    ▪ Using image registry.k8s.io/ingress-nginx/kube-webhook-certgen:v1.5.3
    ▪ Using image registry.k8s.io/ingress-nginx/kube-webhook-certgen:v1.5.3
```

```bash
󰣛 kaiser …/kuber   main !?   base   21:35  ❯ kubectl get ingress

NAME               CLASS   HOSTS   ADDRESS        PORTS   AGE
simpsons-ingress   nginx   *       192.168.49.2   80      114s

󰣛 kaiser …/kuber   main !?   base   21:35  ❯ kubectl get pods -n ingress-nginx

NAME                                       READY   STATUS      RESTARTS   AGE
ingress-nginx-admission-create-wlv4k       0/1     Completed   0          14m
ingress-nginx-admission-patch-wnt8p        0/1     Completed   1          14m
ingress-nginx-controller-67c5cb88f-x8t2f   1/1     Running     0          14m

󰣛 kaiser …/kuber   main !?   base   21:36  ❯ kubectl get svc -n ingress-nginx
NAME                                 TYPE        CLUSTER-IP       EXTERNAL-IP   PORT(S)                      AGE
ingress-nginx-controller             NodePort    10.106.149.88    <none>        80:30653/TCP,443:31330/TCP   16m
ingress-nginx-controller-admission   ClusterIP   10.105.203.182   <none>        443/TCP  

󰣛 kaiser …/kuber   main !?   base   21:37  ❯ minikube service ingress-nginx-controller -n ingress-nginx
|---------------|--------------------------|-------------|---------------------------|
|   NAMESPACE   |           NAME           | TARGET PORT |            URL            |
|---------------|--------------------------|-------------|---------------------------|
| ingress-nginx | ingress-nginx-controller | http/80     | http://192.168.49.2:30653 |
|               |                          | https/443   | http://192.168.49.2:31330 |
|---------------|--------------------------|-------------|---------------------------|
[ingress-nginx ingress-nginx-controller http/80
https/443 http://192.168.49.2:30653
http://192.168.49.2:31330]

```

# Установка Airflow

Рекомендуется скачать uv

Для fish (осторожно с `export`, у меня на этапе constraint url валилось) процесс будет выглядеть так
```bash
uv python install 3.10
uv venv
set -x AIRFLOW_VERSION 2.9.1
set -x PYTHON_VERSION 3.10
set -x CONSTRAINT_URL https://raw.githubusercontent.com/apache/airflow/constraints-$AIRFLOW_VERSION/constraints-$PYTHON_VERSION.txt
uv pip install -r requirements.txt --constraint "$CONSTRAINT_URL"
```