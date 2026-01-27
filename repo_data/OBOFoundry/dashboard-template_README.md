# How to use this template

Please refer to [this page](https://oboacademy.github.io/obook/howto/deploy-custom-obo-dashboard/) on the OBO Academy website.

# Template repository to create Custom OBO Foundry Dashboard

Custom configuration at `dashboard-config.yml`

```yaml
...
ontologies:
  custom:
    - id: Ontology id
      mirror_from: Link to the OWL file in your repository.
      title: Ontology's title
      contact: 
        email: 
        label: 
        orcid: 
        github: 
      description: Ontology's description
      domain: Ontology's domain
      homepage: Ontology's page
      products:
        - id: 
      dependencies:
        - id: 
      tracker: Link to ontology's issue tracker
      license:
        url: License's url
        label: License's label
      preferredPrefix:
      base_ns: Base namespaces
```

# How to update your version of this template

We don't plan to make big changes on this template anymore. The only important change we did was to update the Docker image used in the [GitHub Action](https://github.com/OBOFoundry/dashboard-template/blob/ddde5f42bb2638ed3b07e781923a2a7e3285cc31/.github/workflows/dashboard.yaml#L13-L15
) that updates the dashboard.

```yaml
dashboard:
    runs-on: ubuntu-latest
    container: anitacaron/obo-dashboard:latest
```

The easiest way to update your repository is to do so manually. Please update the Docker image to have the latest changes on the OBO Dashboard.

## If the GitHub Action is failing...

1. We experienced a failure on the GitHub Action in the step to create the pull request with the dashboard changes. To fix the issue, please update the `peter-evans/create-pull-request` version to `v6`.

```yaml
 - name: Create Pull Request
   uses: peter-evans/create-pull-request@v6
   with:
    commit-message: Update dashboard run
    title: 'Update dashboard run'
    body: |
        Updates the Custom OBO Dashboard
```
