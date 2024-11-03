##Linux VM configurations for docker

```
sudo apt update
sudo apt install docker.io
docker --version
whoami
sudo usermod -aG docker avannala
docker --version
docker ps
```


### Debug commands for python issues
```
python -c "import numpy; print(numpy.__version__)"

```
#### Merge kubeconfig
```
cp ~/.kube/config ~/.kube/config.bak && KUBECONFIG=~/.kube/config:/Users/avannala/Downloads/kubeconfig*.yml kubectl config view --flatten > /tmp/config && mv /tmp/config ~/.kube/config
```

####
