# #!/usr/bin/env python3
# """
# Skill: Deal Team – Call Transcription & Analysis – Approved
# Version: 1.0.0
# Status: Approved
# Owner: Deal Team
# Last Review: 2024-01-15
# Next Review: 2024-04-15
# Category: connector-backed
# Dependencies: Notch API, Invenias CRM

# MCP Server for Notch Transcription Tool - Claude Integration
# Supports three output destinations: Personal, Company-wide, and Invenias CRM
# """

# import asyncio
# import json
# import logging
# import os
# from datetime import datetime, timedelta
# from typing import Any, Dict, List, Optional
# from uuid import UUID

# import httpx
# from dotenv import load_dotenv
# from mcp.server import Server, NotificationOptions
# from mcp.server.models import InitializationOptions
# import mcp.server.stdio
# import mcp.types as types

# # Microsoft Graph SDK - COMMENTED OUT (requires additional setup)
# # from azure.identity import DeviceCodeCredential
# # from msgraph.core import GraphClient

# load_dotenv()

# logging.basicConfig(level=logging.INFO)
# logger = logging.getLogger(__name__)

# # Configuration
# NOTCH_API_URL = os.getenv("NOTCH_API_URL", "http://localhost:8000")
# # MICROSOFT_TENANT_ID = os.getenv("MICROSOFT_TENANT_ID")  # COMMENTED OUT
# # MICROSOFT_CLIENT_ID = os.getenv("MICROSOFT_CLIENT_ID")  # COMMENTED OUT
# # SHARED_CLAUDE_PROJECT_ID = os.getenv("SHARED_CLAUDE_PROJECT_ID")  # COMMENTED OUT - not a real feature

# # Skill Governance from environment
# SKILL_NAME = os.getenv("SKILL_NAME", "Deal Team – Call Transcription & Analysis – Approved")
# SKILL_VERSION = os.getenv("SKILL_VERSION", "1.0.0")
# SKILL_STATUS = os.getenv("SKILL_STATUS", "approved")
# SKILL_OWNER = os.getenv("SKILL_OWNER", "Deal Team")
# SKILL_REVIEW_DATE = os.getenv("SKILL_REVIEW_DATE", "2024-01-15")

# # Invenias Configuration
# INVENIAS_API_URL = os.getenv("INVENIAS_API_URL", "http://localhost:8000")  # Same as Notch API
# INVENIAS_DEFAULT_CV = os.getenv("INVENIAS_DEFAULT_CV", "false").lower() == "true"


# class NotchMCPTool:
#     """MCP Server for Notch Transcription Tool with Invenias CRM integration"""
    
#     def __init__(self):
#         self.server = Server("notch-transcription-tool")
#         # self.graph_client = None  # COMMENTED OUT
#         self.notch_client = httpx.AsyncClient(timeout=120.0)
#         self.user_context = {}  # Store user preferences per session
        
#         # Track which destination each call was sent to
#         self.destination_tracking = {}  # call_id -> destination
        
#         self._register_tools()
    
#     def get_skill_metadata(self) -> Dict:
#         """Return skill metadata for governance tracking"""
#         return {
#             "skill_name": SKILL_NAME,
#             "version": SKILL_VERSION,
#             "status": SKILL_STATUS,
#             "owner": SKILL_OWNER,
#             "last_review": SKILL_REVIEW_DATE,
#             "next_review": "2024-04-15",
#             "category": "connector-backed",
#             "dependencies": ["Notch API", "Invenias CRM"],
#             "permission_model": "individual_user_auth",
#             "tools_count": 10,  # Including get_skill_info
#             "api_endpoints": {
#                 "notch": NOTCH_API_URL,
#                 "invenias": INVENIAS_API_URL
#             },
#             "description": "Process meeting transcripts, extract insights, and route to Invenias CRM",
#             "available_commands": [
#                 "List my recent calls",
#                 "Process a transcript",
#                 "Get call insights",
#                 "Search transcripts",
#                 "Share to Invenias",
#                 "Search Invenias people",
#                 "Keep personal",
#                 "Generate summary and actions",
#                 "Get destination status"
#             ]
#         }
        
#     def _register_tools(self):
#         """Register all MCP tools with Claude"""
        
