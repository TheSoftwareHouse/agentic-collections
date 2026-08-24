# Ingress and networking

## Controller choice

| Controller | Use when |
| :-- | :-- |
| ingress-nginx | General purpose, widest support, portable across clouds |
| AWS Load Balancer Controller (ALB) | AWS-native, WAF and ACM integration wanted |
| Traefik | Simple setup, automatic HTTPS |
| Gateway API implementation | New cluster, and the tooling supports it |
| Istio or Linkerd gateway | A service mesh is already in use |

Do not introduce a second controller for one service. Two controllers means two TLS
stories, two annotation dialects, and ambiguity about which owns a hostname.

**Gateway API** is the successor to Ingress and is where new capability is landing. For
a greenfield cluster whose controller supports it, prefer it. For an existing cluster
already using Ingress, stay on Ingress — a mixed estate is worse than either.

## Ingress with TLS

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: api-ingress
  annotations:
    nginx.ingress.kubernetes.io/ssl-redirect: "true"
    cert-manager.io/cluster-issuer: "letsencrypt-prod"
spec:
  ingressClassName: nginx
  tls:
    - hosts:
        - api.example.com
      secretName: api-tls
  rules:
    - host: api.example.com
      http:
        paths:
          - path: /
            pathType: Prefix
            backend:
              service:
                name: api
                port:
                  number: 80
```

Notes that save time:

- **Annotations are controller-specific.** An `nginx.ingress.kubernetes.io/*`
  annotation is silently ignored by an ALB controller — no error, just missing
  behavior. Verify annotation names against the controller and version in use.
- **`ingressClassName`**, not the deprecated `kubernetes.io/ingress.class` annotation.
- **cert-manager issues into `secretName`.** The secret does not need to pre-exist, but
  the issuer does, and a `letsencrypt-prod` issuer will rate-limit if the ingress
  churns during testing — use the staging issuer while iterating.
- **`pathType: Prefix`** unless there is a specific reason for `Exact`.

## Network policies

Default Kubernetes networking is flat: every pod can reach every other pod. Network
policies are the only thing that changes that, and they require a CNI that enforces
them — Calico, Cilium, or a cloud equivalent. **On a CNI without enforcement they
apply cleanly and do nothing**, which is a dangerous kind of silence, so confirm
enforcement before relying on one.

The pattern that works: a default-deny ingress policy per namespace, then explicit
allows.

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: default-deny-ingress
spec:
  podSelector: {}
  policyTypes:
    - Ingress
```

Then allow what should work — and remember DNS: a default-deny **egress** policy
without an explicit allow for port 53 to the cluster DNS service breaks name
resolution for every pod in the namespace, which presents as unrelated timeouts.

## Service type

- **ClusterIP** — the default, and correct for anything reached through an ingress.
- **LoadBalancer** — one cloud load balancer per service, each with a monthly cost. A
  handful of these is usually an ingress that should have been shared.
- **NodePort** — development and specific integrations; not a production front door.
