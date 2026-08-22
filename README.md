# Plant Catalog

**Overview:**

## Tech Stack

- **Frontend:** JavaScript / CSS / HTML
- **Hosting:** AWS Amplify
- **API Gateway:** AWS API Gateway
- **Backend:** AWS Lambda
- **Database:** DynamoDB
- **Storage:** S3

Amplify hosts the static frontend, which calls API Gateway to invoke Lambda functions. Lambda reads and writes plant records in DynamoDB and plant images in S3. Infrastructure is currently configured manually in the AWS console; a `terraform/` setup is planned.

## Repo Structure

```text
frontend/
  index.html      Add-plant entrypoint
  pages/          plants.html, plant.html
  javascript/     page scripts and API client
  style/          style.css
  img/            static images
backend/
  src/app.py      Lambda handler
  requirements.txt
infra/            Terraform (planned)
docs/             API spec and supporting docs
```

## Functional Requirements

- **F1:** Create new plant entry
- **F2:** View All plant
- **F3:** Update Created Plant
- **F4:** Delete plant record
- **F5:** Record when a plant has been watered
- **F6:** View plant watering history

## Non-Functional Requirements

- **Scalability:** Should support max 5 user
- **Reliablity:** Operations should be successful 90% of the time
- **Performance:** Each action should take no more than 3 secs
- **Monitoring:** Each action should be logged
- **Availability:**
- **Security:**

## System Context Diagram

![System context diagram](system-context.png)

## Container Diagram

![Container diagram](container-diagram.png)
