"""Tests for Database Emulator"""

import pytest
from backend.emulators.database_emulator import InMemoryDatabase


@pytest.mark.asyncio
async def test_create_table():
    """Test CREATE TABLE"""
    db = InMemoryDatabase()
    
    await db.execute("CREATE TABLE users")
    
    table = db.get_table("users")
    assert table == []


@pytest.mark.asyncio
async def test_insert():
    """Test INSERT"""
    db = InMemoryDatabase()
    
    await db.execute("CREATE TABLE users")
    result = await db.execute(
        "INSERT INTO users (name, email) VALUES (?, ?)",
        ("John Doe", "john@example.com")
    )
    
    assert len(result) == 1
    assert result[0]["name"] == "John Doe"
    assert result[0]["email"] == "john@example.com"
    assert "id" in result[0]


@pytest.mark.asyncio
async def test_select():
    """Test SELECT"""
    db = InMemoryDatabase()
    
    await db.execute("CREATE TABLE users")
    await db.execute(
        "INSERT INTO users (name, email) VALUES (?, ?)",
        ("John Doe", "john@example.com")
    )
    
    results = await db.execute("SELECT * FROM users")
    
    assert len(results) == 1
    assert results[0]["name"] == "John Doe"


@pytest.mark.asyncio
async def test_select_with_where():
    """Test SELECT with WHERE clause"""
    db = InMemoryDatabase()
    
    await db.execute("CREATE TABLE users")
    await db.execute("INSERT INTO users (name) VALUES (?)", ("Alice",))
    await db.execute("INSERT INTO users (name) VALUES (?)", ("Bob",))
    
    results = await db.execute("SELECT * FROM users WHERE name = ?", ("Alice",))
    
    assert len(results) == 1
    assert results[0]["name"] == "Alice"


@pytest.mark.asyncio
async def test_update():
    """Test UPDATE"""
    db = InMemoryDatabase()
    
    await db.execute("CREATE TABLE users")
    await db.execute("INSERT INTO users (name) VALUES (?)", ("John",))
    
    await db.execute("UPDATE users SET name = ? WHERE name = ?", ("Jane", "John"))
    
    results = await db.execute("SELECT * FROM users")
    assert results[0]["name"] == "Jane"


@pytest.mark.asyncio
async def test_delete():
    """Test DELETE"""
    db = InMemoryDatabase()
    
    await db.execute("CREATE TABLE users")
    await db.execute("INSERT INTO users (name) VALUES (?)", ("John",))
    await db.execute("INSERT INTO users (name) VALUES (?)", ("Jane",))
    
    deleted = await db.execute("DELETE FROM users WHERE name = ?", ("John",))
    
    assert len(deleted) == 1
    
    remaining = await db.execute("SELECT * FROM users")
    assert len(remaining) == 1
    assert remaining[0]["name"] == "Jane"


@pytest.mark.asyncio
async def test_transactions():
    """Test transaction support"""
    db = InMemoryDatabase()
    
    await db.execute("CREATE TABLE users")
    await db.execute("INSERT INTO users (name) VALUES (?)", ("John",))
    
    db.begin_transaction()
    await db.execute("INSERT INTO users (name) VALUES (?)", ("Jane",))
    db.rollback()
    
    results = await db.execute("SELECT * FROM users")
    assert len(results) == 1
    assert results[0]["name"] == "John"


@pytest.mark.asyncio
async def test_health_check():
    """Test health check"""
    db = InMemoryDatabase()
    
    health = await db.health_check()
    assert health is True
