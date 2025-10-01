# NMDC Issues and Project Management 

This repo is for logging and managing issues in the NMDC repo. To log an issue go [here](https://github.com/microbiomedata/issues/issues). 

Decisions are tracked as [ADRs](https://adr.github.io/) in the [decisions](./decisions/) directory.

Tools related to managing issues are located in the [tools](./tools/) directory.

---

# Guidelines

> Tip: There is a notion that things are generally _read_ more times/by more people, than they are _written_. Spending extra time writing something clearly up front can save readers energy each time they read it.

## GitHub issue labels

### Creating a new label

#### Reusing existing labels

> Note: Members of the `microbiomedata` org that cannot see a list of org-level labels will not be able to follow this guideline.

Before creating a label at the repo level, check whether a similar label already exists at the org level. If one does, create a label having the same name and description as that org-level label. That can make it easier for team members that work on multiple repos to leverage their existing knowledge.

#### Descriptions

When creating a label, **include a description** that you think will make sense to the other people that use that repository. That can make it more likely that team members (including your future self) share a common interpretation of the label.

For example, the label `big` could be interpreted as "Going to take a lot of time", "Involves a lot of data", "Involves something that happens to be abbreviated as B.I.G., such as the BioInformatics Group", etc. Given those potential interpretations, a disambiguating description could be "Impacts the bioinformatics group".

## Creating issues

### Including code snippets

When copy/pasting a code snippet into the issue description, wrap it in a [code fence](https://docs.github.com/en/get-started/writing-on-github/working-with-advanced-formatting/creating-and-highlighting-code-blocks). That can make it easier for people to read.

<table>
<tr>
  <td>Raw code :tired_face:</td>
  <td>Monospaced code :relieved:</td>
  <td>Colored monospaced code :heart_eyes:</td>
</tr>
<tr>
<td>

{
  "id": "string",
  "capability_ids": []
}

</td>
<td>
    
```
{
  "id": "string",
  "capability_ids": []
}
```

</td>
<td>
    
```json
{
  "id": "string",
  "capability_ids": []
}
```

</td>
</tr>
</table>

You can achieve the rightmost version by wrapping the raw code with this (without the `+` signs):

```diff
+ ```json
  {
    "id": "string",
    "capability_ids": []
  }
+ ```
```

Alternatives to `json` include `py` (short for Python), `Makefile`, `yaml`, and all the other language identifiers [listed here](https://github.com/github-linguist/linguist/blob/master/lib/linguist/languages.yml).

### Creating an umbrella issue/meta issue

Sometimes, team members want to create an issue that encapsulates multiple sub-issues. Some team members refer to such an issue as an "umbrella issue" or "[meta issue](https://github.com/dart-lang/sdk/blob/main/docs/Working-with-meta-issues.md)."

When creating such an issue, please add the `meta-issue` label to it.

> Note: The `meta-issue` label does not exist at the org level yet.

Here are some examples of meta issues:

- https://github.com/microbiomedata/nmdc-runtime/issues/577
  - Its constituent issues are all about updating the Runtime to work with the Berkeley schema
- https://github.com/microbiomedata/nmdc-schema/issues/1607
  - Its constituent issues are all about implementing migrators to accommodate Berkeley schema changes
