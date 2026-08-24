# Helm and Kustomize

Match whatever the project already uses. Both solve environment variation; running
both in one repository means every change has two possible homes and reviewers guess.

## Helm chart layout

```text
mychart/
├── Chart.yaml          # metadata, version, dependencies
├── values.yaml         # defaults
├── values-dev.yaml     # environment overrides
├── values-prod.yaml
├── templates/
│   ├── _helpers.tpl    # name and label helpers
│   ├── deployment.yaml
│   ├── service.yaml
│   ├── ingress.yaml
│   ├── hpa.yaml
│   ├── pdb.yaml
│   └── configmap.yaml
└── charts/             # subchart dependencies
```

## values.yaml conventions

```yaml
replicaCount: 2

image:
  repository: myapp
  tag: ""              # set by CI, never committed here
  pullPolicy: IfNotPresent

resources:
  requests:
    memory: "256Mi"
    cpu: "100m"
  limits:
    memory: "512Mi"

autoscaling:
  enabled: true
  minReplicas: 2
  maxReplicas: 10
```

- **Never commit an image tag.** `tag: ""` defaulting to the chart's `appVersion`, with
  CI passing the real tag, is what keeps the chart version and the image version from
  drifting apart.
- **Name resources with a helper** — `{{ include "mychart.fullname" . }}` — so two
  releases of the same chart in one namespace do not collide.
- **Structured defaults with feature toggles** (`autoscaling.enabled`) rather than
  separate templates per environment.
- **Defaults should be safe, not minimal.** Someone will install the chart with no
  values file; that install should be production-shaped, not a single replica with no
  probes.

## Kustomize layout

```text
k8s/
├── base/
│   ├── kustomization.yaml
│   ├── deployment.yaml
│   └── service.yaml
└── overlays/
    ├── dev/
    │   ├── kustomization.yaml
    │   └── patch-replicas.yaml
    └── prod/
        ├── kustomization.yaml
        ├── patch-replicas.yaml
        └── hpa.yaml
```

Keep `base/` deployable on its own, and keep overlays to genuine differences —
replica counts, resource sizes, ingress hosts, and resources that exist in only one
environment. An overlay that patches most fields of the base means the base is wrong.

Prefer strategic-merge patches for changing fields and JSON patches only for list
surgery, which is where Kustomize gets hard to read.

## Choosing

| Situation | Use |
| :-- | :-- |
| Already in the project | That one |
| Distributing to other teams or clusters | Helm — it has versioning and a dependency model |
| Internal app, a few environments, no distribution | Kustomize — no templating language to debug |
| Chart from a vendor needing local changes | Helm, with a Kustomize post-render only if unavoidable |

## Validation

- `helm template . -f values-prod.yaml` and read the output — templating errors that
  produce valid-but-wrong YAML are the common failure.
- `helm lint`, and `kubectl apply --dry-run=server` on the rendered output.
- `kustomize build overlays/prod` for the Kustomize equivalent.
- `helm diff upgrade` before any upgrade to an existing release.
