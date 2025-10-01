# The Monarch Hippo

## Introduction

This is a search browser written in React JS to provide a user interface for Phenomics backend services (Phantom). The browser's core functionalities are:

1: Search biomedical entities in PubMed abstracts annotated by Phantom. Currently there are 4 types of entities supported (GENE, PHENOTYPE, DISEASE, DRUG)

2: Once search brings back the results, displaying all abstracts with highlighted annotations, PubMedID, Title and Author information.

3: Collecting all other annotations present in search abstracts and treat them as a filter.

4: Feedback for annotation quality

5: Subscription for search items

Following are dev and prod URL for backend:

Dev: https://phenomics-dev.kccg.garvan.org.au/search-engine/

Prod: https://phenomics.kccg.garvan.org.au/search-engine/

## Setup

### Environment

Node and NPM are required to build and run this app locally.

On Mac this can be done achieved using homebrew

`brew update`

`brew install node`

Once done, you can check the versions to make sure installation is done properly:

`node -v`

`npm -v`

### Build

Build process is fairly simple, a backend service url is needed with build command.

`REACT_APP_BASE_URL=https://phenomics-dev.kccg.garvan.org.au/search-engine/ npm run build`

This will create a build folder, which is the complete app and can be accessed with `index.html` page.

### Deployed Application

Currently the application is deployed on an ECS cluster and can be accessed with following URLS:
Production: https://hippo.monarchinitiative.org/#/
Alias: https://phenomics.kccg.garvan.org.au/hippo/#/

Dev: https://phenomics-dev.kccg.garvan.org.au/hippo/#/

It is advisable to move the deployments to Monarch servers in order to keep them running seamlessly.

### Backend APIs

Here are a bunch of backend APIs along with sample input/output:

Only prod links are listed here, the host prefix should be

https://phenomics.kccg.garvan.org.au/search-engine/

#### 1 Auto Complete

`GET /query/autocomplete/{infix}`

##### Input: A case insensitive string to fetch matches from all 4 ontologies.

##### Response:

```javascript
[
  {
    id: "string",
    rank: 0,
    text: "string",
    type: "string"
  }
];
```

#### 2 Search

`POST /query/`

##### Input:

**params**: pageSize, pageNo, includeHistorical

**body**:

```javascript

{
  "filterItems": [
    "string"
  ],
  "queryId": "string",
  "searchItems": [
    "string"
  ]
}
```
**Example**: https://phenomics.kccg.garvan.org.au/search-engine/query/?pageSize=10&pageNo=1&includeHistorical=false
```{
  "searchItems": [
    "1100"
  ]
}
```


##### Response:

```javascript
{
  "articles": [
    {
      "annotations": [
        {
          "endIndex": 0,
          "highlights": [
            {
              "description": "string",
              "feedbackId": "string",
              "id": "string",
              "link": "string",
              "standard": "string",
              "text": "string",
              "type": "string"
            }
          ],
          "startIndex": 0
        }
      ],
      "articleAbstract": "string",
      "articleRank": 0,
      "articleTitle": "string",
      "authors": [
        {
          "foreName": "string",
          "initials": "string",
          "lastName": "string"
        }
      ],
      "datePublished": "string",
      "language": "string",
      "pmid": 0,
      "publication": {
        "isoAbbreviation": "string",
        "issnNumber": "string",
        "issnType": "string",
        "title": "string",
        "validKey": true
      }
    }
  ],
  "filters": [
    {
      "articleCount": 0,
      "filteredArticleCount": 0,
      "id": "string",
      "rank": 0,
      "text": "string",
      "type": "string"
    }
  ],
  "pagination": {
    "includeHistorical": true,
    "pageNo": 0,
    "pageSize": 0,
    "totalArticles": 0,
    "totalPages": 0
  },
  "query": {
    "filterItems": [
      {
        "id": "string",
        "text": "string",
        "type": "string"
      }
    ],
    "queryId": "string",
    "searchItems": [
      {
        "id": "string",
        "text": "string",
        "type": "string"
      }
    ]
  }
}

```



#### 3 Subscription

`POST /subscription`

`GET /subscription`

`GET /subscription/{subscriptionId}`

`DELETE /subscription/{subscriptionId}`


##### Input:

**body**:

```javascript

{
  "digestFrequencyInDays": 0,
  "emailId": "string",
  "query": {
    "filterItems": [
      "string"
    ],
    "queryId": "string",
    "searchItems": [
      "string"
    ]
  },
  "searchName": "string",
  "subscriptionId": "string"
}

```

#### 4 Feedback

`POST /feedback`


##### Input:
Feedback ID is provided with each annotation in the articles result. Value of feedback can be "good" or "bad".

**body**:

```javascript

{
   "feedback": "string",
   "feedbackId": "string"
}

```






