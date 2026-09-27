# Project Sentinel

A Kubernetes-native cloud security gateway built on Minikube — combines a Web Application Firewall (WAF), Redis-based dynamic IP banning, and NetworkPolicy-enforced pod isolation to protect a backend application.

## Architecture

```
Internet
   │
   ▼
Ingress (nginx)
   │
   ▼
waf-app  ──────►  Redis (dynamic IP ban store)
   │  (regex-based attack filtering)
   ▼
backend-app  (isolated via NetworkPolicy — only reachable from waf-app)
```

## Features

- **WAF Layer** — Regex-based filtering to catch and block malicious requests before they reach the backend.
- **Dynamic IP Banning** — Redis-backed store tracks and bans offending IPs in real time.
- **Network Isolation** — Kubernetes `NetworkPolicy` (enforced via Calico CNI) ensures only `waf-app` can talk to `backend-app`; any other pod is blocked at the network layer.
- **Ingress Routing** — All external traffic enters through an nginx Ingress controller and is routed through the WAF first.

## Tech Stack

- Kubernetes (Minikube)
- Calico CNI (required for NetworkPolicy enforcement)
- Docker
- Python (Flask) — WAF and backend apps
- Redis
- nginx Ingress Controller

## Setup

```bash
# Start Minikube with Calico CNI (needed for NetworkPolicy)
minikube start --cni=calico

# Enable ingress addon
minikube addons enable ingress

# Build and load images into Minikube
docker build -t backend-app:v1 ./backend-app
docker build -t waf-app:v2 ./waf-app
minikube image load backend-app:v1
minikube image load waf-app:v2

# Deploy Redis, backend, WAF and ingress
kubectl apply -f backend-app/redis-deployment.yaml
kubectl apply -f backend-app/deployment.yml
kubectl apply -f waf-app/deployment.yaml
kubectl apply -f backend-app/networkpolicy.yaml
kubectl apply -f backend-app/ingress.yml
```

## Verification

- **NetworkPolicy isolation confirmed**: a test pod without the `waf-app` label timed out when trying to reach `backend-app` directly, confirming that isolation is enforced correctly.
- **Full request flow verified**: `curl` to the Minikube IP successfully traversed ingress → waf-app → backend-app end to end.

## Status

Complete — Calico networking, NetworkPolicy enforcement, WAF filtering, Redis IP banning, and ingress routing are all deployed and verified working.
