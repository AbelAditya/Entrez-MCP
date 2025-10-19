#!/usr/bin/env python3
"""
MCP Client for NCBI Entrez
Example client demonstrating how to interact with the Entrez MCP server
"""

import asyncio
import json
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from dotenv import load_dotenv
import os
import sys
from pathlib import Path

from mistralai import Mistral

load_dotenv()

# Initialize AI if API key is available
ai = None
if os.getenv('MISTRAL_KEY'):
    from mistralai import Mistral
    ai = Mistral(api_key=os.getenv('MISTRAL_KEY'))

async def run_client():
    """Run the MCP client to interact with Entrez server"""
    
    # Configure the server connection
    server_params = StdioServerParameters(
        command="python",
        args=["src/backend/server_main.py"],
    )
    print(server_params)
    
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            # Initialize the session#
            print(session)
            await session.initialize()
            
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


async def interactive_mode():
    """Run an interactive client session"""
    
    server_params = StdioServerParameters(
        command="python",
        args=["src/backend/server_main.py"],
    )
    
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            
            print("=== Interactive Entrez MCP Client ===")
            print("Available commands:")
            print("  search <db> <term> - Search a database")
            print("  fetch <db> <id> - Fetch records")
            print("  summary <db> <id> - Get summaries")
            print("  info [db] - Get database info")
            print("  tools - List all tools")
            print("  quit - Exit")
            print()
            
            while True:
                try:
                    cmd = input("entrez> ").strip()
                    if not cmd:
                        continue
                    
                    parts = cmd.split(maxsplit=2)
                    command = parts[0].lower()
                    
                    if command == "quit":
                        break
                    
                    elif command == "tools":
                        tools = await session.list_tools()
                        for tool in tools.tools:
                            print(f"{tool.name}: {tool.description}")
                    
                    elif command == "search" and len(parts) >= 3:
                        db, term = parts[1], parts[2]
                        result = await session.call_tool(
                            "esearch",
                            arguments={"db": db, "term": term, "retmax": 10}
                        )
                        print(result.content[0].text)
                    
                    elif command == "fetch" and len(parts) >= 3:
                        db, uid = parts[1], parts[2]
                        result = await session.call_tool(
                            "efetch",
                            arguments={"db": db, "id": uid}
                        )
                        print(result.content[0].text)
                    
                    elif command == "summary" and len(parts) >= 3:
                        db, uid = parts[1], parts[2]
                        result = await session.call_tool(
                            "esummary",
                            arguments={"db": db, "id": uid}
                        )
                        print(result.content[0].text)
                    
                    elif command == "info":
                        args = {"db": parts[1]} if len(parts) > 1 else {}
                        result = await session.call_tool("einfo", arguments=args)
                        print(result.content[0].text)
                    
                    else:
                        print("Invalid command. Type 'tools' for help.")
                
                except KeyboardInterrupt:
                    print("\nUse 'quit' to exit")
                except Exception as e:
                    print(f"Error: {e}")

async def ai_mode():
    """Run AI-powered client session"""
    if not ai:
        print("Error: MISTRAL_KEY not found. Please set MISTRAL_KEY environment variable.")
        return
    
    server_params = StdioServerParameters(
        command="python",
        args=["src/backend/server/main.py"],
    )

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            # Get available tools from server
            tools_response = await session.list_tools()
            tools = [{"name": tool.name, "description": tool.description} for tool in tools_response.tools]

            prompts = [{
                "role": "system",
                "content": """You are a MCP Client that can access and present info from Entrez toolset. You are to understand what the user is trying to ask and appropriately call a tool provided to you.

For search strings keep the following in mind:
### Field Tags (use [FieldName] after terms):
- [Gene] or [Gene Name] - for gene symbols/names
- [Organism] - for species names
- [Author] - for author names in publications
- [Journal] - for journal names
- [Title] - for article titles
- [Abstract] - search in abstracts
- [MeSH Terms] - Medical Subject Headings
- [Publication Date] or [PDAT] - publication date
- [Protein Name] - for protein searches
- [All Fields] - search all fields (default if no tag)"""
            }]

            print("=== AI-Powered Entrez Client ===")
            print("Ask me anything about biological data!")
            print("Type 'quit()' to exit\n")

            while True:
                try:
                    ques = input("Ques: ")

                    if ques == "quit()":
                        break

                    prompts.append({'role': "user", "content": ques})

                    resp = ai.chat.complete(
                        messages=prompts,
                        model='mistral-large-latest',
                        tools=tools,
                        tool_choice="any",
                        parallel_tool_calls=False,
                    )

                    print(f"AI Response: {resp.choices[0].message.content}")
                    
                except KeyboardInterrupt:
                    print("\nUse 'quit()' to exit")
                except Exception as e:
                    print(f"Error: {e}")

if __name__ == "__main__":
    args = sys.argv[1:]
    
    if len(args) > 0 and args[0] == "--interactive":
        asyncio.run(interactive_mode())
    elif len(args)>0 and args[0] == '--ai':
        asyncio.run(ai_mode())
    else:
        asyncio.run(run_client())