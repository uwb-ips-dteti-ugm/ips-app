from typing import Any, Callable, Dict, List, Tuple, Type, TypeVar

from beanie import Document
from beanie.odm.queries.find import FindMany
from beanie.operators import In

TDocument = TypeVar("TDocument", bound=Document)
TDomain = TypeVar("TDomain")


async def paginate(
    query: "FindMany[TDocument]",
    page: int,
    limit: int,
    to_domain: Callable[[TDocument], TDomain],
) -> Tuple[List[TDomain], int]:
    total = await query.count()
    docs = await query.sort("_id").skip(page * limit).limit(limit).to_list()
    return [to_domain(doc) for doc in docs], total


async def paginate_with_links(
    document_cls: Type[TDocument],
    query_filter: Dict[str, Any],
    page: int,
    limit: int,
    to_domain: Callable[[TDocument], TDomain],
    session: Any = None,
) -> Tuple[List[TDomain], int]:
    """Beanie's `fetch_links=True` rewrites the query into an aggregation pipeline
    that resolves Link fields *before* the $match stage runs, so filtering on a
    Link's nested id (e.g. "network.$id") never matches once fetch_links is also
    requested. Work around it in two steps: sort/paginate on the raw (unresolved)
    documents first, then re-fetch just that page's ids with fetch_links=True.
    """
    unresolved_query = document_cls.find(query_filter, session=session)
    total = await unresolved_query.count()
    page_docs = await (
        unresolved_query.sort("_id").skip(page * limit).limit(limit).to_list()
    )
    ids = [doc.id for doc in page_docs]
    if not ids:
        return [], total

    resolved_docs = await document_cls.find(
        In(document_cls.id, ids),
        fetch_links=True,
        session=session,
    ).to_list()
    by_id = {doc.id: doc for doc in resolved_docs}
    ordered = [by_id[doc_id] for doc_id in ids if doc_id in by_id]
    return [to_domain(doc) for doc in ordered], total
