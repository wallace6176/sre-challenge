# Fast-API app deployment on Kubernetes

## Overview

<p align="justify">This solution tests and deploys a simple Python Fast-API application to Kubernetes. 
I am proposing provisioning the application on Amazon EKS using Github Actions. Simple tests on the application are done with Pytest, the Docker image hosted on Amazon ECR, and the app is packaged into a Helm chart that is deployed using Terraform.
I will also lay out the assumptions and trade-offs made as well as recommendations for improving the solution to be production-ready.</p>

---

## App Deployment
1. Activate the Workflow template by renaming it to pipeline.yaml.
2. Push and merge the code after successful tests.
3. Create a tag and push it to trigger the Docker image build and Terraform apply.
4. On successful deployment, you can access the app by port-forwarding with kubectl as follows: `kubectl port-forward svc/fast-api 8080:8080 -n dev`
5. You can then access the app using curl like so: `curl http://localhost:8080/`

## Components Summary

### 1. Github Actions
- Each push to Github triggers an Actions Workflow, which runs simple tests on the app to verify outputs and return codes.
- On merge and tag, the workflow builds a Docker image and pushes it to a repository on Amazon ECR.
- Additional steps use Terraform to plan a deployment of the app using the Helm provider, and a manually-approved Terraform apply step that performs the deployment.
- For testing, the service can be exposed using kubectl port forwarding. For proper production use, an ingress should be deployed with a valid hostname and TLS certificate.

### 2. EKS Cluster
- The following resources are created as part of the release:
  - The Fast-API deployment with a health check at `/`
  - A LoadBalancer service.

### 3. ExternalDNS + Route53
- ExternalDNS automatically creates an A record in Route53 in the format: `api.internal.eneco.nl`

### 4. Secrets Management
- Secrets such as database credentials and variables like environment or API endpoint are stored Kubernetes secrets and ConfigMaps. For this demo, these resources are pre-configured before the deployment.

### 5. Observability
- I propose a platform-managed Grafana Alloy daemonset and a Prometheus exporter to collect pod metrics and logs and ship to the observability platform in use.
- I would also propose adding the OpenTelemetry Collector library to the app and instrumenting it to collect traces and runtime metrics.

### 6. Cost Awareness
- Push images to an internal image repo to save internet bandwidth during deploy time
- Start with small base image like Alpine
- Size pod resources to reflect hardware constraints on the hardware.
- Use OSS image registry like [Harbor](https://goharbor.io)
- Use [Karpenter](https://karpenter.sh) to launch the right compute nodes for the cluster to support usage spikes while terminating expensive nodes when unneeded.


---

## Assumptions

1. Grafana Alloy Agent is already installed as a daemonset on the cluster, as well as a Prometheus Service Monitor that watches all namespaces.
2. The Github runner has the appropriate IAM permissions to push the image to Amazon ECR and authenticate with the cluster for Terraform to plan and apply the deployment.
3. The following CRDs and platform tools are already installed on the cluster:
	- ExternalDNS
	- External Secrets Operator
	- cert-manager with AWSPCAClusterIssuer integrated with an ACM PCA.
	- Route53 zone for internal.eneco.nl
	- Ingress-Nginx-Controller

## Architecture Deep-Dive
### Trade-offs
#### Github Actions for CI/CD
<p align="justify">I have chosen to use Github Actions for the skeleton CI/CD pipeline because it is already in use at Eneco, therefore fellow team members can improve on it without much friction.</p>
<p align="justify">I have separated app testing and deployment stages. Testing is done on every push, while deployment steps (building the Docker image, Terraform plan and apply) are performed after the branch is merged. 
Terraform apply requires manual approval by running it in an Actions environment. Approvers can be added to this environment, or Code Owners added to the repo who can approve.</p>

#### Source Management and Testing
<p align="justify">I propose that the main branch is protected from force-pushes and deletions. All commits must be made to a feature branch and submitted via a pull request before they can be merged. Pull request approvals should be enforced using Code Owners to encourage good code review.</p>
<p align="justify">On push, I propose for the pipeline to perform code quality checks using a tool like `pylint`. The app should also have well-designed tests with at least 80% coverage. A tool like Sonarqube can also perform security scanning and publish the hygiene of the code.</p>
<p align="justify">These testing and scanning tools should implement code quality gates to ensure security, reliability and maintainability of the app and the platform as a whole.</p>

#### Build and Packaging
<p align="justify">I have proposed building the Docker image and deploying on a Git tag with the `latest` tag added as well. This is to separate app development from releases, so that releases are deliberately done when a new version of the application has been tagged.
Semantic versioning should be used for tags.
I propose to integrate Sysdig or a similar tool to scan the generated Docker image for dependency and OS vulnerabilities.</p>

#### Operational Readiness
<p align="justify">I propose to add Terraform validation to the plan stage to catch minor issues with the configuration. The apply step should be monitored and alerts set up on Kubernetes events to catch any problems with the Helm install.</p>
<p align="justify">An automated Helm rollback step should be added to the pipeline and triggered if the Terraform apply step fails. A message can be sent to the team via Slack or other notification channel.</p>
<p align="justify">The cluster should have observability already in place, with a Grafana Alloy daemonset collecting and shipping logs and a Prometheus Exporter watching all namespaces and collecting and sending pod metrics through Alloy to the LGTM stack.</p>

#### Amazon Kubernetes Service (EKS)
<p align="justify">I have chosen to use EKS for this demo to approximate a production-ready solution. Specific tools like ECR can be substituted with Azure equivalents (Azure Container Registry).</p>

---

## Possible Enhancements
1. Integrate ExternalDNS and Cert-Manager to the Ingress to expose the app via a trusted URL.
2. Integrate Kubernetes External Secrets Operator and sync database passwords to the cluster from a central secrets management solution like AWS Secrets Manager or Hashicorp Vault.

## LLM Use
- I used the GPT-4o model to create an outline of the Python script for the coding assignment in the interest of saving time, after which I improved on it by hand and added the priority scoring function.

## Contributing
Feel free to contribute to this repository! I'm open to collaboration as well, I can be reached at [wallace@wallace-gaturu.com](mailto:wallace@wallace-gaturu.com)
