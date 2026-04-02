import networkx as nx
import json
import os
import re

class LegalKnowledgeGraph:
    def __init__(self, laws_path="laws_raw.json", topics_path="data/legal_topics.json"):
        self.graph = nx.DiGraph()
        self.laws_path = laws_path
        self.topics_path = topics_path
        self.topics_dict = {}

    def build_graph(self):
        print("Building Legal Knowledge Graph...")
        
        # Load Hierarchical Topics
        if os.path.exists(self.topics_path):
            with open(self.topics_path, "r", encoding="utf-8") as f:
                topics_data = json.load(f)["topics"]
            
            for main_topic, data in topics_data.items():
                self.graph.add_node(main_topic, type="Topic Level 1")
                for subtopic in data["subtopics"]:
                    self.graph.add_node(subtopic, type="Topic Level 2")
                    self.graph.add_edge(subtopic, main_topic, relation="belongs_to_category")
                    self.topics_dict[subtopic.lower()] = subtopic

        # Load IPC Laws (Simulating Acts/Sections)
        if os.path.exists(self.laws_path):
            with open(self.laws_path, "r", encoding="utf-8") as f:
                ipc_data = json.load(f).get("IPC", {})

        # Add Act Node
        self.graph.add_node("IPC", type="Act", full_name="Indian Penal Code")

        if os.path.exists(self.laws_path):
            with open(self.laws_path, "r", encoding="utf-8") as f:
                ipc_data = json.load(f).get("IPC", {})

            for section_num, details in ipc_data.items():
                node_id = f"IPC_{section_num}"
                title = details.get("title", "")
                
                # Add Section Node
                self.graph.add_node(node_id, type="Section", title=title, content=details.get("content", ""))
                self.graph.add_edge(node_id, "IPC", relation="belongs_to_act")

                # Very naive Topic Mapping based on title keywords (for simulation)
                title_lower = title.lower()
                for topic_key, proper_topic in self.topics_dict.items():
                    # Simple keyword matching to simulate manual tagging
                    if topic_key.split()[0] in title_lower or "murder" in title_lower and "murder" in topic_key:
                        self.graph.add_edge(node_id, proper_topic, relation="categorized_under")
                        break
                
                # Penalties / Punishable Under (mocking logic)
                if "punishment" in title_lower:
                    self.graph.add_node(f"Penalty_{section_num}", type="Penalty", description=title)
                    self.graph.add_edge(node_id, f"Penalty_{section_num}", relation="specifies_penalty")

        # Load Mock Past Cases into Graph
        mock_cases = [
            {"id": "Case_001", "title": "State vs. Cyber Thieves (2023)", "content": "The accused was found guilty of stealing funds via phishing emails under IT Act and IPC for fraud. Sentenced to 3 years.", "category": "Cybercrime", "related_sections": ["IPC_415", "IPC_420"]},
            {"id": "Case_002", "title": "Ramesh vs. Builder Co (2021)", "content": "Consumer dispute where the builder failed to deliver the flat on time. Ordered to refund with 12% interest.", "category": "Property dispute", "related_sections": ["IPC_406"]},
            {"id": "Case_003", "title": "State vs. Abusive Husband (2022)", "content": "Domestic violence case where the accused physically assaulted his wife. Convicted under cruelty laws.", "category": "Domestic violence", "related_sections": ["IPC_498A", "IPC_319"]},
            {"id": "Case_004", "title": "Bank Fraud Syndicate (2024)", "content": "A group forging signatures to clone credit cards. Charged with forgery and cheating.", "category": "Fraud", "related_sections": ["IPC_463", "IPC_420"]}
        ]
        
        for case in mock_cases:
            self.graph.add_node(case["id"], type="Past_Case", title=case["title"], content=case["content"])
            
            # Map to Topics if exists
            cat_lower = case["category"].lower()
            if cat_lower in self.topics_dict:
                self.graph.add_edge(case["id"], self.topics_dict[cat_lower], relation="case_category")
                
            # Map to precise Sections
            for sec in case.get("related_sections", []):
                self.graph.add_edge(case["id"], sec, relation="cites_section")

        print(f"Knowledge Graph Built: {self.graph.number_of_nodes()} nodes, {self.graph.number_of_edges()} edges")
        return self.graph

    def expand_query(self, section_id):
        """Find related nodes (Act, Topics, Neighbors) for an expanded context."""
        context_parts = []
        if self.graph.has_node(section_id):
            # Self
            node_data = self.graph.nodes[section_id]
            context_parts.append(f"Primary Section: {section_id} - {node_data.get('title', '')}")
            
            # Neighbors
            neighbors = list(self.graph.neighbors(section_id)) + list(self.graph.predecessors(section_id))
            for n in set(neighbors):
                n_data = self.graph.nodes[n]
                rel_type = n_data.get("type", "Unknown")
                if rel_type == "Topic Level 2":
                    context_parts.append(f"Belongs to Legal Topic: {n}")
                elif rel_type == "Act":
                    context_parts.append(f"Belongs to Act: {n}")
                elif rel_type == "Penalty":
                    context_parts.append(f"Associated Penalty: {n_data.get('description', '')}")
                elif rel_type == "Section":
                    context_parts.append(f"Related Section: {n} - {n_data.get('title', '')}")
                elif rel_type == "Past_Case":
                    context_parts.append(f"Relevant Precedent: {n_data.get('title', '')} - {n_data.get('content', '')}")
                    
        return "\n".join(context_parts)

    def validate_citation(self, extracted_reference):
        """Check if a node like 'IPC_351' actually exists in the graph."""
        # Clean standard format (e.g. "Section 351 of IPC", "IPC 351")
        match = re.search(r'(?i)(?:section\s*)?(\d+[a-z]?)\s*(?:of\s*)?(IPC|BNS|IT Act)?', extracted_reference)
        if match:
            sec_num = match.group(1)
            act_name = (match.group(2) or "IPC").upper()
            node_id = f"{act_name}_{sec_num}"
            if self.graph.has_node(node_id):
                return True, node_id
        return False, None

# Singleton instance for the app
kg_instance = None
def get_kg():
    global kg_instance
    if kg_instance is None:
        kg_instance = LegalKnowledgeGraph()
        kg_instance.build_graph()
    return kg_instance

# test run
if __name__ == "__main__":
    kg = LegalKnowledgeGraph("../laws_raw.json", "../data/legal_topics.json")
    kg.build_graph()
    print("Test Expansion for IPC_302:")
    print(kg.expand_query("IPC_302"))