#         @self.server.list_tools()
#         async def list_tools() -> List[types.Tool]:
#             return [
#                 # COMMENTED OUT - Requires Microsoft Graph
#                 # types.Tool(
#                 #     name="discover_teams_recordings",
#                 #     description="Discover recent Teams meeting recordings from user's Microsoft 365 environment",
#                 #     inputSchema={
#                 #         "type": "object",
#                 #         "properties": {
#                 #             "days_back": {
#                 #                 "type": "integer",
#                 #                 "description": "Number of days to look back (default: 7)",
#                 #                 "default": 7
#                 #             },
#                 #             "limit": {
#                 #                 "type": "integer", 
#                 #                 "description": "Maximum number of recordings to return",
#                 #                 "default": 20
#                 #             }
#                 #         }
#                 #     }
#                 # ),
#                 types.Tool(
#                     name="get_skill_info",
#                     description="Get governance and metadata information about this skill including owner, version, status, and available commands",
#                     inputSchema={
#                         "type": "object",
#                         "properties": {}
#                     }
#                 ),
#                 types.Tool(
#                     name="process_transcript",
#                     description="Process a transcript through the Notch tool to extract insights, tags, action items, etc.",
#                     inputSchema={
#                         "type": "object",
#                         "properties": {
#                             "call_id": {
#                                 "type": "string",
#                                 "description": "ID of the call to process (from Notch tool)"
#                             },
#                             "source_type": {
#                                 "type": "string",
#                                 "enum": ["notch", "upload"],
#                                 "description": "Source of the transcript",
#                                 "default": "notch"
#                             }
#                         },
#                         "required": ["call_id"]
#                     }
#                 ),
#                 types.Tool(
#                     name="list_recent_calls",
#                     description="List recently processed calls in the Notch tool",
#                     inputSchema={
#                         "type": "object",
#                         "properties": {
#                             "status": {
#                                 "type": "string",
#                                 "enum": ["uploaded", "processing", "analyzed", "failed"],
#                                 "description": "Filter by call status"
#                             },
#                             "limit": {
#                                 "type": "integer",
#                                 "default": 50
#                             }
#                         }
#                     }
#                 ),
#                 types.Tool(
#                     name="get_call_insights",
#                     description="Get detailed insights for a processed call",
#                     inputSchema={
#                         "type": "object",
#                         "properties": {
#                             "call_id": {
#                                 "type": "string",
#                                 "description": "Call ID"
#                             }
#                         },
#                         "required": ["call_id"]
#                     }
#                 ),
#                 # COMMENTED OUT - Company workspace storage not implemented yet
#                 # types.Tool(
#                 #     name="share_to_company_workspace",
#                 #     description="Share a processed transcript to the company-wide workspace",
#                 #     inputSchema={
#                 #         "type": "object",
#                 #         "properties": {
#                 #             "call_id": {
#                 #                 "type": "string",
#                 #                 "description": "Call ID to share"
#                 #             },
#                 #             "notes": {
#                 #                 "type": "string",
#                 #                 "description": "Optional notes about why this is being shared"
#                 #             }
#                 #         },
#                 #         "required": ["call_id"]
#                 #     }
#                 # ),
#                 types.Tool(
#                     name="share_to_invenias",
#                     description="Share a processed transcript to an Invenias person record (CRM)",
#                     inputSchema={
#                         "type": "object",
#                         "properties": {
#                             "call_id": {
#                                 "type": "string",
#                                 "description": "Call ID to share"
#                             },
#                             "person_id": {
#                                 "type": "string",
#                                 "description": "Invenias person ID to attach the transcript to"
#                             },
#                             "person_name": {
#                                 "type": "string",
#                                 "description": "Person's name (for display)"
#                             },
#                             "set_as_default_cv": {
#                                 "type": "boolean",
#                                 "description": "Set this transcript as the default CV for the person",
#                                 "default": False
#                             }
#                         },
#                         "required": ["call_id", "person_id"]
#                     }
#                 ),
#                 types.Tool(
#                     name="search_invenias_people",
#                     description="Search for people in Invenias CRM",
#                     inputSchema={
#                         "type": "object",
#                         "properties": {
#                             "query": {
#                                 "type": "string",
#                                 "description": "Search query (name, email, etc.)"
#                             },
#                             "limit": {
#                                 "type": "integer",
#                                 "description": "Maximum results to return",
#                                 "default": 10
#                             }
#                         },
#                         "required": ["query"]
#                     }
#                 ),
#                 types.Tool(
#                     name="keep_personal",
#                     description="Keep a processed transcript in personal workspace only",
#                     inputSchema={
#                         "type": "object",
#                         "properties": {
#                             "call_id": {
#                                 "type": "string",
#                                 "description": "Call ID to mark as personal"
#                             }
#                         },
#                         "required": ["call_id"]
#                     }
#                 ),
#                 types.Tool(
#                     name="generate_summary_and_actions",
#                     description="Generate executive summary and action items from call insights",
#                     inputSchema={
#                         "type": "object",
#                         "properties": {
#                             "call_id": {
#                                 "type": "string",
#                                 "description": "Call ID"
#                             },
#                             "include_full_analysis": {
#                                 "type": "boolean",
#                                 "description": "Include full analysis in response",
#                                 "default": False
#                             }
#                         },
#                         "required": ["call_id"]
#                     }
#                 ),
#                 types.Tool(
#                     name="search_transcripts",
#                     description="Search across all processed transcripts",
#                     inputSchema={
#                         "type": "object",
#                         "properties": {
#                             "query": {
#                                 "type": "string",
#                                 "description": "Search query"
#                             },
#                             "top_k": {
#                                 "type": "integer",
#                                 "description": "Number of results to return",
#                                 "default": 10
#                             }
#                         },
#                         "required": ["query"]
#                     }
#                 ),
#                 types.Tool(
#                     name="get_destination_status",
#                     description="Check where a processed transcript has been shared",
#                     inputSchema={
#                         "type": "object",
#                         "properties": {
#                             "call_id": {
#                                 "type": "string",
#                                 "description": "Call ID"
#                             }
#                         },
#                         "required": ["call_id"]
#                     }
#                 )
#             ]
        
#         @self.server.call_tool()
#         async def call_tool(name: str, arguments: Any) -> List[types.TextContent]:
#             """Handle tool calls from Claude"""
            
#             try:
#                 if name == "get_skill_info":
#                     result = self.get_skill_metadata()
#                 # COMMENTED OUT - Requires Microsoft Graph
#                 # elif name == "discover_teams_recordings":
#                 #     result = await self.discover_teams_recordings(
#                 #         days_back=arguments.get("days_back", 7),
#                 #         limit=arguments.get("limit", 20)
#                 #     )
#                 elif name == "process_transcript":
#                     result = await self.process_transcript(
#                         call_id=arguments["call_id"],
#                         source_type=arguments.get("source_type", "notch")
#                     )
#                 elif name == "list_recent_calls":
#                     result = await self.list_recent_calls(
#                         status=arguments.get("status"),
#                         limit=arguments.get("limit", 50)
#                     )
#                 elif name == "get_call_insights":
#                     result = await self.get_call_insights(call_id=arguments["call_id"])
#                 # COMMENTED OUT - Company workspace not implemented
#                 # elif name == "share_to_company_workspace":
#                 #     result = await self.share_to_company_workspace(
#                 #         call_id=arguments["call_id"],
#                 #         notes=arguments.get("notes")
#                 #     )
#                 elif name == "share_to_invenias":
#                     result = await self.share_to_invenias(
#                         call_id=arguments["call_id"],
#                         person_id=arguments["person_id"],
#                         person_name=arguments.get("person_name", ""),
#                         set_as_default_cv=arguments.get("set_as_default_cv", False)
#                     )
#                 elif name == "search_invenias_people":
#                     result = await self.search_invenias_people(
#                         query=arguments["query"],
#                         limit=arguments.get("limit", 10)
#                     )
#                 elif name == "keep_personal":
#                     result = await self.keep_personal(call_id=arguments["call_id"])
#                 elif name == "generate_summary_and_actions":
#                     result = await self.generate_summary_and_actions(
#                         call_id=arguments["call_id"],
#                         include_full_analysis=arguments.get("include_full_analysis", False)
#                     )
#                 elif name == "search_transcripts":
#                     result = await self.search_transcripts(
#                         query=arguments["query"],
#                         top_k=arguments.get("top_k", 10)
#                     )
#                 elif name == "get_destination_status":
#                     result = await self.get_destination_status(call_id=arguments["call_id"])
#                 else:
#                     return [types.TextContent(type="text", text=f"Unknown tool: {name}")]
                
#                 return [types.TextContent(type="text", text=json.dumps(result, indent=2))]
                
#             except Exception as e:
#                 logger.exception(f"Error in tool {name}")
#                 return [types.TextContent(type="text", text=f"Error: {str(e)}")]
    
#     # COMMENTED OUT - Requires Microsoft Graph
#     # async def discover_teams_recordings(self, days_back: int = 7, limit: int = 20) -> Dict:
#     #     """Discover Teams recordings from OneDrive/SharePoint via Microsoft Graph"""
#     #     # ... entire function commented out ...
    
