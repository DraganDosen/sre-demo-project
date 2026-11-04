# SRE Demo Project

FastAPI aplikacija + Docker + Terraform + Azure Container Apps. Portfolio projekat koji pokazuje kompletan DevOps tok: kod → testovi → image → cloud → metrike.

## Struktura

```
app/            FastAPI aplikacija (/api/health, /api/users, /api/orders, /metrics)
tests/          pytest testovi
terraform/      Azure infrastruktura (RG, ACR, Container Apps)
k8s/            Kubernetes manifesti (opciona faza 2)
Dockerfile      Image za aplikaciju
```

## 1. Lokalno pokretanje

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r app/requirements.txt pytest httpx
uvicorn app.main:app --reload
```

App je na http://127.0.0.1:8000 — dokumentacija na `/docs`, metrike na `/metrics`.

Testovi:

```powershell
pip install pytest httpx
pytest tests/ -v
```

## 2. Docker lokalno

```powershell
docker build -t dragan-api .
docker run -p 8000:8000 dragan-api
```

## 3. Deploy na Azure (bez gita)

Potrebno: besplatan Azure nalog, [Azure CLI](https://aka.ms/installazurecliwindows) i [Terraform](https://developer.hashicorp.com/terraform/install).

```powershell
az login

cd terraform
terraform init
terraform plan
terraform apply
```

Terraform podiže: Resource Group, Container Registry (ACR), Log Analytics i Container App (scale-to-zero, plaćaš samo dok radi).

Zapamti output vrednosti (`app_url`, `acr_login_server`).

### Build i push image-a

```powershell
# iz root foldera projekta
$ACR = terraform -chdir=terraform output -raw acr_login_server

az acr login --name ($ACR.Split('.')[0])
docker build -t "$ACR/sre-demo-api:latest" .
docker push "$ACR/sre-demo-api:latest"

# deploy nove verzije na Container App
$APP = terraform -chdir=terraform output -raw container_app_name
$RG  = terraform -chdir=terraform output -raw resource_group
az containerapp update --name $APP --resource-group $RG --image "$ACR/sre-demo-api:latest"
```

Alternativa bez lokalnog Dockera — Azure sam build-uje iz source-a:

```powershell
az containerapp up --name $APP --resource-group $RG --source .
```

### Provera (smoke test posle deploy-a)

```powershell
curl "$(terraform -chdir=terraform output -raw app_url)/api/health"
```

## 4. Monitoring i alerting

- App izlaže Prometheus metrike na `/metrics`: request count, response time, 5xx greške.
- CPU/memoriju vidiš odmah: Azure Portal → Container App → Monitoring (ili Log Analytics upiti).
- Alert primer (Azure Monitor): metric alert na Container App — `Requests` ili prosrečno vreme odgovora > 2s → akcija email/SMS.
- Puni Prometheus + Grafana stack dolazi uz Kubernetes fazu (faza 2).

## 5. Faza 2 (kasnije, košta više)

- **Kubernetes (AKS)**: manifesti su spremni u `k8s/` — treba ti AKS klaster (~skuplje, radi non-stop).
- **GitHub Actions**: CI/CD pipeline (build → test → push → deploy) kad ubaciš repo na GitHub.
- **Grafana + Prometheus**: Helm chart na AKS, Grafana dashboard sa metrikama iz `/metrics`.

## Brisanje svega (da ne plaćaš)

```powershell
cd terraform
terraform destroy
```
