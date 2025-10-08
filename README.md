# ENTREZ MCP - V1
This project aims to create a MCP server for the host of API endpoints available as part of Entrez.

## Functionalities
The following Entrez functionality will be added to the current version:-
- `Entrez.esearch`
    - searching for data through the various present at the users disposal
- `Entrez.efetch`
    - allows you to fetch the complete stored information about a specific records through their ids
- `Entrez.esummary`
    - allows you to fetch metadata about fetched records using their ids
- `Entrez.einfo`
    -  provides info related to databases
- `Entrez.elink`
    - checks for the existence of an external or Related Articles link from a list of one or more primary IDs

## `Extrez.esearch`
### Parameters
- db : specify which DB is to be searched
- term: specify term to be searched through the selected DB
    - The term has a certain format to be written to incorporate filters within the search string (Term String Formatting)

### Return Format
Returns an ID list containing all the IDs of all relevant documents/data records. Along with the ID list it returns a lot of meta data about the returned data and query translation.


