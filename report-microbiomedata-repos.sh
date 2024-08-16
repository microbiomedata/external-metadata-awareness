gh repo list microbiomedata --limit 1000 --json name,visibility,isPrivate,isFork,isArchived | \
jq -r '(["name","visibility","isPrivate","isFork","isArchived"]),
       (.[] | [.name, .visibility, (.isPrivate|tostring), (.isFork|tostring), (.isArchived|tostring)])
       | @csv'
