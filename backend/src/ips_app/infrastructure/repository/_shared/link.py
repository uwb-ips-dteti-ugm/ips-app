from typing import Any, Dict, List, Optional, Sequence, Type, TypeVar, Union

from beanie import Document, Link

from ips_app.domain.models.exception import UnexpectedDomainException

TDocument = TypeVar("TDocument", bound=Document)


def link_id(value: Optional[Any]) -> Optional[Any]:
    if value is None:
        return None
    if isinstance(value, Link):
        return value.ref.id
    return value.id


def required_link(
    value: Union["Link[TDocument]", TDocument], *, field_name: str
) -> TDocument:
    if isinstance(value, Link):
        raise UnexpectedDomainException(
            f"Link field '{field_name}' was not fetched"
        )
    return value


def resolved_link(
    value: Optional[Union["Link[TDocument]", TDocument]], *, field_name: str
) -> Optional[TDocument]:
    if value is None:
        return None
    return required_link(value, field_name=field_name)


def resolved_links(
    values: Sequence[Union["Link[TDocument]", TDocument]], *, field_name: str
) -> List[TDocument]:
    return [
        required_link(value, field_name=field_name)
        for value in values
    ]


async def find_one_with_links(
    document_cls: Type[TDocument],
    query_filter: Dict[str, Any],
    session: Any = None,
    nesting_depth: Optional[int] = None,
) -> Optional[TDocument]:
    """Beanie's `fetch_links=True` rewrites a query into an aggregation pipeline that
    resolves Link fields *before* the $match stage runs, so filtering on a Link's
    nested id (e.g. "network.$id") never matches once fetch_links is also requested.
    Work around it in two steps: locate the id on the raw (unresolved) document first,
    then re-fetch that single id with fetch_links=True.
    """
    doc = await document_cls.find_one(query_filter, session=session)
    if doc is None:
        return None
    return await document_cls.get(
        doc.id,
        fetch_links=True,
        nesting_depth=nesting_depth,
        session=session,
    )
