"""
AI NEWS FACTORY
ENTITY RESOLUTION ENGINE

Purpose
-------
Identify when different names or references probably refer to
the same real-world entity.

Examples:

    "President Trump"
    "Donald Trump"
    "Trump"

may represent the same person.

Likewise:

    "United States"
    "US"
    "U.S."
    "USA"

may represent the same location.

The engine does NOT invent identities.

It produces:
    - normalized entities
    - aliases
    - possible matches
    - confidence scores
    - ambiguity warnings

Final identity decisions should be verified by the
verification/editorial systems.

Supported entity types:

    PERSON
    ORGANIZATION
    LOCATION
    EVENT
"""


from typing import Any, Dict, List, Optional, Set
import re
import unicodedata


class EntityResolutionEngine:

    def __init__(self):

        self.name = "Entity Resolution Intelligence Engine"
        self.version = "1.0.0"

        self.common_titles = {
            "mr",
            "mrs",
            "ms",
            "miss",
            "dr",
            "prof",
            "professor",
            "president",
            "prime",
            "minister",
            "governor",
            "senator",
            "rep",
            "representative",
            "chief",
            "general",
            "captain",
            "coach",
            "mayor"
        }

        self.organization_aliases = {

            "united nations":
                "united nations",

            "un":
                "united nations",

            "world health organization":
                "world health organization",

            "who":
                "world health organization",

            "world bank":
                "world bank",

            "international monetary fund":
                "international monetary fund",

            "imf":
                "international monetary fund"
        }

        self.location_aliases = {

            "usa":
                "united states",

            "u.s.":
                "united states",

            "u.s":
                "united states",

            "us":
                "united states",

            "united states of america":
                "united states",

            "uk":
                "united kingdom",

            "u.k.":
                "united kingdom",

            "uae":
                "united arab emirates"
        }

    # =====================================================
    # MAIN
    # =====================================================

    def resolve(
        self,
        entities: List[Dict[str, Any]],
        known_entities: List[Dict[str, Any]] = None
    ) -> Dict[str, Any]:

        entities = (
            entities
            if isinstance(
                entities,
                list
            )
            else []
        )

        known_entities = (
            known_entities
            if isinstance(
                known_entities,
                list
            )
            else []
        )

        normalized = []

        for entity in entities:

            item = self._normalize_entity(
                entity
            )

            if item:

                normalized.append(
                    item
                )

        clusters = self._cluster_entities(
            normalized
        )

        matches = self._match_known_entities(
            normalized,
            known_entities
        )

        ambiguity = self._detect_ambiguity(
            clusters
        )

        return {

            "engine":
                self.name,

            "version":
                self.version,

            "status":
                "ENTITY_RESOLUTION_COMPLETE",

            "entity_count":
                len(
                    normalized
                ),

            "normalized_entities":
                normalized,

            "entity_clusters":
                clusters,

            "known_entity_matches":
                matches,

            "ambiguity_warnings":
                ambiguity
        }

    # =====================================================
    # NORMALIZATION
    # =====================================================

    def _normalize_entity(
        self,
        entity: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:

        if isinstance(
            entity,
            str
        ):

            name = entity
            entity_type = "UNKNOWN"

        elif isinstance(
            entity,
            dict
        ):

            name = entity.get(
                "name",
                entity.get(
                    "text",
                    entity.get(
                        "value",
                        ""
                    )
                )
            )

            entity_type = entity.get(
                "type",
                entity.get(
                    "entity_type",
                    "UNKNOWN"
                )
            )

        else:

            return None

        name = str(
            name
        ).strip()

        if not name:

            return None

        entity_type = self._normalize_type(
            entity_type
        )

        normalized_name = self._normalize_name(
            name,
            entity_type
        )

        canonical = self._canonical_alias(
            normalized_name,
            entity_type
        )

        return {

            "original_name":
                name,

            "normalized_name":
                normalized_name,

            "canonical_name":
                canonical,

            "type":
                entity_type,

            "entity_key":
                self._entity_key(
                    canonical,
                    entity_type
                )
        }

    # =====================================================
    # TYPE
    # =====================================================

    def _normalize_type(
        self,
        entity_type: Any
    ) -> str:

        value = str(
            entity_type
        ).strip().upper()

        aliases = {

            "PERSON":
                "PERSON",

            "PER":
                "PERSON",

            "PEOPLE":
                "PERSON",

            "ORG":
                "ORGANIZATION",

            "ORGANISATION":
                "ORGANIZATION",

            "COMPANY":
                "ORGANIZATION",

            "ORGANIZATION":
                "ORGANIZATION",

            "LOCATION":
                "LOCATION",

            "LOC":
                "LOCATION",

            "PLACE":
                "LOCATION",

            "GPE":
                "LOCATION",

            "EVENT":
                "EVENT"
        }

        return aliases.get(
            value,
            "UNKNOWN"
        )

    # =====================================================
    # NAME NORMALIZATION
    # =====================================================

    def _normalize_name(
        self,
        name: str,
        entity_type: str
    ) -> str:

        name = unicodedata.normalize(
            "NFKD",
            name
        )

        name = name.lower().strip()

        name = re.sub(
            r"\s+",
            " ",
            name
        )

        if entity_type == "PERSON":

            name = self._remove_person_title(
                name
            )

        name = name.strip(
            " ,.;:()[]{}"
        )

        return name

    # =====================================================
    # PERSON TITLE
    # =====================================================

    def _remove_person_title(
        self,
        name: str
    ) -> str:

        words = name.split()

        while words:

            first = words[0].rstrip(
                "."
            )

            if first in self.common_titles:

                words.pop(0)

            else:

                break

        return " ".join(
            words
        )

    # =====================================================
    # CANONICAL ALIAS
    # =====================================================

    def _canonical_alias(
        self,
        name: str,
        entity_type: str
    ) -> str:

        if entity_type == "ORGANIZATION":

            return self.organization_aliases.get(
                name,
                name
            )

        if entity_type == "LOCATION":

            return self.location_aliases.get(
                name,
                name
            )

        return name

    # =====================================================
    # ENTITY KEY
    # =====================================================

    def _entity_key(
        self,
        name: str,
        entity_type: str
    ) -> str:

        safe_name = re.sub(
            r"[^a-z0-9]+",
            "_",
            name.lower()
        )

        safe_name = safe_name.strip(
            "_"
        )

        return (
            entity_type.lower()
            +
            ":"
            +
            safe_name
        )

    # =====================================================
    # CLUSTERING
    # =====================================================

    def _cluster_entities(
        self,
        entities: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:

        clusters = []
        used = set()

        for index, entity in enumerate(
            entities
        ):

            if index in used:

                continue

            cluster = [
                entity
            ]

            used.add(
                index
            )

            for other_index in range(
                index + 1,
                len(
                    entities
                )
            ):

                if other_index in used:

                    continue

                other = entities[
                    other_index
                ]

                confidence = self._match_score(
                    entity,
                    other
                )

                if confidence >= 0.85:

                    cluster.append(
                        other
                    )

                    used.add(
                        other_index
                    )

            canonical = self._choose_canonical(
                cluster
            )

            clusters.append({

                "cluster_id":
                    f"entity_cluster_{len(clusters) + 1}",

                "canonical_name":
                    canonical.get(
                        "canonical_name"
                    ),

                "type":
                    canonical.get(
                        "type"
                    ),

                "members":
                    cluster,

                "confidence":
                    self._cluster_confidence(
                        cluster
                    )
            })

        return clusters

    # =====================================================
    # KNOWN ENTITY MATCHING
    # =====================================================

    def _match_known_entities(
        self,
        entities: List[Dict[str, Any]],
        known_entities: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:

        results = []

        normalized_known = []

        for known in known_entities:

            item = self._normalize_entity(
                known
            )

            if item:

                normalized_known.append(
                    item
                )

        for entity in entities:

            candidates = []

            for known in normalized_known:

                score = self._match_score(
                    entity,
                    known
                )

                if score >= 0.60:

                    candidates.append({

                        "entity":
                            known,

                        "confidence":
                            round(
                                score,
                                3
                            )
                    })

            candidates.sort(
                key=lambda item:
                    item[
                        "confidence"
                    ],
                reverse=True
            )

            results.append({

                "input":
                    entity,

                "matches":
                    candidates[:5],

                "ambiguous":
                    self._is_ambiguous(
                        candidates
                    )
            })

        return results

    # =====================================================
    # MATCH SCORE
    # =====================================================

    def _match_score(
        self,
        first: Dict[str, Any],
        second: Dict[str, Any]
    ) -> float:

        if not first or not second:

            return 0.0

        first_type = first.get(
            "type"
        )

        second_type = second.get(
            "type"
        )

        if (
            first_type != "UNKNOWN"
            and
            second_type != "UNKNOWN"
            and
            first_type != second_type
        ):

            return 0.0

        first_name = first.get(
            "canonical_name",
            ""
        )

        second_name = second.get(
            "canonical_name",
            ""
        )

        if not first_name or not second_name:

            return 0.0

        if first_name == second_name:

            return 1.0

        first_tokens = set(
            first_name.split()
        )

        second_tokens = set(
            second_name.split()
        )

        if not first_tokens or not second_tokens:

            return 0.0

        intersection = (
            first_tokens
            &
            second_tokens
        )

        union = (
            first_tokens
            |
            second_tokens
        )

        jaccard = (
            len(
                intersection
            )
            /
            len(
                union
            )
        )

        score = jaccard

        # -------------------------------------------------
        # Person-specific logic
        # -------------------------------------------------

        if first_type == "PERSON":

            first_last = (
                first_tokens.pop()
                if first_tokens
                else ""
            )

            second_last = (
                second_tokens.pop()
                if second_tokens
                else ""
            )

            if (
                first_last
                and
                second_last
                and
                first_last == second_last
            ):

                score += 0.20

        return min(
            1.0,
            score
        )

    # =====================================================
    # CANONICAL ENTITY
    # =====================================================

    def _choose_canonical(
        self,
        cluster: List[Dict[str, Any]]
    ) -> Dict[str, Any]:

        if not cluster:

            return {}

        # Prefer the longest informative name.
        return max(
            cluster,
            key=lambda item:
                len(
                    item.get(
                        "canonical_name",
                        ""
                    )
                )
        )

    # =====================================================
    # CLUSTER CONFIDENCE
    # =====================================================

    def _cluster_confidence(
        self,
        cluster: List[Dict[str, Any]]
    ) -> float:

        if len(
            cluster
        ) <= 1:

            return 1.0

        scores = []

        first = cluster[0]

        for other in cluster[1:]:

            scores.append(
                self._match_score(
                    first,
                    other
                )
            )

        if not scores:

            return 1.0

        return round(
            sum(
                scores
            )
            /
            len(
                scores
            ),
            3
        )

    # =====================================================
    # AMBIGUITY
    # =====================================================

    def _detect_ambiguity(
        self,
        clusters: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:

        warnings = []

        for cluster in clusters:

            members = cluster.get(
                "members",
                []
            )

            if len(
                members
            ) <= 1:

                continue

            names = self._unique([
                member.get(
                    "original_name",
                    ""
                )
                for member
                in members
            ])

            confidence = cluster.get(
                "confidence",
                0
            )

            if confidence < 0.90:

                warnings.append({

                    "cluster_id":
                        cluster.get(
                            "cluster_id"
                        ),

                    "names":
                        names,

                    "warning":
                        "Possible entity match requires additional context.",

                    "confidence":
                        confidence
                })

        return warnings

    # =====================================================
    # AMBIGUOUS MATCH
    # =====================================================

    def _is_ambiguous(
        self,
        candidates: List[Dict[str, Any]]
    ) -> bool:

        if len(
            candidates
        ) < 2:

            return False

        first = candidates[0].get(
            "confidence",
            0
        )

        second = candidates[1].get(
            "confidence",
            0
        )

        return (
            first - second
            <
            0.10
        )

    # =====================================================
    # UNIQUE
    # =====================================================

    def _unique(
        self,
        values: List[Any]
    ) -> List[Any]:

        result = []
        seen = set()

        for value in values:

            value = str(
                value
            ).strip()

            if not value:

                continue

            if value in seen:

                continue

            seen.add(
                value
            )

            result.append(
                value
            )

        return result


# =========================================================
# HELPER
# =========================================================

def resolve_entities(
    entities: List[Dict[str, Any]],
    known_entities: List[Dict[str, Any]] = None
) -> Dict[str, Any]:

    engine = EntityResolutionEngine()

    return engine.resolve(
        entities=entities,
        known_entities=known_entities
      )