#     async def process_transcript(self, call_id: str, source_type: str = "notch") -> Dict:
#         """Process a transcript through Notch tool"""
        
#         try:
#             # Check if call exists
#             call_response = await self.notch_client.get(
#                 f"{NOTCH_API_URL}/api/calls/{call_id}"
#             )
            
#             if call_response.status_code == 404:
#                 return {
#                     "success": False,
#                     "error": "Call not found",
#                     "message": f"Call with ID {call_id} does not exist"
#                 }
            
#             call_data = call_response.json()
            
#             # Check if already analyzed
#             if call_data.get('status') == 'analyzed':
#                 insights = await self.get_call_insights(call_id)
#                 return {
#                     "success": True,
#                     "already_processed": True,
#                     "message": "Call already analyzed",
#                     "call": call_data,
#                     "insights": insights.get('insights')
#                 }
            
#             # Trigger analysis
#             analysis_response = await self.notch_client.post(
#                 f"{NOTCH_API_URL}/api/calls/{call_id}/analyze"
#             )
            
#             if analysis_response.status_code != 200:
#                 return {
#                     "success": False,
#                     "error": f"Analysis failed with status {analysis_response.status_code}",
#                     "message": "Processing failed"
#                 }
            
#             analysis_result = analysis_response.json()
            
#             return {
#                 "success": True,
#                 "message": "Transcript processed successfully",
#                 "call_id": call_id,
#                 "call_title": call_data.get('title'),
#                 "insights": analysis_result.get('insights'),
#                 "interviewee_profile": analysis_result.get('interviewee_profile')
#             }
            
#         except Exception as e:
#             logger.error(f"Processing failed: {e}")
#             return {
#                 "success": False,
#                 "error": str(e),
#                 "message": "Failed to process transcript"
#             }
    
#     async def list_recent_calls(self, status: str = None, limit: int = 50) -> Dict:
#         """List recent calls from Notch tool"""
        
#         try:
#             url = f"{NOTCH_API_URL}/api/calls?limit={limit}"
#             if status:
#                 url += f"&status={status}"
            
#             response = await self.notch_client.get(url)
            
#             if response.status_code != 200:
#                 return {
#                     "success": False,
#                     "error": f"Failed to list calls: {response.status_code}",
#                     "calls": []
#                 }
            
#             calls = response.json()
            
#             # Enhance with destination info
#             enhanced_calls = []
#             for c in calls:
#                 call_info = {
#                     "id": c['id'],
#                     "title": c['title'],
#                     "date": c.get('call_date'),
#                     "status": c.get('status'),
#                     "has_insights": c.get('status') == 'analyzed'
#                 }
                
#                 # Add destination info if tracked
#                 if c['id'] in self.destination_tracking:
#                     call_info["destinations"] = self.destination_tracking[c['id']]
                
#                 enhanced_calls.append(call_info)
            
#             return {
#                 "success": True,
#                 "total": len(enhanced_calls),
#                 "calls": enhanced_calls
#             }
            
#         except Exception as e:
#             logger.error(f"Failed to list calls: {e}")
#             return {
#                 "success": False,
#                 "error": str(e),
#                 "calls": []
#             }
    
#     async def get_call_insights(self, call_id: str) -> Dict:
#         """Get detailed insights for a call"""
        
#         try:
#             # Get insights
#             insights_response = await self.notch_client.get(
#                 f"{NOTCH_API_URL}/api/calls/{call_id}/insights"
#             )
            
#             if insights_response.status_code != 200:
#                 return {
#                     "success": False,
#                     "error": "Insights not found",
#                     "message": "Call may not have been analyzed yet"
#                 }
            
#             insights = insights_response.json()
            
#             # Get basic call info
#             call_response = await self.notch_client.get(
#                 f"{NOTCH_API_URL}/api/calls/{call_id}"
#             )
#             call_data = call_response.json() if call_response.status_code == 200 else {}
            
#             return {
#                 "success": True,
#                 "call_id": call_id,
#                 "title": call_data.get('title'),
#                 "date": call_data.get('call_date'),
#                 "status": call_data.get('status'),
#                 "insights": insights.get('insights', {}),
#                 "interviewee_profile": insights.get('interviewee_profile')
#             }
            
#         except Exception as e:
#             logger.error(f"Failed to get insights: {e}")
#             return {
#                 "success": False,
#                 "error": str(e)
#             }
    
#     async def share_to_invenias(self, call_id: str, person_id: str, person_name: str = "", set_as_default_cv: bool = False) -> Dict:
#         """Share processed transcript to Invenias CRM"""
        
#         # First ensure the call has been analyzed
#         insights_data = await self.get_call_insights(call_id)
        
#         if not insights_data.get('success'):
#             return {
#                 "success": False,
#                 "error": "Cannot share to Invenias: Call hasn't been analyzed",
#                 "message": "Please process the transcript first using process_transcript"
#             }
        
#         try:
#             # Call the existing Invenias endpoint in your Notch API
#             invenias_response = await self.notch_client.post(
#                 f"{INVENIAS_API_URL}/api/invenias/post",
#                 json={
#                     "call_id": call_id,
#                     "person_id": person_id
#                 }
#             )
            
#             if invenias_response.status_code != 200:
#                 return {
#                     "success": False,
#                     "error": f"Invenias sharing failed with status {invenias_response.status_code}",
#                     "message": invenias_response.json().get('message', 'Unknown error')
#                 }
            
#             invenias_result = invenias_response.json()
            
#             # Track this destination
#             if call_id not in self.destination_tracking:
#                 self.destination_tracking[call_id] = []
#             if "invenias" not in self.destination_tracking[call_id]:
#                 self.destination_tracking[call_id].append("invenias")
            
#             # Prepare a summary of what was shared for the response
#             insights = insights_data.get('insights', {})
#             share_summary = {
#                 "person_id": person_id,
#                 "person_name": person_name or invenias_result.get('person_name', 'Unknown'),
#                 "set_as_default_cv": set_as_default_cv,
#                 "shared_at": datetime.now().isoformat(),
#                 "call_title": insights_data.get('title'),
#                 "key_insights": {
#                     "summary": (insights.get('executive_summary') or insights.get('summary', ''))[:200],
#                     "action_items_count": len(insights.get('action_items', [])),
#                     "people_mentioned_count": len(insights.get('people_mentioned', [])),
#                     "tags": insights.get('tags', [])[:5]
#                 }
#             }
            
#             return {
#                 "success": True,
#                 "message": f"Transcript successfully shared to Invenias for {person_name or person_id}",
#                 "destination": "invenias",
#                 "share_details": share_summary,
#                 "invenias_response": invenias_result
#             }
            
