import asyncio

import pytest
from app.tests.test_database import user_repo, message_repo

@pytest.mark.asyncio
async def test_create_user(user_repo):
    """Test creating a user"""
    user = await user_repo.create_user(tg_id=12345)
    assert user is not None
    assert user.tg_id == 12345

@pytest.mark.asyncio
async def test_get_user_by_tg_id(user_repo):
    """Test retrieving a user by Telegram ID"""
    await user_repo.create_user(tg_id=12345)
    user = await user_repo.get_by_tg_id(12345)
    assert user is not None
    assert user.tg_id == 12345

@pytest.mark.asyncio
async def test_get_all_users(user_repo):
    """Test fetching all users"""
    await user_repo.create_user(tg_id=111)
    await user_repo.create_user(tg_id=222)
    users = await user_repo.get_all()
    assert len(users) == 2

@pytest.mark.asyncio
async def test_update_user(user_repo):
    """Test updating a user's thread_id"""
    user = await user_repo.create_user(tg_id=12345)
    updated_user = await user_repo.update(user.id, thread_id="new_thread_123")
    assert updated_user.thread_id == "new_thread_123"

@pytest.mark.asyncio
async def test_delete_user(user_repo):
    """Test deleting a user"""
    user = await user_repo.create_user(tg_id=999)
    deleted = await user_repo.delete(user.id)
    assert deleted is True
    assert await user_repo.get_by_id(user.id) is None

@pytest.mark.asyncio
async def test_save_user_message(message_repo, user_repo):
    """Test saving a user's message"""
    user = await user_repo.create_user(tg_id=12345)
    message = await message_repo.save_user_message(tg_id=user.tg_id, message_text="Hello World!")
    assert message.text == "Hello World!"


@pytest.mark.asyncio
async def test_get_last_messages(message_repo, user_repo):
    """Test fetching the last messages"""
    user = await user_repo.create_user(tg_id=12345)

    await message_repo.save_user_message(tg_id=user.tg_id, message_text="Message 1")
    await message_repo.save_user_message(tg_id=user.tg_id, message_text="Message 2")
    await message_repo.save_user_message(tg_id=user.tg_id, message_text="Message 3")

    messages = await message_repo.get_last_messages(tg_id=user.tg_id, limit=3)
    assert len(messages) == 3
    assert messages == ["Message 3", "Message 2", "Message 1"]


@pytest.mark.asyncio
async def test_get_all_messages(message_repo, user_repo):
    """Test fetching all messages with a limit"""
    user = await user_repo.create_user(tg_id=12345)

    await message_repo.save_user_message(tg_id=user.tg_id, message_text="Hello")
    await asyncio.sleep(0.01)
    await message_repo.save_user_message(tg_id=user.tg_id, message_text="How are you?")
    await asyncio.sleep(0.01)
    await message_repo.save_user_message(tg_id=user.tg_id, message_text="Goodbye")

    messages = await message_repo.get_all(limit=2)

    assert len(messages) == 2


@pytest.mark.asyncio
async def test_get_message_by_id(message_repo, user_repo):
    """Test retrieving a single message by ID"""
    user = await user_repo.create_user(tg_id=12345)

    message = await message_repo.save_user_message(tg_id=user.tg_id, message_text="Find me!")

    retrieved_message = await message_repo.get_by_id(message.id)

    assert retrieved_message is not None
    assert retrieved_message.text == "Find me!"
    assert retrieved_message.id == message.id


@pytest.mark.asyncio
async def test_delete_message(message_repo, user_repo):
    """Test deleting a message by ID"""
    user = await user_repo.create_user(tg_id=12345)

    message = await message_repo.save_user_message(tg_id=user.tg_id, message_text="Delete me!")

    retrieved_message = await message_repo.get_by_id(message.id)
    assert retrieved_message is not None

    deleted = await message_repo.delete(message.id)

    assert deleted is True

    retrieved_message = await message_repo.get_by_id(message.id)
    assert retrieved_message is None