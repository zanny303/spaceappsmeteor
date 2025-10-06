# backend/rag_chat_service.py
"""
Enhanced RAG (Retrieval-Augmented Generation) Chat Service
Provides context-aware answers using NASA documentation and mission data
"""

import os
import logging
from typing import List, Dict, Optional
import json

logger = logging.getLogger(__name__)

try:
    from langchain_community.vectorstores import Chroma
    from langchain_community.embeddings import HuggingFaceEmbeddings
    from langchain.text_splitter import RecursiveCharacterTextSplitter
    from langchain.schema import Document
    LANGCHAIN_AVAILABLE = True
    logger.info("✅ LangChain components imported")
except ImportError as e:
    logger.warning(f"LangChain not fully available, using fallback: {e}")
    LANGCHAIN_AVAILABLE = False
    Document = None


class SimpleDocument:
    """Simple document wrapper to match LangChain Document interface"""
    def __init__(self, page_content: str, metadata: dict = None):
        self.page_content = page_content
        self.metadata = metadata or {}
    
    def get(self, key: str, default=None):
        """Support dict-like access for compatibility"""
        if key == 'page_content':
            return self.page_content
        elif key == 'metadata':
            return self.metadata
        return default


class NASADocumentStore:
    """Manages NASA documentation vector store for RAG"""

    def __init__(self, persist_directory="./nasa_knowledge_base"):
        self.persist_directory = persist_directory
        self.vectorstore = None
        self.embeddings = None
        self.simple_docs = []  # Fallback simple storage

        if LANGCHAIN_AVAILABLE:
            try:
                logger.info("📚 Attempting to load vector store...")
                # Use free, open-source embeddings (no API key needed)
                self.embeddings = HuggingFaceEmbeddings(
                    model_name="sentence-transformers/all-MiniLM-L6-v2"
                )

                # Try to load existing vectorstore
                if os.path.exists(persist_directory):
                    logger.info("Loading existing NASA knowledge base...")
                    self.vectorstore = Chroma(
                        persist_directory=persist_directory,
                        embedding_function=self.embeddings
                    )
                    logger.info("✅ Knowledge base loaded")
                else:
                    logger.info("Creating new NASA knowledge base...")
                    self._initialize_knowledge_base()

            except Exception as e:
                logger.warning(f"Vector store failed, using simple search: {e}")
                self.vectorstore = None
                self._load_simple_docs()
        else:
            logger.info("Using simple keyword-based document retrieval")
            self._load_simple_docs()

    def _initialize_knowledge_base(self):
        """Initialize knowledge base with NASA planetary defense documentation"""

        # Sample NASA documentation (in production, load from files)
        nasa_docs = [
            {
                "title": "Near-Earth Object Basics",
                "content": """
                Near-Earth Objects (NEOs) are asteroids and comets with orbits that bring them
                within 1.3 astronomical units (AU) of the Sun and thus within 0.3 AU of Earth's orbit.
                NASA tracks over 30,000 NEOs. Potentially Hazardous Asteroids (PHAs) are defined as
                objects larger than 140 meters that come within 0.05 AU of Earth's orbit.
                """,
                "source": "NASA NEO Program"
            },
            {
                "title": "Asteroid Impact Energy",
                "content": """
                Impact energy is calculated using kinetic energy formula: E = 0.5 * m * v².
                The energy is often expressed in megatons of TNT equivalent (1 megaton = 4.184×10^15 joules).
                The Tunguska event in 1908 released approximately 10-15 megatons. The Chicxulub impact
                that contributed to dinosaur extinction was estimated at 100 million megatons.
                """,
                "source": "Impact Physics"
            },
            {
                "title": "Deflection Strategies",
                "content": """
                Primary asteroid deflection methods include: Kinetic Impactor (demonstrated by DART mission),
                Gravity Tractor (uses spacecraft's gravitational pull), Nuclear Deflection (standoff or
                subsurface detonation), and Ion Beam Shepherd. The DART mission successfully altered
                asteroid Dimorphos's orbit by 33 minutes using kinetic impact.
                """,
                "source": "Planetary Defense Strategies"
            },
            {
                "title": "Orbital Mechanics Fundamentals",
                "content": """
                Asteroid orbits are characterized by six Keplerian elements: semi-major axis (a),
                eccentricity (e), inclination (i), longitude of ascending node (Ω), argument of
                perihelion (ω), and true anomaly (ν). State vectors consist of position (x,y,z) and
                velocity (vx,vy,vz) components, typically in km and km/s.
                """,
                "source": "Orbital Mechanics"
            },
            {
                "title": "Torino Impact Hazard Scale",
                "content": """
                The Torino Scale categorizes asteroid impact hazards from 0 (no hazard) to 10 (certain
                global catastrophe). Scale 0: negligible chance of collision. Scale 1-4: normal monitoring.
                Scale 5-7: threatening, close monitoring required. Scale 8-10: certain collision with
                regional to global consequences. Most NEOs are rated 0 or 1.
                """,
                "source": "Risk Assessment"
            },
            {
                "title": "DART Mission Results",
                "content": """
                The Double Asteroid Redirection Test (DART) impacted Dimorphos on September 26, 2022.
                The spacecraft weighed 570 kg and struck at 6.6 km/s. The impact changed Dimorphos's
                orbital period by 33 minutes (±1 minute), exceeding the minimum success threshold of
                73 seconds. The momentum transfer efficiency (beta factor) was measured at 3.6, higher
                than pre-impact estimates of 2.2.
                """,
                "source": "DART Mission"
            },
            {
                "title": "Seismic Effects of Impacts",
                "content": """
                Impact-generated seismic magnitude can be estimated using: M = 0.67*log10(E) - 5.87,
                where E is energy in joules. A 100-megaton impact generates approximately magnitude 7.8
                earthquake. Seismic waves from impacts differ from tectonic earthquakes, with more
                short-period energy. Ground motion intensity decreases with distance from impact.
                """,
                "source": "Impact Seismology"
            },
            {
                "title": "Tsunami Generation from Ocean Impacts",
                "content": """
                Ocean impacts can generate tsunamis if the asteroid is larger than the ocean depth at
                impact site. Wave height depends on impact energy, water depth, and distance from impact.
                A 200-meter asteroid impacting deep ocean (4km depth) can generate waves exceeding
                100 meters at the impact site, decreasing to 10-30 meters at coastal regions within
                1000 km. Asteroid must be >200m diameter to cause significant transoceanic tsunami.
                """,
                "source": "Tsunami Modeling"
            },
            {
                "title": "Asteroid Composition Types",
                "content": """
                Asteroids are classified by composition: C-type (carbonaceous, ~75% of asteroids,
                density ~1300 kg/m³), S-type (silicaceous/stony, ~17%, density ~2700 kg/m³),
                M-type (metallic, ~8%, density ~5300 kg/m³). Composition affects mass estimation,
                deflection efficiency, and impact consequences. Most PHAs are S-type asteroids.
                """,
                "source": "Asteroid Science"
            },
            {
                "title": "Lead Time for Deflection Missions",
                "content": """
                Required delta-v (Δv) for deflection decreases with longer lead time. For a 300m
                asteroid with 5 years warning, kinetic impactor may need Δv ~ 1-5 mm/s. With 10 years,
                Δv requirements reduce to <1 mm/s. Minimum viable warning time for current technology
                is approximately 5-10 years for asteroids in 100-500m range. Smaller lead times may
                require nuclear options.
                """,
                "source": "Mission Planning"
            }
        ]

        # Convert to LangChain documents
        documents = []
        for doc in nasa_docs:
            documents.append(Document(
                page_content=f"Title: {doc['title']}\n\n{doc['content']}",
                metadata={"source": doc["source"], "title": doc["title"]}
            ))

        # Split documents into chunks
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=500,
            chunk_overlap=50
        )
        splits = text_splitter.split_documents(documents)

        # Create and persist vectorstore
        self.vectorstore = Chroma.from_documents(
            documents=splits,
            embedding=self.embeddings,
            persist_directory=self.persist_directory
        )

        logger.info(f"✅ Created knowledge base with {len(splits)} document chunks")

    def retrieve_context(self, query: str, k: int = 3):
        """Retrieve relevant documents for a query"""
        if self.vectorstore:
            try:
                docs = self.vectorstore.similarity_search(query, k=k)
                return docs
            except Exception as e:
                logger.warning(f"Vector search failed, using simple search: {e}")

        # Fallback to simple keyword search
        if self.simple_docs:
            return self._simple_keyword_search(query, k)

        return []

    def _load_simple_docs(self):
        """Load documents into simple list for keyword search (fallback)"""
        self.simple_docs = [
            {
                "title": "Near-Earth Object Basics", 
                "content": "Near-Earth Objects (NEOs) are asteroids and comets with orbits that bring them within 1.3 astronomical units (AU) of the Sun and thus within 0.3 AU of Earth's orbit. NASA tracks over 30,000 NEOs. Potentially Hazardous Asteroids (PHAs) are defined as objects larger than 140 meters that come within 0.05 AU of Earth's orbit.", 
                "keywords": ["neo", "asteroid", "comet", "orbit", "pha", "hazardous"]
            },
            {
                "title": "Asteroid Impact Energy", 
                "content": "Impact energy is calculated using kinetic energy formula: E = 0.5 * m * v². The energy is often expressed in megatons of TNT equivalent (1 megaton = 4.184×10^15 joules). The Tunguska event in 1908 released approximately 10-15 megatons. The Chicxulub impact that contributed to dinosaur extinction was estimated at 100 million megatons.", 
                "keywords": ["energy", "impact", "megaton", "tunguska", "chicxulub", "joules"]
            },
            {
                "title": "Deflection Strategies", 
                "content": "Primary asteroid deflection methods include: Kinetic Impactor (demonstrated by DART mission), Gravity Tractor (uses spacecraft's gravitational pull), Nuclear Deflection (standoff or subsurface detonation), and Ion Beam Shepherd. The DART mission successfully altered asteroid Dimorphos's orbit by 33 minutes using kinetic impact.", 
                "keywords": ["deflection", "dart", "kinetic", "nuclear", "gravity", "mission"]
            },
            {
                "title": "Orbital Mechanics Fundamentals", 
                "content": "Asteroid orbits are characterized by six Keplerian elements: semi-major axis (a), eccentricity (e), inclination (i), longitude of ascending node (Ω), argument of perihelion (ω), and true anomaly (ν). State vectors consist of position (x,y,z) and velocity (vx,vy,vz) components, typically in km and km/s.", 
                "keywords": ["orbit", "keplerian", "elements", "state", "vector", "mechanics"]
            },
            {
                "title": "Torino Impact Hazard Scale", 
                "content": "The Torino Scale categorizes asteroid impact hazards from 0 (no hazard) to 10 (certain global catastrophe). Scale 0: negligible chance of collision. Scale 1-4: normal monitoring. Scale 5-7: threatening, close monitoring required. Scale 8-10: certain collision with regional to global consequences. Most NEOs are rated 0 or 1.", 
                "keywords": ["torino", "scale", "hazard", "risk", "rating", "catastrophe"]
            },
            {
                "title": "DART Mission Results", 
                "content": "The Double Asteroid Redirection Test (DART) impacted Dimorphos on September 26, 2022. The spacecraft weighed 570 kg and struck at 6.6 km/s. The impact changed Dimorphos's orbital period by 33 minutes (±1 minute), exceeding the minimum success threshold of 73 seconds. The momentum transfer efficiency (beta factor) was measured at 3.6, higher than pre-impact estimates of 2.2.", 
                "keywords": ["dart", "dimorphos", "mission", "impact", "deflection", "beta"]
            },
            {
                "title": "Seismic Effects of Impacts", 
                "content": "Impact-generated seismic magnitude can be estimated using: M = 0.67*log10(E) - 5.87, where E is energy in joules. A 100-megaton impact generates approximately magnitude 7.8 earthquake. Seismic waves from impacts differ from tectonic earthquakes, with more short-period energy. Ground motion intensity decreases with distance from impact.", 
                "keywords": ["seismic", "earthquake", "magnitude", "ground", "motion"]
            },
            {
                "title": "Asteroid Composition Types", 
                "content": "Asteroids are classified by composition: C-type (carbonaceous, ~75% of asteroids, density ~1300 kg/m³), S-type (silicaceous/stony, ~17%, density ~2700 kg/m³), M-type (metallic, ~8%, density ~5300 kg/m³). Composition affects mass estimation, deflection efficiency, and impact consequences. Most PHAs are S-type asteroids.", 
                "keywords": ["composition", "c-type", "s-type", "m-type", "density", "carbonaceous"]
            },
        ]
        logger.info(f"✅ Loaded {len(self.simple_docs)} NASA documents for simple retrieval")

    def _simple_keyword_search(self, query: str, k: int = 3):
        """Simple keyword-based search fallback - FIXED VERSION"""
        query_lower = query.lower()
        scores = []

        for doc in self.simple_docs:
            score = 0
            # Check title
            if any(word in doc['title'].lower() for word in query_lower.split()):
                score += 3
            # Check keywords
            for keyword in doc['keywords']:
                if keyword in query_lower:
                    score += 2
            # Check content
            if any(word in doc['content'].lower() for word in query_lower.split()):
                score += 1

            if score > 0:
                scores.append((score, doc))

        # Sort by score and return top k
        scores.sort(reverse=True, key=lambda x: x[0])
        
        # Return SimpleDocument objects instead of dictionaries
        return [SimpleDocument(
            page_content=doc['content'], 
            metadata={"title": doc['title'], "source": "NASA Documentation"}
        ) for _, doc in scores[:k]]


