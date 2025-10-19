import json

from client.client import EntrezClient

async def run_client():
    """Run the MCP client to interact with Entrez server"""
    
    # Create client
    client = EntrezClient()
    
    # Use the convenient with_session method
    async def run_examples(session):
        print("Session initialized successfully!")
        
        # List available tools
        print("=== Available Tools ===")
        tools = await session.list_tools()
        for tool in tools.tools:
            print(f"\n{tool.name}:")
            print(f"  {tool.description}")
        
        print("\n" + "="*50)
        
        # Example 1: Search PubMed
        print("\n=== Example 1: Search PubMed for CRISPR articles ===")
        result = await session.call_tool(
            "esearch",
            arguments={
                "db": "pubmed",
                "term": "CRISPR[Title] AND 2024[PDAT]",
                "retmax": 5,
            }
        )
        search_data = json.loads(result.content[0].text)
        print(f"Found {search_data['esearchresult']['count']} results")
        print(f"IDs: {search_data['esearchresult']['idlist']}")
        
        # Get the first ID for further examples
        if search_data['esearchresult']['idlist']:
            first_id = search_data['esearchresult']['idlist'][0]
            
            # Example 2: Get summary of the first article
            print(f"\n=== Example 2: Get summary for PMID {first_id} ===")
            summary = await session.call_tool(
                "esummary",
                arguments={
                    "db": "pubmed",
                    "id": first_id,
                    "retmode": "json",
                }
            )
            summary_data = json.loads(summary.content[0].text)
            doc = summary_data['result'][first_id]
            print(f"Title: {doc.get('title', 'N/A')}")
            print(f"Authors: {', '.join([a['name'] for a in doc.get('authors', [])[:3]])}")
            print(f"PubDate: {doc.get('pubdate', 'N/A')}")
            
            # Example 3: Fetch full abstract
            print(f"\n=== Example 3: Fetch abstract for PMID {first_id} ===")
            abstract = await session.call_tool(
                "efetch",
                arguments={
                    "db": "pubmed",
                    "id": first_id,
                    "rettype": "abstract",
                    "retmode": "text",
                }
            )
            print(abstract.content[0].text[:500] + "...")
        
        # Example 4: Get database information
        print("\n=== Example 4: List all available databases ===")
        info = await session.call_tool(
            "einfo",
            arguments={}
        )
        info_data = json.loads(info.content[0].text)
        print("Available databases:")
        for db in info_data['einforesult']['dblist'][:10]:
            print(f"  - {db}")
        print(f"  ... and {len(info_data['einforesult']['dblist']) - 10} more")
        
        # Example 5: Search across all databases
        print("\n=== Example 5: Search 'COVID-19' across all databases ===")
        global_search = await session.call_tool(
            "egquery",
            arguments={
                "term": "COVID-19",
            }
        )
        # Parse XML response (egquery returns XML)
        print(global_search.content[0].text[:800] + "...")
        
        # Example 6: Search for a gene
        print("\n=== Example 6: Search for TP53 gene ===")
        gene_search = await session.call_tool(
            "esearch",
            arguments={
                "db": "gene",
                "term": "TP53[Gene Name] AND human[Organism]",
                "retmax": 1,
            }
        )
        gene_data = json.loads(gene_search.content[0].text)
        if gene_data['esearchresult']['idlist']:
            gene_id = gene_data['esearchresult']['idlist'][0]
            print(f"Found Gene ID: {gene_id}")
            
            # Get gene summary
            gene_summary = await session.call_tool(
                "esummary",
                arguments={
                    "db": "gene",
                    "id": gene_id,
                }
            )
            gene_sum_data = json.loads(gene_summary.content[0].text)
            gene_info = gene_sum_data['result'][gene_id]
            print(f"Gene: {gene_info.get('name', 'N/A')}")
            print(f"Description: {gene_info.get('description', 'N/A')}")
            print(f"Chromosome: {gene_info.get('chromosome', 'N/A')}")
        
        # Example 7: Find related articles using elink
        print("\n=== Example 7: Find related PubMed articles ===")
        if search_data['esearchresult']['idlist']:
            first_id = search_data['esearchresult']['idlist'][0]
            links = await session.call_tool(
                "elink",
                arguments={
                    "dbfrom": "pubmed",
                    "db": "pubmed",
                    "id": first_id,
                }
            )
            link_data = json.loads(links.content[0].text)
            if 'linksets' in link_data and link_data['linksets']:
                linkset = link_data['linksets'][0]
                if 'linksetdbs' in linkset and linkset['linksetdbs']:
                    related_ids = linkset['linksetdbs'][0].get('links', [])
                    print(f"Found {len(related_ids)} related articles")
                    print(f"First 5 related PMIDs: {related_ids[:5]}")
        
        # Example 8: Fetch protein sequence
        print("\n=== Example 8: Fetch a protein sequence (insulin) ===")
        protein_search = await session.call_tool(
            "esearch",
            arguments={
                "db": "protein",
                "term": "insulin[Protein Name] AND human[Organism]",
                "retmax": 1,
            }
        )
        protein_data = json.loads(protein_search.content[0].text)
        if protein_data['esearchresult']['idlist']:
            protein_id = protein_data['esearchresult']['idlist'][0]
            fasta = await session.call_tool(
                "efetch",
                arguments={
                    "db": "protein",
                    "id": protein_id,
                    "rettype": "fasta",
                    "retmode": "text",
                }
            )
            print(fasta.content[0].text[:300] + "...")
        
        print("\n" + "="*50)
        print("All examples completed successfully!")
    
    # Execute the examples with automatic session management
    await client.with_session(run_examples)
