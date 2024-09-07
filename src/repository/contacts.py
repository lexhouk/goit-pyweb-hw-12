from datetime import date

from fastapi import HTTPException, status
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import Contact
from src.schemas.contact import Request, Response, Responses


async def create(db: AsyncSession, body: Request) -> Response:
    contact = Contact(**body.model_dump(exclude_unset=True))

    db.add(contact)

    await db.commit()
    await db.refresh(contact)

    return contact


async def read(
    db: AsyncSession,
    first_name: str = None,
    last_name: str = None,
    email: str = None
) -> list[Response]:
    query = select(Contact)

    if first_name:
        query.where(Contact.first_name == first_name)

    if last_name:
        query.where(Contact.last_name == last_name)

    if email:
        query.where(Contact.email == email)

    result = await db.execute(query)

    if not (result := result.scalars().all()):
        raise HTTPException(status.HTTP_404_NOT_FOUND, 'Not found')

    return result


async def birthday(db: AsyncSession, days: int) -> Responses:
    query = select(Contact).where(Contact.birthday.isnot(None))
    result = await db.execute(query)

    if not (entities := result.scalars().all()):
        raise HTTPException(status.HTTP_404_NOT_FOUND, 'Not found')

    result = []
    TODAY = date.today()

    for entity in entities:
        real = entity.birthday.replace(year=TODAY.year)

        if real < TODAY:
            real = real.replace(year=TODAY.year + 1)

        if 0 <= (real - TODAY).days <= days:
            result.append(entity)

    return result


async def get(db: AsyncSession, contact_id: int) -> Response:
    query = select(Contact).filter_by(id=contact_id)
    result = await db.execute(query)

    if not (contact := result.scalar_one_or_none()):
        raise HTTPException(status.HTTP_404_NOT_FOUND, 'Not found')

    return contact


async def update(
    db: AsyncSession,
    body: Request,
    contact_id: int
) -> Response:
    if (contact := await get(db, contact_id)):
        for key, value in body.model_dump(exclude_unset=True).items():
            setattr(contact, key, value)

        await db.commit()
        await db.refresh(contact)

    return contact


async def delete(db: AsyncSession, contact_id: int) -> None:
    if (contact := await get(db, contact_id)):
        await db.delete(contact)
        await db.commit()