#         except Exception as e:
#             logger.error(f"Invenias sharing failed: {e}")
#             return {
#                 "success": False,
#                 "error": str(e),
#                 "message": "Failed to share to Invenias"
#             }
    
#     async def search_invenias_people(self, query: str, limit: int = 10) -> Dict:
#         """Search for people in Invenias CRM"""
        
#         try:
#             response = await self.notch_client.get(
#                 f"{INVENIAS_API_URL}/api/invenias/search",
#                 params={"query": query}
#             )
            
#             if response.status_code != 200:
#                 return {
#                     "success": False,
#                     "error": f"Search failed with status {response.status_code}",
#                     "people": []
#                 }
            
#             people = response.json()
            
#             # Limit results
#             if len(people) > limit:
#                 people = people[:limit]
            
#             return {
#                 "success": True,
#                 "query": query,
#                 "total_results": len(people),
#                 "people": [
#                     {
#                         "id": p.get('id'),
#                         "name": p.get('name'),
#                         "email": p.get('email'),
#                         "title": p.get('title'),
#                         "company": p.get('company')
#                     }
#                     for p in people
#                 ]
#             }
            
#         except Exception as e:
#             logger.error(f"Invenias search failed: {e}")
#             return {
#                 "success": False,
#                 "error": str(e),
#                 "people": []
#             }
    
#     # COMMENTED OUT - Company workspace not implemented
#     # async def share_to_company_workspace(self, call_id: str, notes: str = None) -> Dict:
#     #     """Share transcript to company-wide workspace"""
#     #     # ... entire function commented out ...
    
#     # def _format_shareable_content(self, insights_data: Dict, notes: str = None) -> str:
#     #     """Format content for company-wide sharing"""
#     #     # ... entire function commented out ...
    
#     async def keep_personal(self, call_id: str) -> Dict:
#         """Mark transcript as personal (not shared to company or Invenias)"""
        
#         # Track this destination
#         if call_id not in self.destination_tracking:
#             self.destination_tracking[call_id] = []
#         if "personal" not in self.destination_tracking[call_id]:
#             self.destination_tracking[call_id].append("personal")
        
#         return {
#             "success": True,
#             "message": f"Transcript {call_id} kept as personal",
#             "visibility": "personal"
#         }
    
#     async def generate_summary_and_actions(self, call_id: str, include_full_analysis: bool = False) -> Dict:
#         """Generate human-readable summary and action items from insights"""
        
#         insights_data = await self.get_call_insights(call_id)
        
#         if not insights_data.get('success'):
#             return insights_data
        
#         insights = insights_data.get('insights', {})
        
#         # Format summary
#         summary = {
#             "executive_summary": insights.get('executive_summary') or insights.get('summary', ''),
#             "call_type": insights.get('call_type', 'unknown'),
#             "sentiment": insights.get('sentiment', {}).get('overall', 'neutral'),
#             "key_tags": insights.get('tags', [])[:10],
#             "action_items": [],
#             "follow_up_items": [],
#             "people_mentioned": [],
#             "key_decisions": insights.get('key_decisions', [])
#         }
        
#         # Format action items
#         for item in insights.get('action_items', []):
#             summary["action_items"].append({
#                 "description": item.get('description'),
#                 "owner": item.get('owner'),
#                 "urgency": item.get('urgency', 'medium')
#             })
        
#         # Format follow-ups
#         for item in insights.get('follow_up_items', []):
#             summary["follow_up_items"].append({
#                 "description": item.get('description'),
#                 "owner": item.get('owner'),
#                 "context": item.get('context')
#             })
        
#         # Format people mentioned
#         for person in insights.get('people_mentioned', []):
#             summary["people_mentioned"].append({
#                 "name": person.get('name'),
#                 "role": person.get('role'),
#                 "company": person.get('company')
#             })
        
#         # Generate natural language summary for Claude
#         natural_summary = self._format_natural_summary(summary, insights_data.get('title'))
        
#         result = {
#             "success": True,
#             "call_id": call_id,
#             "summary": summary,
#             "natural_language_summary": natural_summary
#         }
        
#         if include_full_analysis:
#             result["full_insights"] = insights
        
#         return result
    
#     def _format_natural_summary(self, summary: Dict, title: str) -> str:
#         """Format insights as natural language for Claude"""
        
#         lines = []
#         lines.append(f"## Call Summary: {title}\n")
        
#         if summary.get('executive_summary'):
#             lines.append(f"**Executive Summary:** {summary['executive_summary']}\n")
        
#         lines.append(f"**Call Type:** {summary['call_type']}")
#         lines.append(f"**Overall Sentiment:** {summary['sentiment']}\n")
        
#         if summary.get('key_tags'):
#             lines.append(f"**Tags:** {', '.join(summary['key_tags'])}\n")
        
#         if summary.get('action_items'):
#             lines.append("### Action Items")
#             for item in summary['action_items']:
#                 urgency_emoji = {"high": "🔴", "medium": "🟡", "low": "🟢"}.get(item['urgency'], "⚪")
#                 owner_str = f" (Owner: {item['owner']})" if item.get('owner') else ""
#                 lines.append(f"- {urgency_emoji} {item['description']}{owner_str}")
#             lines.append("")
        
#         if summary.get('follow_up_items'):
#             lines.append("### Follow-up Items")
#             for item in summary['follow_up_items']:
#                 owner_str = f" (Owner: {item['owner']})" if item.get('owner') else ""
#                 lines.append(f"- {item['description']}{owner_str}")
#             lines.append("")
        
#         if summary.get('key_decisions'):
#             lines.append("### Key Decisions")
#             for decision in summary['key_decisions']:
#                 lines.append(f"- {decision}")
#             lines.append("")
        
#         if summary.get('people_mentioned'):
#             lines.append("### People Mentioned")
#             for person in summary['people_mentioned']:
#                 context = []
#                 if person.get('role'): context.append(person['role'])
#                 if person.get('company'): context.append(person['company'])
#                 context_str = f" ({', '.join(context)})" if context else ""
#                 lines.append(f"- {person['name']}{context_str}")
        
#         return "\n".join(lines)
    
#     async def search_transcripts(self, query: str, top_k: int = 10) -> Dict:
#         """Search across processed transcripts"""
        
#         try:
#             # Use Notch's search endpoint
#             search_response = await self.notch_client.post(
#                 f"{NOTCH_API_URL}/api/calls/search",
#                 json={"query": query, "top_k": top_k}
#             )
            
