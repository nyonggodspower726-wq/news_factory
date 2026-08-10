"""
AI NEWS FACTORY
RESEARCH ENGINE

Purpose
-------
Coordinate raw information collected from multiple sources and
turn it into a structured research package for the downstream
news intelligence system.

The Research Engine does NOT write the final article.

Its job is to answer:

    What information do we have?
    Where did it come from?
    What are the main facts?
    What claims are emerging?
    What information is missing?
    What appears duplicated?
    What needs verification?
    What deserves deeper investigation?

This engine is designed to sit between source collection and
the claim/evidence/editorial systems.

Pipeline position
-----------------

COLLECTORS
    ↓
RESEARCH ENGINE
    ↓
CLAIM ENGINE
    ↓
EVIDENCE ENGINE
    ↓
FACT CHECKER
    ↓
MISINFORMATION ENGINE
    ↓
JOURNALIST / STORY SYNTHESIS
    ↓
EDITOR
"""


from typing import Any, Dict, List, Set
from collections import Counter
from urllib.parse import urlparse
import re


class ResearchEngine:

    def __init__(self):

        self.name = "Research Intelligence Engine"
        self.version = "1.0.0"

        self.stop_words = {
            "about",
            "after",
            "again",
            "against",
            "being",
            "between",
            "could",
            "first",
            "from",
            "have",
            "into",
            "more",
            "other",
            "said",
            "says",
            "some",
            "than",
            "that",
            "their",
            "there",
            "these",
            "they",
            "this",
            "those",
            "through",
            "under",
            "were",
            "which",
            "while",
            "with",
            "would",
            "where",
            "when",
            "what",
            "will",
            "your"
        }

        self.important_terms = {
            "killed",
            "dead",
            "injured",
            "arrested",
            "missing",
            "election",
            "government",
            "president",
            "minister",
            "court",
            "police",
            "company",
            "attack",
            "crash",
            "fire",
            "explosion",
            "flood",
            "earthquake",
            "storm",
            "warning",
            "decision",
            "announced",
            "approved",
            "banned",
            "released",
            "resigned",
            "elected"
        }

    # =====================================================
    # MAIN RESEARCH FUNCTION
    # =====================================================

    def research(
        self,
        sources: List[Dict[str, Any]],
        topic: str = "",
        event: Dict[str, Any] = None
    ) -> Dict[str, Any]:

        sources = self._normalize_sources(
            sources
        )

        event = (
            event
            if isinstance(
                event,
                dict
            )
            else {}
        )

        source_records = []

        for source in sources:

            source_records.append(
                self._process_source(
                    source
                )
            )

        corpus = self._build_corpus(
            source_records
        )

        entities = self._extract_entities(
            corpus
        )

        facts = self._extract_fact_candidates(
            source_records
        )

        claims = self._extract_claim_candidates(
            source_records
        )

        questions = self._identify_research_gaps(
            source_records,
            claims,
            facts
        )

        contradictions = self._detect_internal_conflicts(
            source_records,
            claims
        )

        duplicates = self._detect_duplicates(
            source_records
        )

        timeline = self._build_timeline(
            source_records
        )

        source_map = self._build_source_map(
            source_records
        )

        priority = self._calculate_research_priority(
            topic,
            source_records,
            claims,
            contradictions
        )

        return {

            "engine":
                self.name,

            "version":
                self.version,

            "status":
                "RESEARCH_COMPLETE",

            "topic":
                topic,

            "event":
                event,

            "source_count":
                len(
                    source_records
                ),

            "sources":
                source_records,

            "corpus":
                corpus,

            "entities":
                entities,

            "fact_candidates":
                facts,

            "claim_candidates":
                claims,

            "research_gaps":
                questions,

            "contradictions":
                contradictions,

            "duplicates":
                duplicates,

            "timeline":
                timeline,

            "source_map":
                source_map,

            "research_priority":
                priority
        }

    # =====================================================
    # NORMALIZATION
    # =====================================================

    def _normalize_sources(
        self,
        sources: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:

        if isinstance(
            sources,
            dict
        ):

            sources = list(
                sources.values()
            )

        if not isinstance(
            sources,
            list
        ):

            return []

        normalized = []

        for index, source in enumerate(
            sources
        ):

            if isinstance(
                source,
                str
            ):

                source = {
                    "content":
                        source
                }

            if not isinstance(
                source,
                dict
            ):

                continue

            normalized.append({

                "source_id":
                    source.get(
                        "source_id",
                        source.get(
                            "id",
                            f"research_source_{index + 1}"
                        )
                    ),

                "name":
                    source.get(
                        "name",
                        source.get(
                            "publisher",
                            ""
                        )
                    ),

                "url":
                    source.get(
                        "url",
                        ""
                    ),

                "type":
                    source.get(
                        "type",
                        source.get(
                            "source_type",
                            "unknown"
                        )
                    ),

                "title":
                    source.get(
                        "title",
                        source.get(
                            "headline",
                            ""
                        )
                    ),

                "content":
                    source.get(
                        "content",
                        source.get(
                            "text",
                            source.get(
                                "body",
                                ""
                            )
                        )
                    ),

                "author":
                    source.get(
                        "author",
                        ""
                    ),

                "published_at":
                    source.get(
                        "published_at"
                    ),

                "updated_at":
                    source.get(
                        "updated_at"
                    ),

                "verified":
                    source.get(
                        "verified",
                        False
                    ),

                "primary":
                    source.get(
                        "primary",
                        False
                    ),

                "original_source":
                    source.get(
                        "original_source",
                        ""
                    )
            })

        return normalized

    # =====================================================
    # PROCESS SOURCE
    # =====================================================

    def _process_source(
        self,
        source: Dict[str, Any]
    ) -> Dict[str, Any]:

        title = str(
            source.get(
                "title",
                ""
            )
        ).strip()

        content = str(
            source.get(
                "content",
                ""
            )
        ).strip()

        combined = (
            title
            + " "
            + content
        ).strip()

        keywords = self._extract_keywords(
            combined
        )

        sentences = self._split_sentences(
            content
        )

        domain = self._domain(
            source.get(
                "url",
                ""
            )
        )

        return {

            "source_id":
                source.get(
                    "source_id"
                ),

            "name":
                source.get(
                    "name"
                ),

            "domain":
                domain,

            "type":
                source.get(
                    "type"
                ),

            "title":
                title,

            "content":
                content,

            "author":
                source.get(
                    "author"
                ),

            "published_at":
                source.get(
                    "published_at"
                ),

            "verified":
                source.get(
                    "verified"
                ),

            "primary":
                source.get(
                    "primary"
                ),

            "original_source":
                source.get(
                    "original_source"
                ),

            "word_count":
                len(
                    content.split()
                ),

            "sentence_count":
                len(
                    sentences
                ),

            "keywords":
                keywords,

            "importance_terms":
                [
                    word
                    for word
                    in keywords
                    if word in self.important_terms
                ]
        }

    # =====================================================
    # CORPUS
    # =====================================================

    def _build_corpus(
        self,
        sources: List[Dict[str, Any]]
    ) -> Dict[str, Any]:

        titles = []
        texts = []
        keywords = []

        for source in sources:

            if source.get(
                "title"
            ):

                titles.append(
                    source[
                        "title"
                    ]
                )

            if source.get(
                "content"
            ):

                texts.append(
                    source[
                        "content"
                    ]
                )

            keywords.extend(
                source.get(
                    "keywords",
                    []
                )
            )

        frequency = Counter(
            keywords
        )

        top_keywords = [
            {
                "keyword":
                    word,

                "frequency":
                    count
            }

            for word, count
            in frequency.most_common(
                30
            )
        ]

        return {

            "titles":
                titles,

            "combined_text":
                "\n\n".join(
                    texts
                ),

            "top_keywords":
                top_keywords,

            "total_words":
                sum(
                    len(
                        text.split()
                    )
                    for text
                    in texts
                )
        }

    # =====================================================
    # KEYWORD EXTRACTION
    # =====================================================

    def _extract_keywords(
        self,
        text: str
    ) -> List[str]:

        words = re.findall(
            r"\b[a-zA-Z][a-zA-Z0-9'-]{3,}\b",
            text.lower()
        )

        cleaned = []

        for word in words:

            word = word.strip(
                "'-"
            )

            if word in self.stop_words:

                continue

            if word.isdigit():

                continue

            cleaned.append(
                word
            )

        counts = Counter(
            cleaned
        )

        return [
            word
            for word, _ in
            counts.most_common(
                50
            )
        ]

    # =====================================================
    # ENTITY EXTRACTION
    # =====================================================

    def _extract_entities(
        self,
        corpus: Dict[str, Any]
    ) -> Dict[str, List[str]]:

        text = str(
            corpus.get(
                "combined_text",
                ""
            )
        )

        people = set()
        organizations = set()
        locations = set()

        # Basic proper-name detection.
        # A future NLP model can replace or enhance this.

        person_patterns = re.findall(
            r"\b[A-Z][a-z]{2,}"
            r"(?:\s+[A-Z][a-z]{2,}){1,2}\b",
            text
        )

        for item in person_patterns:

            normalized = item.strip()

            if len(
                normalized.split()
            ) >= 2:

                people.add(
                    normalized
                )

        organization_markers = [
            "Inc",
            "Ltd",
            "Corporation",
            "Company",
            "Government",
            "Ministry",
            "Agency",
            "University",
            "Bank",
            "Court",
            "Police"
        ]

        for marker in organization_markers:

            matches = re.findall(
                rf"\b[A-Z][A-Za-z0-9&'-]*(?:\s+[A-Z][A-Za-z0-9&'-]*){{0,4}}\s+{marker}\b",
                text
            )

            for match in matches:

                organizations.add(
                    match.strip()
                )

        location_patterns = [
            "Nigeria",
            "United States",
            "United Kingdom",
            "Ghana",
            "Kenya",
            "South Africa",
            "Lagos",
            "Abuja",
            "London",
            "New York",
            "Washington",
            "Accra"
        ]

        lower_text = text.lower()

        for location in location_patterns:

            if location.lower() in lower_text:

                locations.add(
                    location
                )

        return {

            "people":
                sorted(
                    people
                ),

            "organizations":
                sorted(
                    organizations
                ),

            "locations":
                sorted(
                    locations
                )
        }

    # =====================================================
    # FACT CANDIDATES
    # =====================================================

    def _extract_fact_candidates(
        self,
        sources: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:

        facts = []

        fact_patterns = [

            r"\b\d+(?:\.\d+)?%\b",

            r"\b\d{1,3}(?:,\d{3})+\b",

            r"\b\d+\s+(?:people|persons|students|workers|victims|days|years)\b",

            r"\b(?:on|in|at)\s+"
            r"(?:Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday)\b"
        ]

        for source in sources:

            content = source.get(
                "content",
                ""
            )

            sentences = self._split_sentences(
                content
            )

            for sentence in sentences:

                matched = False

                for pattern in fact_patterns:

                    if re.search(
                        pattern,
                        sentence,
                        re.IGNORECASE
                    ):

                        matched = True
                        break

                if matched:

                    facts.append({

                        "source_id":
                            source.get(
                                "source_id"
                            ),

                        "text":
                            sentence.strip(),

                        "type":
                            "specific_fact_candidate"
                    })

        return facts[:100]

    # =====================================================
    # CLAIM CANDIDATES
    # =====================================================

    def _extract_claim_candidates(
        self,
        sources: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:

        claims = []

        claim_markers = [

            "said",
            "announced",
            "reported",
            "confirmed",
            "claimed",
            "alleged",
            "according to",
            "stated",
            "warned",
            "revealed",
            "denied",
            "disputed"
        ]

        for source in sources:

            sentences = self._split_sentences(
                source.get(
                    "content",
                    ""
                )
            )

            for sentence in sentences:

                lower = sentence.lower()

                if any(
                    marker in lower
                    for marker
                    in claim_markers
                ):

                    claims.append({

                        "claim_id":
                            f"claim_{len(claims) + 1}",

                        "text":
                            sentence.strip(),

                        "source_id":
                            source.get(
                                "source_id"
                            ),

                        "source_name":
                            source.get(
                                "name"
                            ),

                        "claim_type":
                            self._claim_type(
                                lower
                            ),

                        "requires_verification":
                            True
                    })

        return claims[:150]

    # =====================================================
    # CLAIM TYPE
    # =====================================================

    def _claim_type(
        self,
        text: str
    ) -> str:

        if any(
            word in text
            for word in {
                "denied",
                "disputed",
                "false",
                "incorrect"
            }
        ):

            return "disputed_claim"

        if any(
            word in text
            for word in {
                "alleged",
                "allegedly"
            }
        ):

            return "allegation"

        if any(
            word in text
            for word in {
                "confirmed",
                "officially"
            }
        ):

        