class RAGChatService:
    """Enhanced chat service with Retrieval-Augmented Generation"""

    def __init__(self):
        self.doc_store = NASADocumentStore()
        self.conversation_history = []

    def chat(self, user_message: str, mission_context: Optional[Dict] = None) -> Dict:
        """
        Generate context-aware response using RAG

        Args:
            user_message: User's question
            mission_context: Current mission data (asteroid info, analysis results)

        Returns:
            Response with answer, sources, and context
        """

        # Retrieve relevant NASA documentation
        relevant_docs = self.doc_store.retrieve_context(user_message, k=3)

        # Build context from retrieved documents
        context_text = "\n\n".join([
            f"[{doc.metadata.get('title', 'Unknown')}]\n{doc.page_content}"
            for doc in relevant_docs
        ])

        # Add mission context if available
        mission_summary = ""
        if mission_context:
            mission_summary = self._format_mission_context(mission_context)

        # Generate response using rule-based system (fallback for no OpenAI key)
        response = self._generate_response(
            user_message,
            context_text,
            mission_summary,
            relevant_docs
        )

        return response

    def _format_mission_context(self, context: Dict) -> str:
        """Format mission data into readable context"""
        parts = []

        if 'asteroid_info' in context:
            info = context['asteroid_info']
            parts.append(f"Current Analysis: {info.get('name', 'Unknown asteroid')}")
            parts.append(f"Diameter: {info.get('diameter_m', 0):.1f} meters")
            parts.append(f"Velocity: {info.get('velocity_kms', 0):.2f} km/s")

        if 'ai_predicted_consequences' in context:
            cons = context['ai_predicted_consequences']
            parts.append(f"Impact Energy: {cons.get('impact_energy_megatons', 0):.1f} megatons")
            parts.append(f"Seismic Magnitude: M{cons.get('predicted_seismic_magnitude', 0):.1f}")

        if 'mission_recommendation' in context:
            mission = context['mission_recommendation']
            parts.append(f"Recommended Strategy: {mission.get('interceptor_type', 'Unknown')}")

        return " | ".join(parts)

    def _generate_response(self, question: str, context: str, mission_summary: str, docs: List) -> Dict:
        """Generate response using retrieved context (rule-based fallback)"""

        # Extract key information based on question keywords
        question_lower = question.lower()

        response_text = ""
        confidence = "high"

        # Context-aware responses
        if any(word in question_lower for word in ['what is', 'define', 'explain']):
            response_text = self._extract_definition(context, question)

        elif any(word in question_lower for word in ['how to', 'deflect', 'stop', 'prevent']):
            response_text = self._extract_deflection_info(context)

        elif any(word in question_lower for word in ['energy', 'impact', 'damage', 'magnitude']):
            if mission_summary:
                response_text = f"Based on current analysis: {mission_summary}\n\n"
            response_text += self._extract_impact_info(context)

        elif any(word in question_lower for word in ['dart', 'mission', 'test']):
            response_text = self._extract_dart_info(context)

        elif any(word in question_lower for word in ['torino', 'scale', 'risk']):
            response_text = self._extract_risk_info(context)

        else:
            # Generic response with context
            response_text = f"Based on NASA documentation:\n\n{context[:500]}..."
            confidence = "medium"

        # Add sources - now works with SimpleDocument objects
        sources = [
            {
                "title": doc.metadata.get('title', 'Unknown'),
                "source": doc.metadata.get('source', 'NASA Documentation'),
                "snippet": doc.page_content[:200] + "..."
            }
            for doc in docs
        ]

        return {
            "answer": response_text,
            "confidence": confidence,
            "sources": sources,
            "mission_context": mission_summary if mission_summary else None
        }

    def _extract_definition(self, context: str, question: str) -> str:
        """Extract definition from context"""
        # Find the first paragraph that seems like a definition
        paragraphs = context.split('\n\n')
        for para in paragraphs:
            if len(para) > 50:  # Substantial content
                return para
        return "Based on NASA documentation: " + context[:300] + "..."

    def _extract_deflection_info(self, context: str) -> str:
        """Extract deflection strategy information"""
        if "deflection" in context.lower() or "dart" in context.lower():
            relevant = [p for p in context.split('\n\n') if 'deflection' in p.lower() or 'impactor' in p.lower()]
            if relevant:
                return "\n\n".join(relevant[:2])
        return "Asteroid deflection strategies include kinetic impactors, gravity tractors, and nuclear options. The DART mission demonstrated successful kinetic impact deflection."

    def _extract_impact_info(self, context: str) -> str:
        """Extract impact energy and consequences"""
        if "energy" in context.lower() or "megaton" in context.lower():
            relevant = [p for p in context.split('\n\n') if 'energy' in p.lower() or 'impact' in p.lower()]
            if relevant:
                return "\n\n".join(relevant[:2])
        return "Impact energy depends on asteroid mass and velocity. Energy is often measured in megatons of TNT equivalent."

    def _extract_dart_info(self, context: str) -> str:
        """Extract DART mission information"""
        if "dart" in context.lower():
            relevant = [p for p in context.split('\n\n') if 'dart' in p.lower()]
            if relevant:
                return "\n\n".join(relevant)
        return "DART (Double Asteroid Redirection Test) successfully demonstrated kinetic impactor technology in 2022."

    def _extract_risk_info(self, context: str) -> str:
        """Extract risk assessment information"""
        if "torino" in context.lower() or "scale" in context.lower():
            relevant = [p for p in context.split('\n\n') if 'torino' in p.lower() or 'scale' in p.lower()]
            if relevant:
                return "\n\n".join(relevant)
        return "The Torino Scale rates asteroid impact hazards from 0 (no hazard) to 10 (certain global catastrophe)."


# Global instance
rag_chat = RAGChatService()

# Test function
if __name__ == "__main__":
    print("🧪 Testing RAG Chat Service")
    print("=" * 70)

    test_questions = [
        "What is a Near-Earth Object?",
        "How does the DART mission work?",
        "What is the Torino Scale?",
        "How do we calculate impact energy?"
    ]

    for question in test_questions:
        print(f"\n❓ Question: {question}")
        response = rag_chat.chat(question)
        print(f"💬 Answer: {response['answer'][:200]}...")
        print(f"📚 Sources: {len(response['sources'])} documents")