#             if search_response.status_code == 200:
#                 results = search_response.json()
#                 # Enhance with destination info
#                 if 'results' in results:
#                     for result in results['results']:
#                         call_id = result.get('id') or result.get('call_id')
#                         if call_id and call_id in self.destination_tracking:
#                             result['destinations'] = self.destination_tracking[call_id]
#                 return results
            
#             # Fallback: search through recent calls
#             calls_data = await self.list_recent_calls(limit=100)
#             results = []
            
#             for call in calls_data.get('calls', []):
#                 if call.get('has_insights'):
#                     insights = await self.get_call_insights(call['id'])
#                     if insights.get('success'):
#                         summary = insights.get('insights', {}).get('summary', '')
#                         if query.lower() in summary.lower():
#                             results.append({
#                                 "call_id": call['id'],
#                                 "title": call['title'],
#                                 "relevance": "title_match",
#                                 "summary_preview": summary[:200],
#                                 "destinations": self.destination_tracking.get(call['id'], [])
#                             })
            
#             return {
#                 "success": True,
#                 "query": query,
#                 "total_results": len(results),
#                 "results": results[:top_k]
#             }
            
#         except Exception as e:
#             logger.error(f"Search failed: {e}")
#             return {
#                 "success": False,
#                 "error": str(e),
#                 "results": []
#             }
    
#     async def get_destination_status(self, call_id: str) -> Dict:
#         """Check where a processed transcript has been shared"""
        
#         destinations = self.destination_tracking.get(call_id, [])
        
#         # If no tracking yet, check if it might have been shared via Notch directly
#         call_data = await self.list_recent_calls(limit=1)
#         call_info = None
#         for call in call_data.get('calls', []):
#             if call['id'] == call_id:
#                 call_info = call
#                 break
        
#         return {
#             "success": True,
#             "call_id": call_id,
#             "destinations": destinations or ["unknown (not tracked)"],
#             "has_been_shared": len(destinations) > 0,
#             "call_status": call_info.get('status') if call_info else "unknown",
#             "suggested_next_steps": self._suggest_next_steps(destinations, call_info)
#         }
    
#     def _suggest_next_steps(self, destinations: List[str], call_info: Dict = None) -> List[str]:
#         """Suggest what the user can do next based on current destinations"""
        
#         suggestions = []
        
#         if "personal" not in destinations and "company" not in destinations and "invenias" not in destinations:
#             suggestions.append("This transcript hasn't been shared anywhere yet. You can:")
#             suggestions.append("- Keep it personal")
#             suggestions.append("- Share to Invenias (attach to a person record)")
#         elif "personal" in destinations and len(destinations) == 1:
#             suggestions.append("This transcript is currently personal only. Consider:")
#             suggestions.append("- Attaching to an Invenias record if this was an interview")
#         elif "invenias" in destinations:
#             suggestions.append("This transcript is attached to an Invenias record.")
        
#         return suggestions
    
#     # COMMENTED OUT - Requires Microsoft Graph
#     # async def _init_graph_client(self):
#     #     """Initialize Microsoft Graph client with device code auth"""
#     #     # ... entire function commented out ...
    
#     async def run(self):
#         """Run the MCP server"""
#         async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
#             await self.server.run(
#                 read_stream,
#                 write_stream,
#                 InitializationOptions(
#                     server_name="notch-transcription-tool",
#                     server_version="1.0.0",
#                     capabilities=self.server.get_capabilities(
#                         notification_options=NotificationOptions(),
#                         experimental_capabilities={}
#                     )
#                 )
#             )


# async def main():
#     tool = NotchMCPTool()
#     await tool.run()


# if __name__ == "__main__":
#     asyncio.run(main())

#!/usr/bin/env python3
"""
Skill: Deal Team – Call Transcription & Analysis – Approved
Version: 1.0.0
Status: Approved
Owner: Deal Team
Last Review: 2024-01-15
Next Review: 2024-04-15
Category: connector-backed
Dependencies: Notch API, Invenias CRM

MCP Server for Notch Transcription Tool - Claude Integration
Supports three output destinations: Personal, Company-wide, and Invenias CRM

HOSTING VERSION: HTTP/SSE Transport for Render/Claude Web
"""

import asyncio
import json
import logging
import os
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional
from uuid import UUID

import httpx
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration
NOTCH_API_URL = os.getenv("NOTCH_API_URL", "http://localhost:8000")
PORT = int(os.getenv("PORT", "8000"))
HOST = os.getenv("HOST", "0.0.0.0")

# Skill Governance from environment
SKILL_NAME = os.getenv("SKILL_NAME", "Deal Team – Call Transcription & Analysis – Approved")
SKILL_VERSION = os.getenv("SKILL_VERSION", "1.0.0")
SKILL_STATUS = os.getenv("SKILL_STATUS", "approved")
SKILL_OWNER = os.getenv("SKILL_OWNER", "Deal Team")
SKILL_REVIEW_DATE = os.getenv("SKILL_REVIEW_DATE", "2024-01-15")

# Invenias Configuration
INVENIAS_API_URL = os.getenv("INVENIAS_API_URL", "http://localhost:8000")
INVENIAS_DEFAULT_CV = os.getenv("INVENIAS_DEFAULT_CV", "false").lower() == "true"

# Optional authentication token for production
MCP_API_TOKEN = os.getenv("MCP_API_TOKEN", "")


