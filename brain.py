
import sqlite3
import json
from pathlib import Path
from datetime import datetime, timezone


# ============================================================
# LUMEN CORE
# VEIL SYSTEMS | VSTG OS
# ============================================================

CORE_NAME = "LUMEN"
CORE_VERSION = "1.0.0"

BASE_DIR = Path(__file__).resolve().parent
MEMORY_DIR = BASE_DIR / "memory"
DATABASE_PATH = MEMORY_DIR / "lumen_memory.db"


# ============================================================
# MEMORY SYSTEM
# ============================================================

class MemorySystem:

    def __init__(self, database_path=DATABASE_PATH):
        self.database_path = Path(database_path)
        self.database_path.parent.mkdir(parents=True, exist_ok=True)

        self.connection = sqlite3.connect(self.database_path)
        self.connection.row_factory = sqlite3.Row

        self.initialize_database()

    def initialize_database(self):

        with self.connection:
            self.connection.execute("""
                CREATE TABLE IF NOT EXISTS memories (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    category TEXT NOT NULL,
                    title TEXT NOT NULL,
                    content TEXT NOT NULL,
                    importance INTEGER DEFAULT 3,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    tags TEXT DEFAULT '[]'
                )
            """)

    def remember(
        self,
        title,
        content,
        category="general",
        importance=3,
        tags=None
    ):

        title = str(title).strip()
        content = str(content).strip()

        if not title or not content:
            raise ValueError("Memory title and content cannot be empty.")

        importance = max(1, min(5, int(importance)))

        tags = tags or []
        timestamp = datetime.now(timezone.utc).isoformat()

        with self.connection:
            cursor = self.connection.execute("""
                INSERT INTO memories (
                    category,
                    title,
                    content,
                    importance,
                    created_at,
                    updated_at,
                    tags
                )
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                category,
                title,
                content,
                importance,
                timestamp,
                timestamp,
                json.dumps(tags)
            ))

        return cursor.lastrowid

    def recall(self, query, limit=10):

        query = str(query).strip()

        if not query:
            return []

        limit = max(1, min(100, int(limit)))

        search = f"%{query}%"

        cursor = self.connection.execute("""
            SELECT *
            FROM memories
            WHERE title LIKE ?
               OR content LIKE ?
               OR category LIKE ?
               OR tags LIKE ?
            ORDER BY importance DESC, updated_at DESC
            LIMIT ?
        """, (
            search,
            search,
            search,
            search,
            limit
        ))

        results = []

        for row in cursor.fetchall():

            memory = dict(row)
            memory["tags"] = json.loads(memory["tags"])

            results.append(memory)

        return results

    def get_all(self, limit=100):

        cursor = self.connection.execute("""
            SELECT *
            FROM memories
            ORDER BY updated_at DESC
            LIMIT ?
        """, (limit,))

        results = []

        for row in cursor.fetchall():

            memory = dict(row)
            memory["tags"] = json.loads(memory["tags"])

            results.append(memory)

        return results

    def update(self, memory_id, content):

        timestamp = datetime.now(timezone.utc).isoformat()

        with self.connection:
            cursor = self.connection.execute("""
                UPDATE memories
                SET content = ?, updated_at = ?
                WHERE id = ?
            """, (content, timestamp, memory_id))

        return cursor.rowcount > 0

    def forget(self, memory_id):

        with self.connection:
            cursor = self.connection.execute("""
                DELETE FROM memories
                WHERE id = ?
            """, (memory_id,))

        return cursor.rowcount > 0

    def close(self):
        self.connection.close()


# ============================================================
# CONTEXT SYSTEM
# ============================================================

class ContextSystem:

    def __init__(self):
        self.context = {
            "current_project": None,
            "current_task": None,
            "last_command": None,
            "session_started": datetime.now(timezone.utc).isoformat()
        }

    def set(self, key, value):
        self.context[key] = value

    def get(self, key):
        return self.context.get(key)

    def clear(self):
        self.context = {
            "current_project": None,
            "current_task": None,
            "last_command": None,
            "session_started": datetime.now(timezone.utc).isoformat()
        }

    def snapshot(self):
        return dict(self.context)


# ============================================================
# COMMAND SYSTEM
# ============================================================

class CommandSystem:

    def __init__(self, memory, context):
        self.memory = memory
        self.context = context
        self.commands = {}

    def register(self, name, function, description=""):
        self.commands[name.lower()] = {
            "function": function,
            "description": description
        }

    def execute(self, command, *args):

        command = str(command).lower().strip()

        self.context.set("last_command", command)

        if command not in self.commands:
            return {
                "success": False,
                "message": f"Unknown command: {command}"
            }

        try:
            result = self.commands[command]["function"](*args)

            return {
                "success": True,
                "result": result
            }

        except Exception as error:
            return {
                "success": False,
                "message": str(error)
            }

    def available_commands(self):

        return {
            name: data["description"]
            for name, data in self.commands.items()
        }


# ============================================================
# LUMEN CORE
# ============================================================

class LumenCore:

    def __init__(self):

        print(f"[{CORE_NAME}] Initializing...")

        self.memory = MemorySystem()
        self.context = ContextSystem()

        self.commands = CommandSystem(
            self.memory,
            self.context
        )

        self.register_default_commands()

        print(f"[{CORE_NAME}] Core initialized.")
        print(f"[{CORE_NAME}] Memory database connected.")

    def register_default_commands(self):

        self.commands.register(
            "remember",
            self.memory.remember,
            "Store a new memory."
        )

        self.commands.register(
            "recall",
            self.memory.recall,
            "Search stored memories."
        )

        self.commands.register(
            "commands",
            self.commands.available_commands,
            "List available commands."
        )

    def status(self):

        return {
            "name": CORE_NAME,
            "version": CORE_VERSION,
            "memory_database": str(DATABASE_PATH),
            "memory_count": len(self.memory.get_all(100000)),
            "context": self.context.snapshot(),
            "commands": self.commands.available_commands()
        }

    def shutdown(self):

        self.memory.close()

        print(f"[{CORE_NAME}] Core shutdown complete.")


# ============================================================
# STANDALONE TEST INTERFACE
# ============================================================

def main():

    lumen = LumenCore()

    print("\n=== LUMEN CORE TEST INTERFACE ===")
    print("Commands: remember, recall, status, exit")

    try:

        while True:

            command = input("\nLUMEN > ").strip()

            if not command:
                continue

            if command.lower() == "exit":
                break

            elif command.lower() == "status":

                print(json.dumps(
                    lumen.status(),
                    indent=4
                ))

            elif command.lower() == "remember":

                title = input("Memory title: ")
                content = input("Memory content: ")
                category = input("Category: ") or "general"

                memory_id = lumen.memory.remember(
                    title,
                    content,
                    category
                )

                print(f"[LUMEN] Memory stored. ID: {memory_id}")

            elif command.lower() == "recall":

                query = input("Search memories: ")

                results = lumen.memory.recall(query)

                if not results:
                    print("[LUMEN] No matching memories found.")
                    continue

                for memory in results:

                    print(f"\nID: {memory['id']}")
                    print(f"Title: {memory['title']}")
                    print(f"Category: {memory['category']}")
                    print(f"Content: {memory['content']}")
                    print("-" * 50)

            else:

                print("[LUMEN] Unknown command.")

    finally:
        lumen.shutdown()


if __name__ == "__main__":
    main()
