# Kubernetes / Helm Deployment

A complete Helm chart is included in `deploy/helm/hallucination-guard/`.

## Install

```bash
helm install hallucination-guard deploy/helm/hallucination-guard \
  --namespace ai-safety \
  --create-namespace \
  --set replicaCount=2 \
  --set persistence.enabled=true
```

## Key Values

| Value | Default | Description |
|-------|---------|-------------|
| `replicaCount` | `1` | Number of replicas |
| `image.repository` | `ghcr.io/certainlogicai/hallucination-guard` | Image |
| `image.tag` | `latest` | Image tag |
| `persistence.enabled` | `false` | Enable PVC for cache |
| `persistence.size` | `1Gi` | PVC size |
| `resources.requests.memory` | `256Mi` | Memory request |
| `resources.requests.cpu` | `100m` | CPU request |
| `service.port` | `8000` | Service port |

## Custom Facts Database

Mount your facts DB via ConfigMap:

```bash
kubectl create configmap facts-db \
  --from-file=facts_db.json=./my_company_facts.json \
  --namespace ai-safety
```

Then set in values:

```yaml
factsDb:
  configMap: facts-db
```

## High Availability

For production, run at least 2 replicas behind the service:

```yaml
replicaCount: 3
resources:
  requests:
    memory: "512Mi"
    cpu: "250m"
  limits:
    memory: "2Gi"
    cpu: "1"
```

Each replica maintains its own cache. Cache hits improve over time per pod.