class NotchMCPTool:
    """MCP Server for Notch Transcription Tool with Invenias CRM integration"""
    
    def __init__(self):
        self.notch_client = httpx.AsyncClient(timeout=120.0)
        self.user_context = {}
        self.destination_tracking = {}
        self.mcp_server = None
        self.transport = None
        
    def get_skill_metadata(self) -> Dict:
        """Return skill metadata for governance tracking"""
        return {
            "skill_name": SKILL_NAME,
            "version": SKILL_VERSION,
            "status": SKILL_STATUS,
            "owner": SKILL_OWNER,
            "last_review": SKILL_REVIEW_DATE,
            "next_review": "2024-04-15",
            "category": "connector-backed",
            "dependencies": ["Notch API", "Invenias CRM"],
            "permission_model": "individual_user_auth",
            "tools_count": 10,
            "api_endpoints": {
                "notch": NOTCH_API_URL,
                "invenias": INVENIAS_API_URL
            },
            "description": "Process meeting transcripts, extract insights, and route to Invenias CRM",
            "available_commands": [
                "List my recent calls",
                "Process a transcript",
                "Get call insights",
                "Search transcripts",
                "Share to Invenias",
                "Search Invenias people",
                "Keep personal",
                "Generate summary and actions",
                "Get destination status"
            ]
        }
    
    async def process_transcript(self, call_id: str, source_type: str = "notch") -> Dict:
        """Process a transcript through Notch tool"""
        
        try:
            call_response = await self.notch_client.get(
                f"{NOTCH_API_URL}/api/calls/{call_id}"
            )
            
            if call_response.status_code == 404:
                return {
                    "success": False,
                    "error": "Call not found",
                    "message": f"Call with ID {call_id} does not exist"
                }
            
            call_data = call_response.json()
            
            if call_data.get('status') == 'analyzed':
                insights = await self.get_call_insights(call_id)
                return {
                    "success": True,
                    "already_processed": True,
                    "message": "Call already analyzed",
                    "call": call_data,
                    "insights": insights.get('insights')
                }
            
            analysis_response = await self.notch_client.post(
                f"{NOTCH_API_URL}/api/calls/{call_id}/analyze"
            )
            
            if analysis_response.status_code != 200:
                return {
                    "success": False,
                    "error": f"Analysis failed with status {analysis_response.status_code}",
                    "message": "Processing failed"
                }
            
            analysis_result = analysis_response.json()
            
            return {
                "success": True,
                "message": "Transcript processed successfully",
                "call_id": call_id,
                "call_title": call_data.get('title'),
                "insights": analysis_result.get('insights'),
                "interviewee_profile": analysis_result.get('interviewee_profile')
            }
            
        except Exception as e:
            logger.error(f"Processing failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to process transcript"
            }
    
    async def list_recent_calls(self, status: str = None, limit: int = 50) -> Dict:
        """List recent calls from Notch tool"""
        
        try:
            url = f"{NOTCH_API_URL}/api/calls?limit={limit}"
            if status:
                url += f"&status={status}"
            
            response = await self.notch_client.get(url)
            
            if response.status_code != 200:
                return {
                    "success": False,
                    "error": f"Failed to list calls: {response.status_code}",
                    "calls": []
                }
            
            calls = response.json()
            
            enhanced_calls = []
            for c in calls:
                call_info = {
                    "id": c['id'],
                    "title": c['title'],
                    "date": c.get('call_date'),
                    "status": c.get('status'),
                    "has_insights": c.get('status') == 'analyzed'
                }
                
                if c['id'] in self.destination_tracking:
                    call_info["destinations"] = self.destination_tracking[c['id']]
                
                enhanced_calls.append(call_info)
            
            return {
                "success": True,
                "total": len(enhanced_calls),
                "calls": enhanced_calls
            }
            
        except Exception as e:
            logger.error(f"Failed to list calls: {e}")
            return {
                "success": False,
                "error": str(e),
                "calls": []
            }
    
    async def get_call_insights(self, call_id: str) -> Dict:
        """Get detailed insights for a call"""
        
        try:
            insights_response = await self.notch_client.get(
                f"{NOTCH_API_URL}/api/calls/{call_id}/insights"
            )
            
            if insights_response.status_code != 200:
                return {
                    "success": False,
                    "error": "Insights not found",
                    "message": "Call may not have been analyzed yet"
                }
            
            insights = insights_response.json()
            
            call_response = await self.notch_client.get(
                f"{NOTCH_API_URL}/api/calls/{call_id}"
            )
            call_data = call_response.json() if call_response.status_code == 200 else {}
            
            return {
                "success": True,
                "call_id": call_id,
                "title": call_data.get('title'),
                "date": call_data.get('call_date'),
                "status": call_data.get('status'),
                "insights": insights.get('insights', {}),
                "interviewee_profile": insights.get('interviewee_profile')
            }
            
        except Exception as e:
            logger.error(f"Failed to get insights: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def share_to_invenias(self, call_id: str, person_id: str, person_name: str = "", set_as_default_cv: bool = False) -> Dict:
        """Share processed transcript to Invenias CRM"""
        
        insights_data = await self.get_call_insights(call_id)
        
        if not insights_data.get('success'):
            return {
                "success": False,
                "error": "Cannot share to Invenias: Call hasn't been analyzed",
                "message": "Please process the transcript first using process_transcript"
            }
        
        try:
            invenias_response = await self.notch_client.post(
                f"{INVENIAS_API_URL}/api/invenias/post",
                json={
                    "call_id": call_id,
                    "person_id": person_id
                }
            )
            
            if invenias_response.status_code != 200:
                return {
                    "success": False,
                    "error": f"Invenias sharing failed with status {invenias_response.status_code}",
                    "message": invenias_response.json().get('message', 'Unknown error')
                }
            
            invenias_result = invenias_response.json()
            
            if call_id not in self.destination_tracking:
                self.destination_tracking[call_id] = []
            if "invenias" not in self.destination_tracking[call_id]:
                self.destination_tracking[call_id].append("invenias")
            
            insights = insights_data.get('insights', {})
            share_summary = {
                "person_id": person_id,
                "person_name": person_name or invenias_result.get('person_name', 'Unknown'),
                "set_as_default_cv": set_as_default_cv,
                "shared_at": datetime.now().isoformat(),
                "call_title": insights_data.get('title'),
                "key_insights": {
                    "summary": (insights.get('executive_summary') or insights.get('summary', ''))[:200],
                    "action_items_count": len(insights.get('action_items', [])),
                    "people_mentioned_count": len(insights.get('people_mentioned', [])),
                    "tags": insights.get('tags', [])[:5]
                }
            }
            
            return {
                "success": True,
                "message": f"Transcript successfully shared to Invenias for {person_name or person_id}",
                "destination": "invenias",
                "share_details": share_summary,
                "invenias_response": invenias_result
            }
            
        except Exception as e:
            logger.error(f"Invenias sharing failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to share to Invenias"
            }
    
    async def search_invenias_people(self, query: str, limit: int = 10) -> Dict:
        """Search for people in Invenias CRM"""
        
        try:
            response = await self.notch_client.get(
                f"{INVENIAS_API_URL}/api/invenias/search",
                params={"query": query}
            )
            
            if response.status_code != 200:
                return {
                    "success": False,
                    "error": f"Search failed with status {response.status_code}",
                    "people": []
                }
            
            people = response.json()
            
            if len(people) > limit:
                people = people[:limit]
            
            return {
                "success": True,
                "query": query,
                "total_results": len(people),
                "people": [
                    {
                        "id": p.get('id'),
                        "name": p.get('name'),
                        "email": p.get('email'),
                        "title": p.get('title'),
                        "company": p.get('company')
                    }
                    for p in people
                ]
            }
            
        except Exception as e:
            logger.error(f"Invenias search failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "people": []
            }
    
    async def keep_personal(self, call_id: str) -> Dict:
        """Mark transcript as personal"""
        
        if call_id not in self.destination_tracking:
            self.destination_tracking[call_id] = []
        if "personal" not in self.destination_tracking[call_id]:
            self.destination_tracking[call_id].append("personal")
        
        return {
            "success": True,
            "message": f"Transcript {call_id} kept as personal",
            "visibility": "personal"
        }
    
    async def generate_summary_and_actions(self, call_id: str, include_full_analysis: bool = False) -> Dict:
        """Generate human-readable summary and action items from insights"""
        
        insights_data = await self.get_call_insights(call_id)
        
        if not insights_data.get('success'):
            return insights_data
        
        insights = insights_data.get('insights', {})
        
        summary = {
            "executive_summary": insights.get('executive_summary') or insights.get('summary', ''),
            "call_type": insights.get('call_type', 'unknown'),
            "sentiment": insights.get('sentiment', {}).get('overall', 'neutral'),
            "key_tags": insights.get('tags', [])[:10],
            "action_items": [],
            "follow_up_items": [],
            "people_mentioned": [],
            "key_decisions": insights.get('key_decisions', [])
        }
        
        for item in insights.get('action_items', []):
            summary["action_items"].append({
                "description": item.get('description'),
                "owner": item.get('owner'),
                "urgency": item.get('urgency', 'medium')
            })
        
        for item in insights.get('follow_up_items', []):
            summary["follow_up_items"].append({
                "description": item.get('description'),
                "owner": item.get('owner'),
                "context": item.get('context')
            })
        
        for person in insights.get('people_mentioned', []):
            summary["people_mentioned"].append({
                "name": person.get('name'),
                "role": person.get('role'),
                "company": person.get('company')
            })
        
        natural_summary = self._format_natural_summary(summary, insights_data.get('title'))
        
        result = {
            "success": True,
            "call_id": call_id,
            "summary": summary,
            "natural_language_summary": natural_summary
        }
        
        if include_full_analysis:
            result["full_insights"] = insights
        
        return result
    
    def _format_natural_summary(self, summary: Dict, title: str) -> str:
        """Format insights as natural language for Claude"""
        
        lines = []
        lines.append(f"## Call Summary: {title}\n")
        
        if summary.get('executive_summary'):
            lines.append(f"**Executive Summary:** {summary['executive_summary']}\n")
        
        lines.append(f"**Call Type:** {summary['call_type']}")
        lines.append(f"**Overall Sentiment:** {summary['sentiment']}\n")
        
        if summary.get('key_tags'):
            lines.append(f"**Tags:** {', '.join(summary['key_tags'])}\n")
        
        if summary.get('action_items'):
            lines.append("### Action Items")
            for item in summary['action_items']:
                urgency_emoji = {"high": "🔴", "medium": "🟡", "low": "🟢"}.get(item['urgency'], "⚪")
                owner_str = f" (Owner: {item['owner']})" if item.get('owner') else ""
                lines.append(f"- {urgency_emoji} {item['description']}{owner_str}")
            lines.append("")
        
        if summary.get('follow_up_items'):
            lines.append("### Follow-up Items")
            for item in summary['follow_up_items']:
                owner_str = f" (Owner: {item['owner']})" if item.get('owner') else ""
                lines.append(f"- {item['description']}{owner_str}")
            lines.append("")
        
        if summary.get('key_decisions'):
            lines.append("### Key Decisions")
            for decision in summary['key_decisions']:
                lines.append(f"- {decision}")
            lines.append("")
        
        if summary.get('people_mentioned'):
            lines.append("### People Mentioned")
            for person in summary['people_mentioned']:
                context = []
                if person.get('role'): context.append(person['role'])
                if person.get('company'): context.append(person['company'])
                context_str = f" ({', '.join(context)})" if context else ""
                lines.append(f"- {person['name']}{context_str}")
        
        return "\n".join(lines)
    
    async def search_transcripts(self, query: str, top_k: int = 10) -> Dict:
        """Search across processed transcripts"""
        
        try:
            search_response = await self.notch_client.post(
                f"{NOTCH_API_URL}/api/calls/search",
                json={"query": query, "top_k": top_k}
            )
            
            if search_response.status_code == 200:
                results = search_response.json()
                if 'results' in results:
                    for result in results['results']:
                        call_id = result.get('id') or result.get('call_id')
                        if call_id and call_id in self.destination_tracking:
                            result['destinations'] = self.destination_tracking[call_id]
                return results
            
            calls_data = await self.list_recent_calls(limit=100)
            results = []
            
            for call in calls_data.get('calls', []):
                if call.get('has_insights'):
                    insights = await self.get_call_insights(call['id'])
                    if insights.get('success'):
                        summary = insights.get('insights', {}).get('summary', '')
                        if query.lower() in summary.lower():
                            results.append({
                                "call_id": call['id'],
                                "title": call['title'],
                                "relevance": "title_match",
                                "summary_preview": summary[:200],
                                "destinations": self.destination_tracking.get(call['id'], [])
                            })
            
            return {
                "success": True,
                "query": query,
                "total_results": len(results),
                "results": results[:top_k]
            }
            
        except Exception as e:
            logger.error(f"Search failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "results": []
            }
    
    async def get_destination_status(self, call_id: str) -> Dict:
        """Check where a processed transcript has been shared"""
        
        destinations = self.destination_tracking.get(call_id, [])
        
        call_data = await self.list_recent_calls(limit=1)
        call_info = None
        for call in call_data.get('calls', []):
            if call['id'] == call_id:
                call_info = call
                break
        
        return {
            "success": True,
            "call_id": call_id,
            "destinations": destinations or ["unknown (not tracked)"],
            "has_been_shared": len(destinations) > 0,
            "call_status": call_info.get('status') if call_info else "unknown",
            "suggested_next_steps": self._suggest_next_steps(destinations, call_info)
        }
    
    def _suggest_next_steps(self, destinations: List[str], call_info: Dict = None) -> List[str]:
        """Suggest what the user can do next based on current destinations"""
        
        suggestions = []
        
        if "personal" not in destinations and "invenias" not in destinations:
            suggestions.append("This transcript hasn't been shared anywhere yet. You can:")
            suggestions.append("- Keep it personal")
            suggestions.append("- Share to Invenias (attach to a person record)")
        elif "personal" in destinations and len(destinations) == 1:
            suggestions.append("This transcript is currently personal only. Consider:")
            suggestions.append("- Attaching to an Invenias record if this was an interview")
        elif "invenias" in destinations:
            suggestions.append("This transcript is attached to an Invenias record.")
        
        return suggestions
    
    async def run_http(self):
        """Run MCP server with HTTP transport for Render/Claude Web"""
        
        from starlette.applications import Starlette
        from starlette.routing import Route, Mount
        from starlette.responses import JSONResponse, Response
        from starlette.middleware import Middleware
        from starlette.middleware.cors import CORSMiddleware
        from mcp.server import Server
        from mcp.server.sse import SseServerTransport
        
        # Create MCP server instance
        self.mcp_server = Server("notch-transcription-tool")
        
        # Register tools
        @self.mcp_server.list_tools()
        async def list_tools():
            from mcp.types import Tool
            
            return [
                Tool(
                    name="get_skill_info",
                    description="Get governance and metadata information about this skill",
                    inputSchema={"type": "object", "properties": {}}
                ),
                Tool(
                    name="process_transcript",
                    description="Process a transcript through the Notch tool",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "call_id": {"type": "string", "description": "ID of the call to process"},
                            "source_type": {"type": "string", "enum": ["notch", "upload"], "default": "notch"}
                        },
                        "required": ["call_id"]
                    }
                ),
                Tool(
                    name="list_recent_calls",
                    description="List recently processed calls",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "status": {"type": "string", "enum": ["uploaded", "processing", "analyzed", "failed"]},
                            "limit": {"type": "integer", "default": 50}
                        }
                    }
                ),
                Tool(
                    name="get_call_insights",
                    description="Get detailed insights for a processed call",
                    inputSchema={
                        "type": "object",
                        "properties": {"call_id": {"type": "string"}},
                        "required": ["call_id"]
                    }
                ),
                Tool(
                    name="share_to_invenias",
                    description="Share a processed transcript to Invenias CRM",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "call_id": {"type": "string"},
                            "person_id": {"type": "string"},
                            "person_name": {"type": "string"},
                            "set_as_default_cv": {"type": "boolean", "default": False}
                        },
                        "required": ["call_id", "person_id"]
                    }
                ),
                Tool(
                    name="search_invenias_people",
                    description="Search for people in Invenias CRM",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "query": {"type": "string"},
                            "limit": {"type": "integer", "default": 10}
                        },
                        "required": ["query"]
                    }
                ),
                Tool(
                    name="keep_personal",
                    description="Keep transcript in personal workspace only",
                    inputSchema={
                        "type": "object",
                        "properties": {"call_id": {"type": "string"}},
                        "required": ["call_id"]
                    }
                ),
                Tool(
                    name="generate_summary_and_actions",
                    description="Generate executive summary and action items",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "call_id": {"type": "string"},
                            "include_full_analysis": {"type": "boolean", "default": False}
                        },
                        "required": ["call_id"]
                    }
                ),
                Tool(
                    name="search_transcripts",
                    description="Search across processed transcripts",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "query": {"type": "string"},
                            "top_k": {"type": "integer", "default": 10}
                        },
                        "required": ["query"]
                    }
                ),
                Tool(
                    name="get_destination_status",
                    description="Check where a transcript has been shared",
                    inputSchema={
                        "type": "object",
                        "properties": {"call_id": {"type": "string"}},
                        "required": ["call_id"]
                    }
                )
            ]
        
        @self.mcp_server.call_tool()
        async def call_tool(name: str, arguments: dict):
            try:
                if name == "get_skill_info":
                    result = self.get_skill_metadata()
                elif name == "process_transcript":
                    result = await self.process_transcript(
                        call_id=arguments["call_id"],
                        source_type=arguments.get("source_type", "notch")
                    )
                elif name == "list_recent_calls":
                    result = await self.list_recent_calls(
                        status=arguments.get("status"),
                        limit=arguments.get("limit", 50)
                    )
                elif name == "get_call_insights":
                    result = await self.get_call_insights(call_id=arguments["call_id"])
                elif name == "share_to_invenias":
                    result = await self.share_to_invenias(
                        call_id=arguments["call_id"],
                        person_id=arguments["person_id"],
                        person_name=arguments.get("person_name", ""),
                        set_as_default_cv=arguments.get("set_as_default_cv", False)
                    )
                elif name == "search_invenias_people":
                    result = await self.search_invenias_people(
                        query=arguments["query"],
                        limit=arguments.get("limit", 10)
                    )
                elif name == "keep_personal":
                    result = await self.keep_personal(call_id=arguments["call_id"])
                elif name == "generate_summary_and_actions":
                    result = await self.generate_summary_and_actions(
                        call_id=arguments["call_id"],
                        include_full_analysis=arguments.get("include_full_analysis", False)
                    )
                elif name == "search_transcripts":
                    result = await self.search_transcripts(
                        query=arguments["query"],
                        top_k=arguments.get("top_k", 10)
                    )
                elif name == "get_destination_status":
                    result = await self.get_destination_status(call_id=arguments["call_id"])
                else:
                    return [{"type": "text", "text": f"Unknown tool: {name}"}]
                
                return [{"type": "text", "text": json.dumps(result, indent=2)}]
                
            except Exception as e:
                logger.exception(f"Error in tool {name}")
                return [{"type": "text", "text": f"Error: {str(e)}"}]
        
        # Set up SSE transport
        self.transport = SseServerTransport("/messages")
        
        async def handle_sse(request):
            """Handle SSE connections for MCP"""
            async with self.transport.connect_sse(
                request.scope, request.receive, request._send
            ) as streams:
                await self.mcp_server.run(
                    streams[0],
                    streams[1],
                    self.mcp_server.create_initialization_options()
                )
        
        async def health_check(request):
            """Health check endpoint for Render"""
            return JSONResponse({
                "status": "healthy",
                "service": "notch-transcription",
                "version": SKILL_VERSION,
                "skill_name": SKILL_NAME
            })
        
        async def cors_options(request):
            """Handle CORS preflight requests"""
            return Response(status_code=200, headers={
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
                "Access-Control-Allow-Headers": "Content-Type, Authorization",
            })
        
        # Create Starlette app
        app = Starlette(
            routes=[
                Route("/health", health_check, methods=["GET"]),
                Route("/sse", handle_sse, methods=["GET"]),
                Route("/messages", self.transport.handle_post_message, methods=["POST"]),
                Route("/{path:path}", cors_options, methods=["OPTIONS"]),
            ],
            middleware=[
                Middleware(
                    CORSMiddleware,
                    allow_origins=["*"],
                    allow_methods=["GET", "POST", "OPTIONS"],
                    allow_headers=["Content-Type", "Authorization"],
                )
            ]
        )
        
        logger.info(f"Starting Notch MCP Server on {HOST}:{PORT}")
        logger.info(f"SSE endpoint: http://{HOST}:{PORT}/sse")
        logger.info(f"Health check: http://{HOST}:{PORT}/health")
        
        import uvicorn
        uvicorn.run(app, host=HOST, port=PORT)


async def main():
    tool = NotchMCPTool()
    await tool.run_http()


if __name__ == "__main__":
    asyncio.run(main())