<img width="10%" alt="gwas_icon" src="https://www.ebi.ac.uk/gwas/images/GWAS_Catalog_circle_178x178.png" 
alt="GWAS logo" />
## gwasdepo-rest-api
Refactored repo for Goci rest api to move away from Spring Data rest to microservices which can be customized. API uses spring Jpa query DSL for
filtering reducing the lines of code required with JPA repository methods . API has been documented using Open API Swagger. Api supports as new 
feature of filtering based on child traits for a parent efo term . This need prepopulating parent child efo mapping & assigning parent term for 
association & studies . The pre-population logic is implemented using the below components

- [gwas-association-parent-trait-executor](https://github.com/EBISPOT/gwas-data-services/tree/master/gwas-association-parent-trait-executor)
- [gwas-association-parent-trait-mapper](https://github.com/EBISPOT/gwas-data-services/tree/master/gwas-association-parent-trait-mapper)

![New-rest-api-architecture.drawio.png](./src/main/resources/static/New-rest-api-architecture.drawio.png)




## Requirements

Before you begin, ensure you have met the following requirements:

- You have a MacOSX/Linux/Windows machine.
- You have Java 8 installed.   

## Deploying this service locally
1. Install Java and JDK8 
2. Clone the application from https://github.com/EBISPOT/gwas-rest-api.git
3. Run `mvn clean install` to build the application and generate executable jar 
4. The application uses default profile as `local`
5. java -Dspring.datasource.username=**** -Dspring.datasource.password=****** -jar gwas-rest-api-*.jar


## Running from Intellij 

1. After step 2 above 
2. Go to Run > Edit Configurations 
3. A dialog box will appear. 
4. Insert in the VM Options text field: java -Dspring.datasource.username=**** -Dspring.datasource.password=******
5. Access the app on url: localhost:{port}/gwas/rest/api/swagger-ui/index.html#


### Contributing

Submitting changes to the data follows this workfow:

1. Create a branch with using issue number and brief issue description using [kebab-case](https://medium.com/better-programming/string-case-styles-camel-pascal-snake-and-kebab-case-981407998841), eg. `git checkout -b 'goci-rest-71-rest-api-documentation'`
1. Do the work to fix the issue or add a new feature and commit message as appropriate
    - Summarize the change in less than 50 characters
    - Because: - Explain the reasons you made this change
    - Make a new bullet for each reason - Each line should be under 72 characters
    - Explain exactly what was done in this commit with more depth than the 50 character subject line. Remember to wrap at 72 characters!
1. Push local changes to the remote feature branch
1. Create a Pull Request to merge the updates in the feature branch into `develop` branch
1. Once the changes are merged into `develop` branch, the Gitlab plan will automatically deploy these changes to the Kubernetes sandbox environment where User Acceptance Testing can be done
1. When the UAT is completed successfully, the updates in `develop` can be merged into `master`, either through a Pull Request or using git merge from your local repo


### Contributors

- Check the contribution section [here](https://github.com/EBISPOT/gwas-rest-api/graphs/contributors)

### Troubleshooting

If something goes wrong, please check the logs.
